from django.shortcuts import render

def payment_callback(request):
    status = (request.GET.get("status") or request.GET.get("Status") or "").strip()
    ref_id = (request.GET.get("ref_id") or request.GET.get("RefID") or "").strip()
    authority = (request.GET.get("authority") or request.GET.get("Authority") or "").strip()

    ok = status.lower() in {"ok", "success", "1", "true"}

    return render(
        request,
        "payments/callback.html",
        {
            "ok": ok,
            "status": status,
            "ref_id": ref_id,
            "authority": authority,
            "params": dict(request.GET.items()),
        },
    )