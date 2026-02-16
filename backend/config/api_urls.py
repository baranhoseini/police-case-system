from rest_framework.routers import DefaultRouter
from cases.views import CaseViewSet
from evidence.views import EvidenceViewSet
from config.stats_api import StatsView


router = DefaultRouter()
router.register(r"cases", CaseViewSet, basename="cases")
router.register(r"evidence", EvidenceViewSet, basename="evidence")


urlpatterns = router.urls
