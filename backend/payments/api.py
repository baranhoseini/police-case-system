from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import HasRole
from .gateways import MockGateway
from .models import PaymentRequest
from .serializers import PaymentRequestCreateSerializer, PaymentRequestPublicSerializer

User = get_user_model()

IsSergent = HasRole.with_roles("Sergent", "Admin")
# If your role is spelled "Sergeant" in DB, change the string above.


class CreatePaymentRequest(APIView):
    """
    Sergent sets amount and creates the payment record.
    """
    permission_classes = [IsSergent]

    def post(self, request):
        ser = PaymentRequestCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        payer = get_object_or_404(User, id=data["payer_user_id"])
        purpose = data["purpose"]
        level = data["crime_level"]

        # Enforce doc rules:
        if purpose == PaymentRequest.PURPOSE_BAIL and level not in (2, 3):
            return Response({"detail": "Bail is allowed only for crime level 2 or 3."}, status=400)

        if purpose == PaymentRequest.PURPOSE_FINE and level != 3:
            return Response({"detail": "Fine is allowed only for crime level 3."}, status=400)

        pr = PaymentRequest.objects.create(
            payer=payer,
            purpose=purpose,
            amount_rials=data["amount_rials"],
            crime_level=level,
            case_id=data.get("case_id"),
            suspect_id=data.get("suspect_id"),
            created_by=request.user,
            status=PaymentRequest.STATUS_DRAFT,
            gateway="mock",
        )

        return Response(PaymentRequestPublicSerializer(pr).data, status=201)


class ApprovePaymentRequest(APIView):
    """
    Sergent approval step (required for FINE, optional for BAIL).
    """
    permission_classes = [IsSergent]

    def post(self, request, pk: int):
        pr = get_object_or_404(PaymentRequest, pk=pk)

        if pr.status not in (PaymentRequest.STATUS_DRAFT, PaymentRequest.STATUS_FAILED):
            return Response({"detail": f"Cannot approve in status={pr.status}."}, status=409)

        pr.status = PaymentRequest.STATUS_APPROVED
        pr.approved_by = request.user
        pr.approved_at = __import__("django.utils.timezone").utils.timezone.now()
        pr.save(update_fields=["status", "approved_by", "approved_at"])

        return Response(PaymentRequestPublicSerializer(pr).data, status=200)


class InitiatePayment(APIView):
    """
    Payer initiates payment and gets redirect_url to gateway.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        pr = get_object_or_404(PaymentRequest, pk=pk)

        if pr.payer_id != request.user.id:
            return Response({"detail": "You are not the payer for this payment request."}, status=403)

        # For fines, sergent approval is mandatory
        if pr.purpose == PaymentRequest.PURPOSE_FINE and pr.status != PaymentRequest.STATUS_APPROVED:
            return Response({"detail": "Fine payment requires sergent approval."}, status=409)

        # Optional: if you want bail also require approval, uncomment:
        # if pr.purpose == PaymentRequest.PURPOSE_BAIL and pr.status != PaymentRequest.STATUS_APPROVED:
        #     return Response({"detail": "Bail payment requires sergent approval."}, status=409)

        if pr.status == PaymentRequest.STATUS_PAID:
            return Response({"detail": "Already paid."}, status=409)

        callback_url = request.build_absolute_uri(
            reverse("payment-callback") + f"?payment_id={pr.public_id}"
        )

        gw = MockGateway()
        init = gw.initiate(payment_public_id=pr.public_id, callback_url=callback_url)

        pr.authority = init.authority
        pr.status = PaymentRequest.STATUS_INITIATED
        pr.save(update_fields=["authority", "status"])

        return Response(
            {"payment_id": pr.public_id, "redirect_url": init.redirect_url},
            status=200,
        )


class GetPaymentRequest(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        pr = get_object_or_404(PaymentRequest, pk=pk)

        # payer can view their own; sergent/admin can view all
        if pr.payer_id != request.user.id and not HasRole.with_roles("Sergent", "Admin")().has_permission(request, self):
            return Response({"detail": "Forbidden."}, status=403)

        return Response(PaymentRequestPublicSerializer(pr).data, status=200)