# backend/intake/urls.py
from rest_framework.routers import DefaultRouter
from .views import ComplaintViewSet

router = DefaultRouter()
router.register(r"complaints", ComplaintViewSet, basename="intake-complaint")

urlpatterns = router.urls
