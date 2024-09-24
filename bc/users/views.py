from datetime import timedelta
from email.utils import parseaddr

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.utils.timezone import now
from django.views.decorators.cache import never_cache
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
    AccountDeleteForm,
    CustomPasswordResetForm,
    EmailConfirmationForm,
    OptInConsentForm,
    RegisterForm,
    UserForm,
)
from .models import User
from .services import convert_to_stub_account
from .types import AuthenticatedHttpRequest
from .utils.email import EmailType, emails, message_dict


@sensitive_post_parameters("password1", "password2")
@sensitive_variables("cd", "signed_pk", "email")
@ratelimiter_unsafe_10_per_m
@ratelimiter_unsafe_2000_per_h
@never_cache
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


@never_cache
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


@sensitive_variables("signed_pk")
@never_cache
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
    "signed_pk",
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


@sensitive_variables(
    # Contains user info
    "user_cd",
    # Contains activation key
    "signed_pk",
    "email",
)
@login_required
@never_cache
def profile_settings(request: AuthenticatedHttpRequest) -> HttpResponse:
    old_email = request.user.email
    user = request.user
    form = UserForm(request.POST or None, instance=user)
    if form.is_valid():
        user_cd = form.cleaned_data
        new_email = user_cd["email"]
        changed_email = old_email != new_email
        if changed_email:
            # Email was changed.
            signed_pk = user.get_signed_pk()

            # Send an email to the new and old addresses. New for verification;
            # old for notification of the change.
            email: EmailType = emails["email_changed_successfully"]
            send_mail(
                email["subject"],
                email["body"] % (user.username, signed_pk),
                email["from_email"],
                [new_email],
            )
            email = emails["notify_old_address"]
            send_mail(
                email["subject"],
                email["body"] % (user.username, old_email, new_email),
                email["from_email"],
                [old_email],
            )
            msg = message_dict["email_changed_successfully"]
            messages.add_message(request, msg["level"], msg["message"])
            logout(request)
        else:
            # if the email wasn't changed, simply inform of success.
            msg = message_dict["settings_changed_successfully"]
            messages.add_message(request, msg["level"], msg["message"])

        form.save()
        return HttpResponseRedirect(reverse("profile_settings"))

    return render(
        request,
        "profile/settings.html",
        {"form": form},
    )


@sensitive_post_parameters("old_password", "new_password1", "new_password2")
@login_required
@never_cache
def password_change(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            msg = message_dict["pwd_changed_successfully"]
            messages.add_message(request, msg["level"], msg["message"])
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect(reverse("password_change"))
    else:
        form = PasswordChangeForm(user=request.user)
    return render(
        request,
        "profile/password_form.html",
        {"form": form},
    )


@login_required
@ratelimiter_unsafe_10_per_m
@ratelimiter_unsafe_2000_per_h
@never_cache
def take_out(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "POST":
        email: EmailType = emails["take_out_requested"]
        send_mail(
            email["subject"],
            email["body"] % (request.user, request.user.email),
            email["from_email"],
            email["to"],
        )

        return HttpResponseRedirect(reverse("take_out_done"))

    return render(
        request,
        "profile/take_out.html",
    )


def take_out_done(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "profile/take_out_done.html",
    )


@sensitive_post_parameters("password")
@login_required
@ratelimiter_unsafe_10_per_m
@ratelimiter_unsafe_2000_per_h
@never_cache
def delete_account(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "POST":
        delete_form = AccountDeleteForm(request, request.POST)
        if delete_form.is_valid():
            email: EmailType = emails["account_deleted"]
            send_mail(
                email["subject"],
                email["body"] % request.user,
                email["from_email"],
                email["to"],
            )
            convert_to_stub_account(request.user)
            update_session_auth_hash(request, request.user)
            logout(request)
            return HttpResponseRedirect(reverse("delete_profile_done"))
    else:
        delete_form = AccountDeleteForm(request=request)
    return render(
        request,
        "profile/delete.html",
        {
            "form": delete_form,
        },
    )


def delete_profile_done(request: HttpRequest) -> HttpResponse:
    return render(request, "profile/deleted.html")
