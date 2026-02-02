from rest_framework.views import exception_handler as drf_exception_handler

def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return response

    data = {
        "error": {
            "status_code": response.status_code,
            "detail": response.data,
        }
    }
    response.data = data
    return response
