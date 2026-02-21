from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/", include("accounts.urls")),
    path("api/rbac/", include("rbac.urls")),
    path("api/", include("config.api_urls")),
    path("api/suspects/", include("suspects.urls")),
    path("api/rewards/", include("rewards.urls")),
    path("payments/", include("payments.urls")),
]
