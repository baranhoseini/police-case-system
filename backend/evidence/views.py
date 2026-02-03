from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rbac.permissions import HasRole
from .models import Evidence
from .serializers import EvidenceSerializer

class EvidenceViewSet(viewsets.ModelViewSet):
    queryset = Evidence.objects.all().order_by("-id")
    serializer_class = EvidenceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
