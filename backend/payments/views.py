from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import PaymentRequest


def payment_callback(request):
    public_id = (request.GET.get("payment_id") or "").strip()
    status_param = (request.GET.get("status") or request.GET.get("Status") or "").strip()
    ref_id = (request.GET.get("ref_id") or request.GET.get("RefID") or "").strip()
    authority = (request.GET.get("authority") or request.GET.get("Authority") or "").strip()

    pr = None
    if public_id:
        pr = get_object_or_404(PaymentRequest, public_id=public_id)

    ok = status_param.lower() in {"ok", "success", "1", "true", "paid"}

    if pr:
        pr.authority = authority or pr.authority
        if ok:
            pr.mark_paid(ref_id=ref_id, authority=authority)
        else:
            pr.status = PaymentRequest.STATUS_FAILED
            pr.save(update_fields=["status", "authority"])

    return render(
        request,
        "payments/callback.html",
        {
            "ok": ok,
            "status": status_param,
            "ref_id": ref_id,
            "authority": authority,
            "params": dict(request.GET.items()),
            "payment": pr,
        },
    )


def mock_gateway(request):
    payment_id = request.GET.get("payment_id", "")
    callback = request.GET.get("callback", "")
    return render(
        request,
        "payments/mock_gateway.html",
        {
            "payment_id": payment_id,
            "callback": callback,
        },
    )


def mock_gateway_pay(request):
    payment_id = request.GET.get("payment_id", "")
    callback = request.GET.get("callback", "")
    qs = urlencode({"status": "ok", "ref_id": "MOCK_REF", "authority": "MOCK_AUTH"})
    # callback already contains ?payment_id=...
    return HttpResponseRedirect(f"{callback}&{qs}" if "?" in callback else f"{callback}?{qs}")


def mock_gateway_fail(request):
    payment_id = request.GET.get("payment_id", "")
    callback = request.GET.get("callback", "")
    qs = urlencode({"status": "fail", "authority": "MOCK_AUTH"})
    return HttpResponseRedirect(f"{callback}&{qs}" if "?" in callback else f"{callback}?{qs}")