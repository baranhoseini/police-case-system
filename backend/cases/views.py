from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rbac.permissions import HasRole
from .models import Case, Complaint, CrimeSceneReport
from .serializers import (
    CaseSerializer,
    ComplaintCreateSerializer,
    ComplaintResubmitSerializer,
    CrimeSceneCreateSerializer,
    CaseFromComplaintSerializer,
)


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all().order_by("-id")
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, status="OPEN")

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def from_complaint(self, request):
        ser = CaseFromComplaintSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        case = Case.objects.create(
            title=ser.validated_data["title"],
            description=ser.validated_data.get("description", ""),
            status="UNDER_REVIEW",
            created_by=request.user,
        )

        complaint = Complaint.objects.create(
            case=case,
            complainant=request.user,
            details=ser.validated_data["details"],
        )

        return Response(
            {
                "case": CaseSerializer(case, context={"request": request}).data,
                "complaint_id": complaint.id,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def create_complaint(self, request, pk=None):
        case = self.get_object()
        if hasattr(case, "complaint"):
            return Response(
                {"detail": "Complaint already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ser = ComplaintCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        complaint = Complaint.objects.create(
            case=case,
            complainant=request.user,
            details=ser.validated_data["details"],
        )

        return Response(
            {"detail": "Complaint created", "complaint_id": complaint.id},
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[HasRole.with_roles("Cadet", "Officer", "Admin")],
    )
    def complaint_strike(self, request, pk=None):
        case = self.get_object()
        if not hasattr(case, "complaint"):
            return Response({"detail": "No complaint"}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get("reason", "") or "Invalid data"
        case.complaint.strike(reason=reason)

        case.refresh_from_db()
        if case.status != "INVALIDATED":
            case.status = "DRAFT"
            case.save(update_fields=["status"])

        return Response(
            {
                "detail": "Strike applied",
                "revision_count": case.complaint.revision_count,
                "case_status": case.status,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def complaint_resubmit(self, request, pk=None):
        case = self.get_object()
        if not hasattr(case, "complaint"):
            return Response({"detail": "No complaint"}, status=status.HTTP_404_NOT_FOUND)

        if request.user != case.complaint.complainant and not request.user.is_staff:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        if case.status == "INVALIDATED":
            return Response({"detail": "Case is invalidated"}, status=status.HTTP_400_BAD_REQUEST)

        ser = ComplaintResubmitSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        complaint = case.complaint
        complaint.details = ser.validated_data["details"]
        complaint.rejection_reason = None
        complaint.save(update_fields=["details", "rejection_reason"])

        case.status = "UNDER_REVIEW"
        case.save(update_fields=["status"])

        return Response(
            {
                "detail": "Complaint resubmitted",
                "revision_count": complaint.revision_count,
                "case_status": case.status,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[HasRole.with_roles("Officer", "Supervisor", "Chief", "Admin")],
    )
    def create_crime_scene(self, request, pk=None):
        case = self.get_object()
        if hasattr(case, "crime_scene"):
            return Response(
                {"detail": "Crime scene report already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ser = CrimeSceneCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        report = CrimeSceneReport.objects.create(
            case=case,
            reporter=request.user,
            **ser.validated_data,
        )

        return Response(
            {"detail": "Crime scene report created", "crime_scene_id": report.id},
            status=status.HTTP_201_CREATED,
        )
