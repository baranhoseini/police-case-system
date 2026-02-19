from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
)


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    # Unhandled exception -> consistent JSON 500 (instead of HTML)
    if response is None:
        return Response(
            {
                "error": {
                    "status_code": 500,
                    "code": "server_error",
                    "message": "Internal server error",
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    code = "error"
    message = "Request failed"

    if isinstance(exc, ValidationError):
        code = "validation_error"
        message = "Validation failed"
    elif isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        code = "auth_error"
        message = "Authentication failed"
    elif isinstance(exc, PermissionDenied):
        code = "forbidden"
        message = "Permission denied"

    response.data = {
        "error": {
            "status_code": response.status_code,
            "code": code,
            "message": message,
            "details": response.data,
        }
    }
    return response
