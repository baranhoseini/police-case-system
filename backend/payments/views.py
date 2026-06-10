from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .gateways import get_gateway
from .models import PaymentRequest


def payment_callback(request):
    public_id = (request.GET.get("payment_id") or "").strip()
    status_param = (request.GET.get("status") or request.GET.get("Status") or "").strip()
    ref_id = (request.GET.get("ref_id") or request.GET.get("RefID") or "").strip()
    authority = (request.GET.get("authority") or request.GET.get("Authority") or "").strip()

    pr = None
    if public_id:
        pr = get_object_or_404(PaymentRequest, public_id=public_id)

    ok = False
    verify = None

    if pr and pr.gateway.lower() == "zarinpal":
        pr.authority = authority or pr.authority
        pr.save(update_fields=["authority"])

        status_ok = status_param.upper() == "OK"
        if status_ok and pr.authority:
            gw = get_gateway("zarinpal")
            verify = gw.verify(authority=pr.authority, amount_rials=pr.amount_rials)
            if verify.ok:
                ok = True
                pr.mark_paid(ref_id=verify.ref_id, authority=pr.authority)
                ref_id = verify.ref_id
            else:
                pr.status = PaymentRequest.STATUS_FAILED
                pr.save(update_fields=["status"])
        else:
            pr.status = PaymentRequest.STATUS_FAILED
            pr.save(update_fields=["status"])
    else:
        ok = status_param.lower() in {"ok", "success", "1", "true", "paid"}
        if pr:
            pr.authority = authority or pr.authority
            if ok:
                pr.mark_paid(ref_id=ref_id, authority=authority)
            else:
                pr.status = PaymentRequest.STATUS_FAILED
                pr.save(update_fields=["status", "authority"])

    frontend_return_url = (getattr(settings, "FRONTEND_PAYMENT_RETURN_URL", "") or "").strip()
    if frontend_return_url and pr:
        qs = urlencode(
            {
                "payment_id": pr.public_id,
                "ok": "1" if ok else "0",
                "status": status_param,
                "ref_id": ref_id,
                "authority": authority,
                "code": getattr(verify, "code", "") if verify else "",
                "message": getattr(verify, "message", "") if verify else "",
            }
        )
        return HttpResponseRedirect(
            f"{frontend_return_url}&{qs}" if "?" in frontend_return_url else f"{frontend_return_url}?{qs}"
        )

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
            "gateway": pr.gateway if pr else "",
            "verify": verify,
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
    return HttpResponseRedirect(f"{callback}&{qs}" if "?" in callback else f"{callback}?{qs}")


def mock_gateway_fail(request):
    payment_id = request.GET.get("payment_id", "")
    callback = request.GET.get("callback", "")
    qs = urlencode({"status": "fail", "authority": "MOCK_AUTH"})
    return HttpResponseRedirect(f"{callback}&{qs}" if "?" in callback else f"{callback}?{qs}")