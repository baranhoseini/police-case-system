from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rbac.permissions import HasRole
from .models import Case, Complaint, CrimeSceneReport
from .serializers import (
    CaseSerializer,
    ComplaintCreateSerializer,
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

        return Response(
            {"detail": "Strike applied", "revision_count": case.complaint.revision_count},
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
