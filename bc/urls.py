from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path(
        # Redirect admin login to our ratelimited version.
        "admin/login/",
        RedirectView.as_view(url="/sign-in/", permanent=False),
    ),
    path("admin/", admin.site.urls),
    path("", include("bc.users.urls")),
    path("", include("bc.web.urls")),
    path("", include("bc.core.urls")),
    path("", include("bc.channel.urls")),
    path("", include("bc.subscription.urls")),
    path("django-rq/", include("django_rq.urls")),
]

if settings.DEVELOPMENT:
    urlpatterns.append(
        path("__reload__/", include("django_browser_reload.urls")),
    )
    urlpatterns += static(  # type: ignore
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
