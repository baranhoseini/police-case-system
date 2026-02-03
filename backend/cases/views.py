from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rbac.permissions import HasRole
from .models import Case, Complaint, CrimeSceneReport
from .serializers import CaseSerializer, ComplaintCreateSerializer, CrimeSceneCreateSerializer

class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all().order_by("-id")
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, status="OPEN")

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def create_complaint(self, request, pk=None):
        case = self.get_object()
        if hasattr(case, "complaint"):
            return Response({"detail":"Complaint already exists"}, status=400)
        ser = ComplaintCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        complaint = Complaint.objects.create(
            case=case,
            complainant=request.user,
            details=ser.validated_data["details"],
        )
        return Response({"detail":"Complaint created", "complaint_id": complaint.id}, status=201)

    @action(detail=True, methods=["post"], permission_classes=[HasRole.with_roles("Cadet","Officer","Admin")])
    def complaint_strike(self, request, pk=None):
        case = self.get_object()
        if not hasattr(case, "complaint"):
            return Response({"detail":"No complaint"}, status=404)
        reason = request.data.get("reason","")
        case.complaint.strike(reason=reason or "Invalid data")
        return Response({"detail":"Strike applied", "revision_count": case.complaint.revision_count})

    @action(detail=True, methods=["post"], permission_classes=[HasRole.with_roles("Officer","Supervisor","Chief","Admin")])
    def create_crime_scene(self, request, pk=None):
        case = self.get_object()
        if hasattr(case, "crime_scene"):
            return Response({"detail":"Crime scene report already exists"}, status=400)
        ser = CrimeSceneCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        report = CrimeSceneReport.objects.create(
            case=case,
            reporter=request.user,
            **ser.validated_data
        )
        return Response({"detail":"Crime scene report created", "crime_scene_id": report.id}, status=201)
