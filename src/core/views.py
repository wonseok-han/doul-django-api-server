import json
import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from core.utils import get_client_ip
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.middleware.csrf import get_token as csrf_get_token
from django.test.client import ClientHandler, conditional_content_removal
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.test import APIClient


class Method(str, Enum):
    GET = "GET"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass
class BatchOption:
    """
    Front에서의 요청을 아래와 같이 구성하여 받을 수 있도록 해야합니다.
    """

    url: str
    method: Method
    data: Optional[Dict[str, Any]] = None


class APIClientHandler(ClientHandler):
    """
    A HTTP Handler that can be used for testing purposes. Use the WSGI
    interface to compose requests, but return the raw HttpResponse object with
    the originating WSGIRequest attached to its ``wsgi_request`` attribute.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(enforce_csrf_checks=False, *args, **kwargs)

    def __call__(self, environ):
        if self._middleware_chain is None:
            self.load_middleware()

        request = WSGIRequest(environ)
        request._batch_request = (
            True  # custom attribute. it is using in CoreMixin.dispatch.
        )
        request._dont_enforce_csrf_checks = not self.enforce_csrf_checks
        response = self.get_response(request)
        conditional_content_removal(request, response)
        response.wsgi_request = request

        return response


class Rollback(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def batch(request):
    """
    다수의 요청을 하나의 트랜잭션으로 처리합니다.
    """

    batch_option_list: List[BatchOption] = [
        BatchOption(**kwargs) for kwargs in request.data
    ]

    response_list = []
    status_code = status.HTTP_200_OK

    try:
        with transaction.atomic():
            client = APIClient()
            client.handler = APIClientHandler()

            content_type = request.headers.get("Content-Type")

            headers = {
                "Content-Type": content_type,
                "X-Forwarded-For": get_client_ip(request),
                "X-CSRFToken": csrf_get_token(request),
                "Referer": request.META.get("HTTP_REFERER"),
                "User-Agent": request.META.get("HTTP_USER_AGENT"),
                "X-Current-Menu": request.headers.get("X-Current-Menu"),
            }
            headers = {k: v for k, v in headers.items() if v is not None}

            authorization = request.headers.get("Authorization")
            if authorization:
                client.credentials(HTTP_AUTHORIZATION=authorization)

            # 뷰 내에서 다른 View를 호출합니다.
            for batch_option in batch_option_list:
                # 조회성 요청(GET/OPTIONS/HEAD)은 거부합니다.
                if batch_option.method not in (
                    Method.POST,
                    Method.PUT,
                    Method.DELETE,
                ):
                    raise Rollback(status.HTTP_405_METHOD_NOT_ALLOWED)

                # 다른 서버로의 요청은 수행하지 않습니다.
                if not batch_option.url.startswith("/"):
                    raise Rollback(status.HTTP_400_BAD_REQUEST)

                handler = getattr(client, batch_option.method.lower())
                response = handler(
                    batch_option.url,
                    json.dumps(batch_option.data),
                    content_type=content_type,
                    **headers
                )

                response_list.append(
                    {
                        "status_code": response.status_code,
                        "data": response.data,
                    }
                )

                if response.status_code >= status.HTTP_400_BAD_REQUEST:
                    raise Rollback(response.status_code)
    except Rollback as e:
        status_code = e.status_code
    except Exception:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        traceback.print_stack()

    return Response(response_list, status=status_code)
