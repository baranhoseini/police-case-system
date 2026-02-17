# backend/intake/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Complaint, ComplaintStatus
from .serializers import (
    ComplaintSerializer,
    ComplaintCreateSerializer,
    ResubmitSerializer,
    CadetReviewSerializer,
    OfficerReviewSerializer,
)


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all().select_related("created_by", "cadet", "officer")
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return super().get_queryset()
        return super().get_queryset().filter(created_by=user)

    def get_serializer_class(self):
        if self.action == "create":
            return ComplaintCreateSerializer
        if self.action == "resubmit":
            return ResubmitSerializer
        if self.action == "cadet_review":
            return CadetReviewSerializer
        if self.action == "officer_review":
            return OfficerReviewSerializer
        return ComplaintSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, status=ComplaintStatus.SUBMITTED)

    @action(detail=False, methods=["get"], url_path="cadet-inbox")
    def cadet_inbox(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"detail": "Forbidden."}, status=403)
        qs = Complaint.objects.filter(
            status__in=[ComplaintStatus.SUBMITTED, ComplaintStatus.OFFICER_DEFECT]
        ).select_related("created_by", "cadet", "officer")
        return Response(ComplaintSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="officer-inbox")
    def officer_inbox(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"detail": "Forbidden."}, status=403)
        qs = Complaint.objects.filter(
            status=ComplaintStatus.CADET_APPROVED
        ).select_related("created_by", "cadet", "officer")
        return Response(ComplaintSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"], url_path="cadet-review")
    def cadet_review(self, request, pk=None):
        complaint = self.get_object()
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        if complaint.status not in [ComplaintStatus.SUBMITTED, ComplaintStatus.OFFICER_DEFECT]:
            return Response({"detail": "Not in cadet-review state."}, status=400)

        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"detail": "Forbidden."}, status=403)

        complaint.cadet = request.user

        if ser.validated_data["action"] == "approve":
            complaint.status = ComplaintStatus.CADET_APPROVED
            complaint.cadet_error_message = ""
        else:
            complaint.status = ComplaintStatus.NEEDS_FIX
            complaint.cadet_error_message = ser.validated_data.get("error_message", "") or "Information is incomplete or incorrect."
            complaint.bad_submission_count += 1
            complaint.invalidate_if_needed()

        complaint.save()
        return Response(ComplaintSerializer(complaint).data)

    @action(detail=True, methods=["post"], url_path="resubmit")
    def resubmit(self, request, pk=None):
        complaint = self.get_object()

        if complaint.status == ComplaintStatus.INVALIDATED:
            return Response({"detail": "This complaint is invalidated and cannot be resubmitted."}, status=400)

        if complaint.status != ComplaintStatus.NEEDS_FIX:
            return Response({"detail": "Not in resubmission state."}, status=400)

        if complaint.created_by_id != request.user.id:
            return Response({"detail": "Forbidden."}, status=403)

        ser = self.get_serializer(instance=complaint, data=request.data)
        ser.is_valid(raise_exception=True)

        ser.save(status=ComplaintStatus.SUBMITTED, cadet_error_message="")
        return Response(ComplaintSerializer(complaint).data)

    @action(detail=True, methods=["post"], url_path="officer-review")
    def officer_review(self, request, pk=None):
        complaint = self.get_object()
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        if complaint.status != ComplaintStatus.CADET_APPROVED:
            return Response({"detail": "Not in officer-review state."}, status=400)

        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"detail": "Forbidden."}, status=403)

        complaint.officer = request.user

        if ser.validated_data["action"] == "defect":
            complaint.status = ComplaintStatus.OFFICER_DEFECT
            complaint.officer_error_message = ser.validated_data.get("error_message", "") or "Requires cadet re-check."
        else:
            complaint.status = ComplaintStatus.OFFICER_APPROVED
            complaint.officer_error_message = ""

        complaint.save()
        return Response(ComplaintSerializer(complaint).data)
