from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import HasRole
from .gateways import get_gateway
from .models import PaymentRequest
from .serializers import PaymentRequestCreateSerializer, PaymentRequestPublicSerializer

User = get_user_model()

IsSergent = HasRole.with_roles("Sergent", "Admin")


class CreatePaymentRequest(APIView):
    permission_classes = [IsSergent]

    def post(self, request):
        ser = PaymentRequestCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        payer = get_object_or_404(User, id=data["payer_user_id"])
        purpose = data["purpose"]
        level = data["crime_level"]

        if purpose == PaymentRequest.PURPOSE_BAIL and level not in (2, 3):
            return Response({"detail": "Bail is allowed only for crime level 2 or 3."}, status=400)

        if purpose == PaymentRequest.PURPOSE_FINE and level != 3:
            return Response({"detail": "Fine is allowed only for crime level 3."}, status=400)

        default_gateway = getattr(settings, "PAYMENT_GATEWAY", "mock")

        pr = PaymentRequest.objects.create(
            payer=payer,
            purpose=purpose,
            amount_rials=data["amount_rials"],
            crime_level=level,
            case_id=data.get("case_id"),
            suspect_id=data.get("suspect_id"),
            created_by=request.user,
            status=PaymentRequest.STATUS_DRAFT,
            gateway=default_gateway,
        )

        return Response(PaymentRequestPublicSerializer(pr).data, status=201)


class ApprovePaymentRequest(APIView):
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
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        pr = get_object_or_404(PaymentRequest, pk=pk)

        if pr.payer_id != request.user.id:
            return Response({"detail": "You are not the payer for this payment request."}, status=403)

        if pr.purpose == PaymentRequest.PURPOSE_FINE and pr.status != PaymentRequest.STATUS_APPROVED:
            return Response({"detail": "Fine payment requires sergent approval."}, status=409)

        if pr.status == PaymentRequest.STATUS_PAID:
            return Response({"detail": "Already paid."}, status=409)

        callback_url = request.build_absolute_uri(
            reverse("payment-callback") + f"?payment_id={pr.public_id}"
        )

        parts = ["Police Case System", pr.purpose]
        if pr.case_id:
            parts.append(f"case:{pr.case_id}")
        if pr.suspect_id:
            parts.append(f"suspect:{pr.suspect_id}")
        description = " | ".join(parts)

        gw = get_gateway(pr.gateway)

        try:
            init = gw.initiate(
                payment_public_id=pr.public_id,
                callback_url=callback_url,
                amount_rials=pr.amount_rials,
                description=description,
            )
        except Exception as e:
            pr.status = PaymentRequest.STATUS_FAILED
            pr.save(update_fields=["status"])
            return Response({"detail": str(e)}, status=502)

        pr.authority = init.authority
        pr.status = PaymentRequest.STATUS_INITIATED
        pr.save(update_fields=["authority", "status"])

        redirect_url = init.redirect_url
        if isinstance(redirect_url, str) and redirect_url.startswith("/"):
            redirect_url = request.build_absolute_uri(redirect_url)

        return Response(
            {"payment_id": pr.public_id, "redirect_url": redirect_url},
            status=200,
        )


class GetPaymentRequest(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        pr = get_object_or_404(PaymentRequest, pk=pk)

        if pr.payer_id != request.user.id and not HasRole.with_roles("Sergent", "Admin")().has_permission(request, self):
            return Response({"detail": "Forbidden."}, status=403)

        return Response(PaymentRequestPublicSerializer(pr).data, status=200)