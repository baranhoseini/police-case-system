from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rbac.models import UserRole
from rbac.permissions import HasRole
from .models import (
    Case,
    Complaint,
    CrimeSceneReport,
    DetectiveBoard,
    DetectiveBoardItem,
    DetectiveBoardLink,
)
from .serializers import (
    CaseSerializer,
    ComplaintCreateSerializer,
    ComplaintResubmitSerializer,
    CrimeSceneCreateSerializer,
    CaseFromComplaintSerializer,
    DetectiveBoardSerializer,
    DetectiveBoardItemSerializer,
    DetectiveBoardLinkSerializer,
)


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all().order_by("-id")
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, status="OPEN")

    def _get_or_create_board(self, case, user):
        try:
            return case.detective_board
        except DetectiveBoard.DoesNotExist:
            return DetectiveBoard.objects.create(case=case, created_by=user)

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

        is_chief = UserRole.objects.filter(user=request.user, role__name="Chief").exists() or getattr(request.user, "is_superuser", False)
        if is_chief:
            report.is_approved = True
            report.approved_by = request.user
            report.approved_at = timezone.now()
            report.save(update_fields=["is_approved", "approved_by", "approved_at"])

            if case.status not in ["CLOSED", "INVALIDATED"]:
                case.status = "OPEN"
                case.save(update_fields=["status"])

        return Response(
            {"detail": "Crime scene report created", "crime_scene_id": report.id},
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[HasRole.with_roles("Supervisor", "Chief", "Admin")],
    )
    def crime_scene_approve(self, request, pk=None):
        case = self.get_object()
        if not hasattr(case, "crime_scene"):
            return Response({"detail": "No crime scene report"}, status=status.HTTP_404_NOT_FOUND)

        if case.status == "INVALIDATED":
            return Response({"detail": "Case is invalidated"}, status=status.HTTP_400_BAD_REQUEST)

        report = case.crime_scene
        if not report.is_approved:
            report.is_approved = True
            report.approved_by = request.user
            report.approved_at = timezone.now()
            report.save(update_fields=["is_approved", "approved_by", "approved_at"])

        if case.status != "CLOSED":
            case.status = "OPEN"
            case.save(update_fields=["status"])

        return Response(
            {
                "detail": "Crime scene approved",
                "crime_scene_id": report.id,
                "is_approved": report.is_approved,
                "case_status": case.status,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[HasRole.with_roles("Detective", "Sergent", "Captain", "Supervisor", "Chief", "Admin")],
    )
    def detective_board(self, request, pk=None):
        case = self.get_object()
        board = self._get_or_create_board(case, request.user)
        return Response(DetectiveBoardSerializer(board, context={"request": request}).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path=r"detective_board/items",
        permission_classes=[HasRole.with_roles("Detective", "Sergent", "Captain", "Supervisor", "Chief", "Admin")],
    )
    def detective_board_create_item(self, request, pk=None):
        case = self.get_object()
        board = self._get_or_create_board(case, request.user)

        ser = DetectiveBoardItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        item = ser.save(board=board, created_by=request.user)

        return Response(DetectiveBoardItemSerializer(item, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["patch"],
        url_path=r"detective_board/items/(?P<item_id>\d+)",
        permission_classes=[HasRole.with_roles("Detective", "Sergent", "Captain", "Supervisor", "Chief", "Admin")],
    )
    def detective_board_update_item(self, request, pk=None, item_id=None):
        case = self.get_object()
        board = self._get_or_create_board(case, request.user)

        try:
            item = DetectiveBoardItem.objects.get(id=item_id, board=board)
        except DetectiveBoardItem.DoesNotExist:
            return Response({"detail": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        ser = DetectiveBoardItemSerializer(item, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        item = ser.save()

        return Response(DetectiveBoardItemSerializer(item, context={"request": request}).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"detective_board/items/(?P<item_id>\d+)",
        permission_classes=[HasRole.with_roles("Detective", "Sergent", "Captain", "Supervisor", "Chief", "Admin")],
    )
    def detective_board_delete_item(self, request, pk=None, item_id=None):
        case = self.get_object()
        board = self._get_or_create_board(case, request.user)

        try:
            item = DetectiveBoardItem.objects.get(id=item_id, board=board)
        except DetectiveBoardItem.DoesNotExist:
            return Response({"detail": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        url_path=r"detective_board/links",
        permission_classes=[HasRole.with_roles("Detective", "Sergent", "Captain", "Supervisor", "Chief", "Admin")],
    )
    def detective_board_create_link(self, request, pk=None):
        case = self.get_object()
        board = self._get_or_create_board(case, request.user)

        ser = DetectiveBoardLinkSerializer(data=request.data, context={"request": request, "board": board})
        ser.is_valid(raise_exception=True)
        link = ser.save()

        return Response(
            {
                "id": link.id,
                "source": link.source_id,
                "target": link.target_id,
                "label": link.label,
                "meta": link.meta,
                "created_by": link.created_by_id,
                "created_at": link.created_at,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"detective_board/links/(?P<link_id>\d+)",
        permission_classes=[HasRole.with_roles("Detective", "Sergent", "Captain", "Supervisor", "Chief", "Admin")],
    )
    def detective_board_delete_link(self, request, pk=None, link_id=None):
        case = self.get_object()
        board = self._get_or_create_board(case, request.user)

        try:
            link = DetectiveBoardLink.objects.get(id=link_id, board=board)
        except DetectiveBoardLink.DoesNotExist:
            return Response({"detail": "Link not found"}, status=status.HTTP_404_NOT_FOUND)

        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
