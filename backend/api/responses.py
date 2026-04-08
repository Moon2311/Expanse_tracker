from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def envelope(*, success=True, data=None, message=None, errors=None, meta=None, code=None):
    body = {"success": success}
    if data is not None:
        body["data"] = data
    if message is not None:
        body["message"] = message
    if errors is not None:
        body["errors"] = errors
    if meta is not None:
        body["meta"] = meta
    if code is not None:
        body["code"] = code
    return body


def ok(data=None, message=None, status_code=status.HTTP_200_OK, meta=None):
    return Response(
        envelope(success=True, data=data, message=message, meta=meta),
        status=status_code,
    )


def fail(
    message,
    *,
    errors=None,
    code="error",
    status_code=status.HTTP_400_BAD_REQUEST,
    extra=None,
):
    payload = envelope(success=False, message=message, errors=errors)
    payload["code"] = code
    if extra:
        payload.update(extra)
    return Response(payload, status=status_code)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(response.data, dict):
            if "detail" in response.data and len(response.data) == 1:
                msg = response.data["detail"]
                response.data = envelope(
                    success=False,
                    message=str(msg),
                    code="api_error",
                )
            else:
                response.data = envelope(
                    success=False,
                    message="Validation failed.",
                    errors=response.data,
                    code="validation_error",
                )
        return response
    return None
