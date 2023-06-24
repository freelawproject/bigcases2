from datetime import timedelta
from email.utils import parseaddr

from django.conf import settings
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.utils.timezone import now
from django.views.decorators.debug import (
    sensitive_post_parameters,
    sensitive_variables,
)

from bc.core.utils.network import (
    ratelimiter_unsafe_10_per_m,
    ratelimiter_unsafe_2000_per_h,
)
from bc.core.utils.urls import get_redirect_or_login_url

from .forms import (
    CustomPasswordResetForm,
    EmailConfirmationForm,
    OptInConsentForm,
    RegisterForm,
)
from .models import User
from .utils.email import EmailType, emails


@sensitive_post_parameters("password1", "password2")
@sensitive_variables("cd")
@ratelimiter_unsafe_10_per_m
@ratelimiter_unsafe_2000_per_h
def register(request: HttpRequest) -> HttpResponse:
    """allow only an anonymous user to register"""
    if not request.user.is_anonymous:
        # The user is already logged in. Direct them to their settings page as
        # a logical fallback
        return HttpResponseRedirect(reverse("homepage"))

    redirect_to = get_redirect_or_login_url(request, "next")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        consent_form = OptInConsentForm(request.POST)

        if form.is_valid() and consent_form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create_user(
                cd["username"], cd["email"], cd["password1"]
            )

            if cd["first_name"]:
                user.first_name = cd["first_name"]
            if cd["last_name"]:
                user.last_name = cd["last_name"]

            signed_pk = user.get_signed_pk()
            email: EmailType = emails["confirm_your_new_account"]
            send_mail(
                email["subject"],
                email["body"] % (user.username, signed_pk),
                email["from_email"],
                [user.email],
            )
            email = emails["new_account_created"]
            send_mail(
                email["subject"] % user.username,
                email["body"]
                % (
                    user.get_full_name() or "Not provided",
                    user.email,
                ),
                email["from_email"],
                email["to"],
            )

            user.save(
                update_fields=[
                    "first_name",
                    "last_name",
                ]
            )
            query_string = urlencode(
                {"next": redirect_to, "email": user.email}
            )
            return redirect(f"{reverse('register_success')}?{query_string}")
    else:
        form = RegisterForm()
        consent_form = OptInConsentForm()

    return render(
        request,
        "register/register.html",
        {"form": form, "consent_form": consent_form},
    )


def register_success(request: HttpRequest) -> HttpResponse:
    """
    Let the user know they have been registered and allow them
    to continue where they left off.
    """
    redirect_to = get_redirect_or_login_url(request, "next")
    email = request.GET.get("email", "")
    default_from = parseaddr(settings.DEFAULT_FROM_EMAIL)[1]
    return render(
        request,
        "register/registration_complete.html",
        {
            "redirect_to": redirect_to,
            "email": email,
            "default_from": default_from,
            "private": True,
        },
    )


@sensitive_variables("activation_key")
def confirm_email(request, signed_pk):
    """Confirms email addresses for a user and sends an email to the admins.

    Checks if a hash in a confirmation link is valid, and if so sets the user's
    email address as valid.
    """
    try:
        pk = User.signer.unsign(signed_pk, max_age=timedelta(days=5))
        user = User.objects.get(pk=pk)
    except SignatureExpired:
        return render(
            request,
            "register/confirm.html",
            {"expired": True},
        )
    except (BadSignature, User.DoesNotExist):
        return render(
            request,
            "register/confirm.html",
            {"invalid": True},
        )

    if user.email_confirmed:
        return render(
            request,
            "register/confirm.html",
            {"already_confirmed": True},
        )

    user.email_confirmed = True
    user.save(update_fields=["email_confirmed"])

    return render(request, "register/confirm.html", {"success": True})


@sensitive_variables(
    "activation_key",
    "email",
    "cd",
    "confirmation_email",
)
@ratelimiter_unsafe_10_per_m
@ratelimiter_unsafe_2000_per_h
def request_email_confirmation(request: HttpRequest) -> HttpResponse:
    """Send an email confirmation email"""
    if request.method == "POST":
        form = EmailConfirmationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.filter(email__iexact=cd["email"]).first()
            if not user:
                # Normally, we'd throw an error here, but instead we pretend it
                # was a success. Meanwhile, we send an email saying that a
                # request was made, but we don't have an account with that
                # email address.
                email: EmailType = emails["no_account_found"]
                message = email["body"] % (
                    "email confirmation",
                    reverse("register"),
                )
                send_mail(
                    email["subject"],
                    message,
                    email["from_email"],
                    [cd["email"]],
                )
                return HttpResponseRedirect(
                    reverse("email_confirmation_request_success")
                )

            signed_pk = user.get_signed_pk()
            confirmation_email: EmailType = emails["confirm_existing_account"]
            send_mail(
                confirmation_email["subject"],
                confirmation_email["body"] % signed_pk,
                confirmation_email["from_email"],
                [user.email],
            )
            return HttpResponseRedirect(
                reverse("email_confirmation_request_success")
            )
    else:
        form = EmailConfirmationForm()
    return render(
        request,
        "register/request_email_confirmation.html",
        {"form": form},
    )


@method_decorator(ratelimiter_unsafe_10_per_m, name="post")
@method_decorator(ratelimiter_unsafe_2000_per_h, name="post")
class RateLimitedPasswordResetView(PasswordResetView):
    """
    Custom Password reset view with rate limiting
    """

    template_name = "register/password_reset_form.html"
    email_template_name = "register/password_reset_email.html"
    form_class = CustomPasswordResetForm
