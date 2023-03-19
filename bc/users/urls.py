from django.contrib.auth import views as auth_views
from django.urls import path

from bc.core.utils.network import ratelimiter_unsafe_10_per_m

urlpatterns = [
    # Sign in page
    path(
        "sign-in/",
        ratelimiter_unsafe_10_per_m(
            auth_views.LoginView.as_view(template_name="register/login.html")
        ),
        name="sign-in",
    )
]
