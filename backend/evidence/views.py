from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from cases.models import CaseNotification
from .models import Evidence
from .serializers import EvidenceSerializer


class EvidenceViewSet(viewsets.ModelViewSet):
    queryset = Evidence.objects.all().order_by("-id")
    serializer_class = EvidenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        case_id = self.request.query_params.get("case_id") or self.request.query_params.get("case")
        if case_id:
            qs = qs.filter(case_id=case_id)
        return qs

    def perform_create(self, serializer):
        evidence = serializer.save(created_by=self.request.user)

        # Notify detective board owner if exists
        try:
            board = evidence.case.detective_board
        except Exception:
            board = None

        if board and board.created_by_id:
            CaseNotification.objects.create(
                case=evidence.case,
                recipient=board.created_by,
                notif_type="EVIDENCE_ADDED",
                message=f"New evidence added to case #{evidence.case_id}: {evidence.title}",
                ref_model="Evidence",
                ref_id=evidence.id,
                created_at=timezone.now(),
            )
