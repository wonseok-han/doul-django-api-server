from django.core.handlers.wsgi import WSGIRequest
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

ALLOWED_HTTP_METHOD_NAMES = ["GET", "POST"]


@property
def patched_allow_methods(self):
    return ALLOWED_HTTP_METHOD_NAMES


class PatchHttpMethodMiddleware:
    """
    Front의 Http Method를 GET, POST만 허용토록 합니다.
    """

    def __init__(self, get_response):
        """
        프로젝트 초기화시 1회만 호촐됩니다.
        """
        APIView.http_method_names = ["get", "post", "put", "patch", "delete"]
        APIView.allowed_methods = patched_allow_methods

        self.get_response = get_response

    def __call__(self, request: WSGIRequest) -> Response:
        """
        매 View 호출시마다 호출됩니다.
        """

        # FIXME: 해당 로직이 "batch/" url에서도 동작하는지 확인 필요.
        # 요청의 method는 ALLOW_HTTP_METHOD_NAMES만 허용합니다.
        # if request.method not in ALLOWED_HTTP_METHOD_NAMES:
        #     raise exceptions.MethodNotAllowed(request.method)

        x_http_method = request.META.get("HTTP_X_HTTP_METHOD", "").lower()
        if x_http_method:
            if x_http_method not in APIView.http_method_names:
                raise exceptions.MethodNotAllowed(x_http_method)
            request.method = x_http_method.upper()

        response = self.get_response(request)
        return response
