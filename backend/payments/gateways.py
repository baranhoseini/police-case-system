from dataclasses import dataclass
import json
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError
from django.conf import settings


@dataclass
class GatewayInitResult:
    authority: str
    redirect_url: str


@dataclass
class GatewayVerifyResult:
    ok: bool
    ref_id: str
    code: int | None = None
    message: str = ""


class MockGateway:
    def initiate(self, payment_public_id: str, callback_url: str, amount_rials: int, description: str) -> GatewayInitResult:
        authority = "MOCK_AUTH"
        redirect_url = f"/payments/mock-gateway/?payment_id={payment_public_id}&callback={callback_url}"
        return GatewayInitResult(authority=authority, redirect_url=redirect_url)

    def verify(self, authority: str, amount_rials: int) -> GatewayVerifyResult:
        return GatewayVerifyResult(ok=False, ref_id="", code=None, message="mock")


class ZarinpalGateway:
    def __init__(
        self,
        merchant_id: str,
        request_url: str,
        verify_url: str,
        startpay_url: str,
        currency: str = "IRR",
        timeout_seconds: int = 10,
    ):
        if not merchant_id:
            raise ValueError("ZARINPAL_MERCHANT_ID is required")
        self.merchant_id = merchant_id
        self.request_url = request_url
        self.verify_url = verify_url
        self.startpay_url = startpay_url
        self.currency = currency
        self.timeout_seconds = timeout_seconds

    def _post_json(self, url: str, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        req = urlrequest.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlrequest.urlopen(req, timeout=self.timeout_seconds) as resp:
                raw = resp.read().decode("utf-8")
        except HTTPError as e:
            raw = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"gateway_http_error: {e.code}: {raw}")
        except URLError as e:
            raise RuntimeError(f"gateway_connection_error: {e.reason}")
        try:
            return json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            raise RuntimeError(f"gateway_bad_json: {raw[:200]}")

    def initiate(self, payment_public_id: str, callback_url: str, amount_rials: int, description: str) -> GatewayInitResult:
        payload = {
            "merchant_id": self.merchant_id,
            "amount": int(amount_rials),
            "currency": self.currency,
            "description": description,
            "callback_url": callback_url,
            "metadata": {"order_id": payment_public_id},
        }
        res = self._post_json(self.request_url, payload)
        data = res.get("data") or {}
        code = data.get("code")
        authority = (data.get("authority") or "").strip()
        if code != 100 or not authority:
            err = res.get("errors") or {}
            msg = data.get("message") or (err.get("message") if isinstance(err, dict) else "") or "request_failed"
            raise RuntimeError(f"gateway_request_failed: code={code} message={msg}")
        return GatewayInitResult(authority=authority, redirect_url=f"{self.startpay_url}{authority}")

    def verify(self, authority: str, amount_rials: int) -> GatewayVerifyResult:
        payload = {
            "merchant_id": self.merchant_id,
            "amount": int(amount_rials),
            "authority": authority,
        }
        res = self._post_json(self.verify_url, payload)
        data = res.get("data") or {}
        code = data.get("code")
        ok = code in (100, 101)
        ref_id = str(data.get("ref_id") or "")
        msg = str(data.get("message") or "")
        return GatewayVerifyResult(ok=ok, ref_id=ref_id, code=code, message=msg)


def get_gateway(gateway_name: str):
    name = (gateway_name or "").lower()
    if name == "zarinpal":
        sandbox = getattr(settings, "ZARINPAL_SANDBOX", False)
        merchant_id = getattr(settings, "ZARINPAL_MERCHANT_ID", "")
        if sandbox:
            request_url = getattr(settings, "ZARINPAL_REQUEST_URL_SANDBOX", "https://sandbox.zarinpal.com/pg/v4/payment/request.json")
            verify_url = getattr(settings, "ZARINPAL_VERIFY_URL_SANDBOX", "https://sandbox.zarinpal.com/pg/v4/payment/verify.json")
            startpay_url = getattr(settings, "ZARINPAL_STARTPAY_URL_SANDBOX", "https://sandbox.zarinpal.com/pg/StartPay/")
        else:
            request_url = getattr(settings, "ZARINPAL_REQUEST_URL", "https://payment.zarinpal.com/pg/v4/payment/request.json")
            verify_url = getattr(settings, "ZARINPAL_VERIFY_URL", "https://payment.zarinpal.com/pg/v4/payment/verify.json")
            startpay_url = getattr(settings, "ZARINPAL_STARTPAY_URL", "https://payment.zarinpal.com/pg/StartPay/")
        currency = getattr(settings, "ZARINPAL_CURRENCY", "IRR")
        return ZarinpalGateway(
            merchant_id=merchant_id,
            request_url=request_url,
            verify_url=verify_url,
            startpay_url=startpay_url,
            currency=currency,
        )
    return MockGateway()