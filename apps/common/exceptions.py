from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from .error_codes import ErrorCode


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        code_map = {
            400: ErrorCode.VALIDATION_ERROR,
            403: ErrorCode.PERMISSION_DENIED,
            404: ErrorCode.NOT_FOUND,
            500: ErrorCode.SERVER_ERROR,
        }
        response.data = {
            "code": code_map.get(response.status_code, ErrorCode.UNKNOWN_ERROR),
            "detail": response.data,
        }

    return response


def error_response(code: ErrorCode, detail: str, http_status: int = status.HTTP_400_BAD_REQUEST):
    return Response({"code": code, "detail": detail}, status=http_status)
