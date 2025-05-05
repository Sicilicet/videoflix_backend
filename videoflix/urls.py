from django.views.generic.base import RedirectView
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=True), name="index"),
    path('admin/', admin.site.urls),
    path("django-rq/", include("django_rq.urls")),
    path("auth/", include("authentication_app.urls")),
    path("content/", include("content_app.urls")),
    path("watch/", include("watch_history_app.urls")),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + debug_toolbar_urls()
