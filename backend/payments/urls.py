from django.urls import path
from .views import payment_callback, mock_gateway, mock_gateway_pay, mock_gateway_fail
from .api import CreatePaymentRequest, ApprovePaymentRequest, InitiatePayment, GetPaymentRequest

urlpatterns = [
    # HTML
    path("callback/", payment_callback, name="payment-callback"),
    path("mock-gateway/", mock_gateway),
    path("mock-gateway/pay/", mock_gateway_pay),
    path("mock-gateway/fail/", mock_gateway_fail),

    # API
    path("api/requests/", CreatePaymentRequest.as_view()),
    path("api/requests/<int:pk>/", GetPaymentRequest.as_view()),
    path("api/requests/<int:pk>/approve/", ApprovePaymentRequest.as_view()),
    path("api/requests/<int:pk>/initiate/", InitiatePayment.as_view()),
]