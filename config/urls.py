from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.common.health import health_check

urlpatterns = [
    # ── Ops ──────────────────────────────────────────────────────
    path('health/',   health_check,             name='health-check'),

    # ── Admin ────────────────────────────────────────────────────
    path('admin/',    admin.site.urls),

    # ── API v1 ───────────────────────────────────────────────────
    path('api/v1/auth/',          include('apps.accounts.urls')),
    path('api/v1/profile/',       include('apps.profiles.urls')),
    path('api/v1/companies/',     include('apps.companies.urls')),
    path('api/v1/jobs/',          include('apps.jobs.urls')),
    path('api/v1/applications/',  include('apps.applications.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),

    # ── OpenAPI / Swagger Docs ───────────────────────────────────
    path('api/schema/',  SpectacularAPIView.as_view(),                         name='schema'),
    path('api/docs/',    SpectacularSwaggerView.as_view(url_name='schema'),    name='swagger-ui'),
    path('api/redoc/',   SpectacularRedocView.as_view(url_name='schema'),      name='redoc'),
]

# Serve media files during development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)