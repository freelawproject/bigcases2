from disposable_email_domains import blocklist
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserCreationForm,
)
from django.contrib.auth.models import AbstractBaseUser
from django.core.mail import send_mail
from django.urls import reverse

from .utils.email import EmailType, emails


class ConfirmedEmailAuthenticationForm(AuthenticationForm):
    """
    Tweak the AuthenticationForm class to  ensure that only users with
    confirmed email addresses can log in.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def confirm_login_allowed(self, user: AbstractBaseUser) -> None:
        """Make sure the user is active and has a confirmed email address

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:  # type: ignore
            raise forms.ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

        if not user.email_confirmed:  # type: ignore
            raise forms.ValidationError(
                "Please validate your email address to log in."
            )


class RegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        _, domain_part = email.rsplit("@", 1)
        if domain_part in blocklist:
            raise forms.ValidationError(
                f"{domain_part} is a blocked email provider",
                code="bad_email_domain",
            )
        return email


class OptInConsentForm(forms.Form):
    consent = forms.BooleanField(
        error_messages={
            "required": "To create a new account, you must agree below.",
        },
        required=True,
    )


class EmailConfirmationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control input-lg",
                "placeholder": "Your Email Address",
                "autocomplete": "email",
                "autofocus": "on",
            }
        ),
        required=True,
    )


class CustomPasswordResetForm(PasswordResetForm):
    """A simple subclassing of a Django form in order to change class
    attributes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs) -> None:
        """Override the usual password form to send a message if we don't find
        any accounts
        """
        recipient_addr = self.cleaned_data["email"]
        users = self.get_users(recipient_addr)
        if not len(list(users)):
            email: EmailType = emails["no_account_found"]
            body = email["body"] % ("password reset", reverse("register"))
            send_mail(
                email["subject"], body, email["from_email"], [recipient_addr]
            )
        else:
            super().save(*args, **kwargs)
