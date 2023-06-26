from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.views.generic import TemplateView

from bc.core.utils.network import ratelimiter_unsafe_10_per_m

from .forms import ConfirmedEmailAuthenticationForm
from .views import (
    RateLimitedPasswordResetView,
    confirm_email,
    register,
    register_success,
    request_email_confirmation,
)

urlpatterns = [
    # Sign in page
    path(
        "sign-in/",
        ratelimiter_unsafe_10_per_m(
            auth_views.LoginView.as_view(
                template_name="register/login.html",
                authentication_form=ConfirmedEmailAuthenticationForm,
            )
        ),
        name="sign-in",
    ),
    path(
        "sign-out/",
        auth_views.LogoutView.as_view(template_name="register/logout.html"),
        name="logout",
    ),
    path(
        "register/",
        register,
        name="register",
    ),
    path(
        "register/success/",
        register_success,
        name="register_success",
    ),
    re_path(
        r"^email/confirm/(?P<signed_pk>[0-9]+/[A-Za-z0-9_=-]+/[A-Za-z0-9_=-]+)/$",
        confirm_email,
        name="email_confirm",
    ),
    path(
        "email-confirmation/request/",
        request_email_confirmation,
        name="email_confirmation_request",
    ),
    path(
        "email-confirmation/success/",
        TemplateView.as_view(
            template_name="register/request_email_confirmation_success.html"
        ),
        name="email_confirmation_request_success",
    ),
    path(
        "reset-password/",
        RateLimitedPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "reset-password/instructions-sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="register/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    re_path(
        r"^confirm-password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="register/password_reset_confirm.html",
        ),
        name="confirm_password",
    ),
    path(
        "reset-password/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="register/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
