from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from rbac.models import UserRole
from rbac.permissions import HasRole, user_has_role

from .models import (
    Case,
    Complaint,
    CrimeSceneReport,
    DetectiveBoard,
    DetectiveBoardItem,
    DetectiveBoardLink,
    SolveRequest,
    Interrogation,
    CaptainDecision,
    Trial,
    CaseNotification,
    CaseComplainant,
)
from .serializers import (
    CaseSerializer,
    CaseComplainantSerializer,
    ComplaintCreateSerializer,
    ComplaintResubmitSerializer,
    CrimeSceneCreateSerializer,
    CaseFromCrimeSceneSerializer,
    CaseFromComplaintSerializer,
    DetectiveBoardSerializer,
    DetectiveBoardItemSerializer,
    DetectiveBoardLinkSerializer,
    SolveSubmitSerializer,
    SolveReviewSerializer,
    SolveRequestSerializer,
    InterrogationScoreSerializer,
    InterrogationSerializer,
    CaptainDecisionCreateSerializer,
    ChiefApprovalSerializer,
    CaptainDecisionSerializer,
    TrialVerdictSerializer,
    TrialSerializer,
    CaseNotificationSerializer,
)


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all().order_by("-id")
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        case = serializer.save(created_by=self.request.user, status="OPEN")
        CaseComplainant.objects.get_or_create(
            case=case,
            user=self.request.user,
            defaults={"status": CaseComplainant.STATUS_APPROVED},
        )
        CaseNotification.objects.create(case=case, recipient=self.request.user, message="Case created")

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

        CaseNotification.objects.create(case=case, recipient=request.user, message="Complaint submitted")

        return Response(
            {
                "case": CaseSerializer(case, context={"request": request}).data,
                "complaint_id": complaint.id,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="from-crime-scene")
    def from_crime_scene(self, request):
        serializer = CaseFromCrimeSceneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if not any(
            user_has_role(request.user, r)
            for r in ["Officer", "Patrol", "Detective", "Sergeant", "Supervisor", "Captain", "Chief", "Admin"]
        ):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        is_chief = user_has_role(request.user, "Chief") or user_has_role(request.user, "Admin") or getattr(request.user, "is_superuser", False)

        with transaction.atomic():
            case = Case.objects.create(
                title=data["title"],
                description=data.get("description", ""),
                crime_level=data["crime_level"],
                created_by=request.user,
                status="OPEN" if is_chief else "UNDER_REVIEW",
            )

            CrimeSceneReport.objects.create(
                case=case,
                reporter=request.user,
                report=data["report"],
                witnessed_phone=data.get("witnessed_phone", ""),
                witnessed_national_id=data.get("witnessed_national_id", ""),
                is_approved=True if is_chief else False,
                approved_by=request.user if is_chief else None,
                approved_at=timezone.now() if is_chief else None,
            )

            CaseComplainant.objects.get_or_create(
                case=case,
                user=request.user,
                defaults={"status": CaseComplainant.STATUS_APPROVED},
            )

            CaseNotification.objects.create(
                case=case,
                recipient=request.user,
                message="Crime scene report submitted",
            )

        return Response(CaseSerializer(case, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="complainants")
    def complainants(self, request, pk=None):
        case = self.get_object()

        if request.method.lower() == "get":
            qs = case.complainant_links.select_related("user", "reviewed_by").all()
            return Response(CaseComplainantSerializer(qs, many=True).data)

        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        allowed = (
            case.created_by_id == request.user.id
            or user_has_role(request.user, "Cadet")
            or user_has_role(request.user, "Admin")
            or case.complainant_links.filter(user=request.user, status=CaseComplainant.STATUS_APPROVED).exists()
        )
        if not allowed:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        link, created = CaseComplainant.objects.get_or_create(case=case, user_id=user_id)
        if not created:
            return Response({"detail": "Already exists"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CaseComplainantSerializer(link).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post"],
        url_path="complainants/(?P<link_id>[^/.]+)/review",
        permission_classes=[HasRole.with_roles("Cadet", "Admin")],
    )
    def review_complainant(self, request, pk=None, link_id=None):
        case = self.get_object()
        try:
            link = case.complainant_links.get(id=link_id)
        except CaseComplainant.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        action_value = request.data.get("action")
        message = request.data.get("message", "")

        if action_value not in ["approve", "reject"]:
            return Response({"detail": "action must be approve or reject"}, status=status.HTTP_400_BAD_REQUEST)

        link.status = CaseComplainant.STATUS_APPROVED if action_value == "approve" else CaseComplainant.STATUS_REJECTED
        link.cadet_message = message
        link.reviewed_by = request.user
        link.reviewed_at = timezone.now()
        link.save(update_fields=["status", "cadet_message", "reviewed_by", "reviewed_at"])
        return Response(CaseComplainantSerializer(link).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def create_complaint(self, request, pk=None):
        case = self.get_object()
        if hasattr(case, "complaint"):
            return Response({"detail": "Complaint already exists"}, status=status.HTTP_400_BAD_REQUEST)

        ser = ComplaintCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        complaint = Complaint.objects.create(
            case=case,
            complainant=request.user,
            details=ser.validated_data["details"],
        )

        CaseNotification.objects.create(case=case, recipient=request.user, message="Complaint created")

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

        CaseNotification.objects.create(case=case, recipient=request.user, message="Complaint resubmitted")

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
            return Response({"detail": "Crime scene report already exists"}, status=status.HTTP_400_BAD_REQUEST)

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

        CaseNotification.objects.create(case=case, recipient=request.user, message="Crime scene report created")

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

        CaseNotification.objects.create(case=case, recipient=request.user, message="Crime scene approved")

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

    @action(
        detail=True,
        methods=["post"],
        url_path="solve/submit",
        permission_classes=[HasRole.with_roles("Detective", "Admin")],
    )
    def solve_submit(self, request, pk=None):
        case = self.get_object()
        if case.status in ["CLOSED", "INVALIDATED"]:
            return Response({"detail": "Case is not active."}, status=status.HTTP_400_BAD_REQUEST)

        if SolveRequest.objects.filter(case=case, status="SUBMITTED").exists():
            return Response({"detail": "There is already a pending solve request."}, status=status.HTTP_400_BAD_REQUEST)

        ser = SolveSubmitSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        sr = SolveRequest.objects.create(
            case=case,
            suspect_ids=list(dict.fromkeys(ser.validated_data["suspect_ids"])),
            note=ser.validated_data.get("note", ""),
            status="SUBMITTED",
            submitted_by=request.user,
        )
        return Response(SolveRequestSerializer(sr).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post"],
        url_path="solve/review",
        permission_classes=[HasRole.with_roles("Sergent", "Admin")],
    )
    def solve_review(self, request, pk=None):
        case = self.get_object()
        sr = SolveRequest.objects.filter(case=case, status="SUBMITTED").order_by("-id").first()
        if not sr:
            return Response({"detail": "No pending solve request."}, status=status.HTTP_404_NOT_FOUND)

        ser = SolveReviewSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        decision = ser.validated_data["decision"]
        sr.reviewed_by = request.user
        sr.reviewed_at = timezone.now()
        sr.review_comment = ser.validated_data.get("comment", "")

        if decision == "approve":
            sr.status = "APPROVED"
        else:
            sr.status = "REJECTED"

        sr.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_comment"])
        return Response(SolveRequestSerializer(sr).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path=r"interrogations/(?P<suspect_id>\d+)/detective_score",
        permission_classes=[HasRole.with_roles("Detective", "Admin")],
    )
    def interrogation_detective_score(self, request, pk=None, suspect_id=None):
        case = self.get_object()
        if not SolveRequest.objects.filter(case=case, status="APPROVED").exists():
            return Response({"detail": "Solve request must be approved first."}, status=status.HTTP_400_BAD_REQUEST)

        ser = InterrogationScoreSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        obj, _ = Interrogation.objects.get_or_create(case=case, suspect_id=int(suspect_id))
        obj.detective_score = ser.validated_data["score"]
        obj.save(update_fields=["detective_score", "updated_at"])
        return Response(InterrogationSerializer(obj).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path=r"interrogations/(?P<suspect_id>\d+)/sergent_score",
        permission_classes=[HasRole.with_roles("Sergent", "Admin")],
    )
    def interrogation_sergent_score(self, request, pk=None, suspect_id=None):
        case = self.get_object()
        if not SolveRequest.objects.filter(case=case, status="APPROVED").exists():
            return Response({"detail": "Solve request must be approved first."}, status=status.HTTP_400_BAD_REQUEST)

        ser = InterrogationScoreSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        obj, _ = Interrogation.objects.get_or_create(case=case, suspect_id=int(suspect_id))
        obj.sergent_score = ser.validated_data["score"]
        obj.save(update_fields=["sergent_score", "updated_at"])
        return Response(InterrogationSerializer(obj).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="captain/decision",
        permission_classes=[HasRole.with_roles("Captain", "Admin")],
    )
    def captain_decision(self, request, pk=None):
        case = self.get_object()
        if case.status in ["CLOSED", "INVALIDATED"]:
            return Response({"detail": "Case is not active."}, status=status.HTTP_400_BAD_REQUEST)

        ser = CaptainDecisionCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        decision = ser.validated_data["decision"]
        comment = ser.validated_data.get("comment", "")

        obj, created = CaptainDecision.objects.get_or_create(
            case=case,
            defaults={
                "decision": decision,
                "comment": comment,
                "decided_by": request.user,
                "decided_at": timezone.now(),
            },
        )
        if not created:
            obj.decision = decision
            obj.comment = comment
            obj.decided_by = request.user
            obj.decided_at = timezone.now()
            obj.chief_approved = None
            obj.chief_by = None
            obj.chief_at = None
            obj.chief_comment = ""
            obj.save()

        return Response(CaptainDecisionSerializer(obj).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="chief/approve",
        permission_classes=[HasRole.with_roles("Chief", "Admin")],
    )
    def chief_approve(self, request, pk=None):
        case = self.get_object()
        if not hasattr(case, "captain_decision"):
            return Response({"detail": "No captain decision yet."}, status=status.HTTP_400_BAD_REQUEST)

        cd = case.captain_decision
        if cd.decision != "SEND_TO_TRIAL":
            return Response({"detail": "Chief approval is only needed for SEND_TO_TRIAL."}, status=status.HTTP_400_BAD_REQUEST)

        if not case.is_critical:
            return Response({"detail": "Chief approval only required for critical cases."}, status=status.HTTP_400_BAD_REQUEST)

        ser = ChiefApprovalSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        cd.chief_approved = bool(ser.validated_data["approve"])
        cd.chief_by = request.user
        cd.chief_at = timezone.now()
        cd.chief_comment = ser.validated_data.get("comment", "")
        cd.save(update_fields=["chief_approved", "chief_by", "chief_at", "chief_comment"])
        return Response(CaptainDecisionSerializer(cd).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="trial/verdict",
        permission_classes=[HasRole.with_roles("Judge", "Chief", "Admin")],
    )
    def trial_verdict(self, request, pk=None):
        case = self.get_object()

        if case.status in ["CLOSED", "INVALIDATED"]:
            return Response({"detail": "Case is not active."}, status=status.HTTP_400_BAD_REQUEST)

        if not hasattr(case, "captain_decision") or case.captain_decision.decision != "SEND_TO_TRIAL":
            return Response({"detail": "Case is not sent to trial by Captain."}, status=status.HTTP_400_BAD_REQUEST)

        if case.is_critical:
            if case.captain_decision.chief_approved is not True:
                return Response({"detail": "Chief approval is required for critical cases."}, status=status.HTTP_400_BAD_REQUEST)

        ser = TrialVerdictSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        verdict = ser.validated_data["verdict"]
        title = ser.validated_data.get("punishment_title", "")
        desc = ser.validated_data.get("punishment_description", "")

        trial, created = Trial.objects.get_or_create(
            case=case,
            defaults={
                "verdict": verdict,
                "punishment_title": title,
                "punishment_description": desc,
                "judged_by": request.user,
                "judged_at": timezone.now(),
            },
        )
        if not created:
            trial.verdict = verdict
            trial.punishment_title = title
            trial.punishment_description = desc
            trial.judged_by = request.user
            trial.judged_at = timezone.now()
            trial.save()

        case.status = "CLOSED"
        case.save(update_fields=["status"])

        return Response(TrialSerializer(trial).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["get"],
        url_path="dossier",
        permission_classes=[HasRole.with_roles("Detective", "Sergent", "Captain", "Supervisor", "Chief", "Admin")],
    )
    def dossier(self, request, pk=None):
        case = self.get_object()

        solve_latest = case.solve_requests.order_by("-id").first()
        interrogations = case.interrogations.order_by("suspect_id")
        captain_decision = getattr(case, "captain_decision", None)
        trial = getattr(case, "trial", None)

        payload = {
            "case": CaseSerializer(case, context={"request": request}).data,
            "complaint": getattr(case, "complaint", None).details if hasattr(case, "complaint") else None,
            "crime_scene": {
                "exists": hasattr(case, "crime_scene"),
                "is_approved": case.crime_scene.is_approved if hasattr(case, "crime_scene") else None,
                "report": case.crime_scene.report if hasattr(case, "crime_scene") else None,
            },
            "solve_request": SolveRequestSerializer(solve_latest).data if solve_latest else None,
            "interrogations": InterrogationSerializer(interrogations, many=True).data,
            "captain_decision": CaptainDecisionSerializer(captain_decision).data if captain_decision else None,
            "trial": TrialSerializer(trial).data if trial else None,
        }
        return Response(payload, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="notifications", permission_classes=[IsAuthenticated])
    def notifications(self, request):
        qs = CaseNotification.objects.filter(recipient=request.user).order_by("-created_at")
        return Response(CaseNotificationSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path=r"notifications/(?P<notif_id>\d+)/mark_read", permission_classes=[IsAuthenticated])
    def notification_mark_read(self, request, notif_id=None):
        try:
            n = CaseNotification.objects.get(id=int(notif_id), recipient=request.user)
        except CaseNotification.DoesNotExist:
            return Response({"detail": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)

        if n.read_at is None:
            n.read_at = timezone.now()
            n.save(update_fields=["read_at"])

        return Response(CaseNotificationSerializer(n).data, status=status.HTTP_200_OK)
