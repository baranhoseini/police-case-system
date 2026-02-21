from dataclasses import dataclass

@dataclass
class GatewayInitResult:
    authority: str
    redirect_url: str


class MockGateway:
    """
    Demo gateway:
    - initiate() returns a redirect to /payments/mock-gateway/?payment_id=...
    - "Pay" and "Fail" buttons redirect to your callback.
    """
    def initiate(self, payment_public_id: str, callback_url: str) -> GatewayInitResult:
        authority = "MOCK_AUTH"
        redirect_url = f"/payments/mock-gateway/?payment_id={payment_public_id}&callback={callback_url}"
        return GatewayInitResult(authority=authority, redirect_url=redirect_url)