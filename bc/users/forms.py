from disposable_email_domains import blocklist
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserCreationForm,
)
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from hcaptcha.fields import hCaptchaField

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


class UserForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(attrs={"autocomplete": "email"}),
    )

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email", "affiliation")
        widgets = {
            "first_name": forms.TextInput(
                attrs={"autocomplete": "given-name"}
            ),
            "last_name": forms.TextInput(
                attrs={"autocomplete": "family-name"}
            ),
            "affiliation": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user_part, domain_part = email.rsplit("@", 1)
        if domain_part in blocklist:
            raise forms.ValidationError(
                f"{domain_part} is a blocked email provider",
                code="bad_email_domain",
            )
        return email


class AccountDeleteForm(forms.Form):
    password = forms.CharField(
        label="Confirm your password to continue...",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Your password...",
                "autocomplete": "off",
                "autofocus": "on",
            },
        ),
    )

    def __init__(self, request=None, *args, **kwargs):
        """Set the request attribute for use by the clean method."""
        self.request = request
        super().__init__(*args, **kwargs)

    def clean_password(self) -> dict[str, str]:
        password = self.cleaned_data["password"]

        if password:
            user = authenticate(
                self.request, username=self.request.user, password=password
            )
            if user is None:
                raise ValidationError(
                    "Your password was invalid. Please try again."
                )

        return self.cleaned_data


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
    hcaptcha = hCaptchaField()


class EmailConfirmationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Your Email Address",
                "autocomplete": "email",
                "autofocus": "on",
            }
        ),
        required=True,
    )


class CustomPasswordResetForm(PasswordResetForm):
    """
    Tweaks the PasswordResetForm class to ensure we send a message
    even if we don't find an account with the recipient address
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs) -> None:
        """Override the usual save method to send a message if we don't find
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
