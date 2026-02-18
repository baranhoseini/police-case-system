from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from cases.views import CaseViewSet
from evidence.views import EvidenceViewSet
from config.stats_api import StatsView  

router = DefaultRouter()
router.register(r"cases", CaseViewSet, basename="cases")
router.register(r"evidence", EvidenceViewSet, basename="evidence")

urlpatterns = [
    path("", include(router.urls)),
    path("stats/", StatsView.as_view(), name="stats"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("intake/", include("intake.urls")),
]
