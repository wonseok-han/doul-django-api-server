from typing import Optional

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_jwt.compat import set_cookie_with_token
from rest_framework_jwt.serializers import (
    RefreshAuthTokenSerializer,
    JSONWebTokenSerializer,
)
from rest_framework_jwt.settings import api_settings

from .authentication import TransferringUserJWTAuthentication
from .models import IssuedToken, User


class BaseJSONWebTokenAPIView(GenericAPIView):
    """Base JWT auth view used for all other JWT views (verify/refresh)."""

    permission_classes = ()
    authentication_classes = ()

    serializer_class = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user: Optional[User] = None  # 요청한 user
        self.issued_token: Optional[str] = None  # 새로 발급받은 JWT
        self.issued_at: Optional[int] = None  # 토큰 생성시각

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.current_user = serializer.validated_data["user"]
        self.issued_token = serializer.validated_data["token"]
        self.issued_at = serializer.validated_data["issued_at"]

        response_data = TransferringUserJWTAuthentication.jwt_create_response_payload(
            self.issued_token, self.current_user, request, self.issued_at
        )

        response = Response(response_data, status=status.HTTP_201_CREATED)

        if api_settings.JWT_AUTH_COOKIE:
            set_cookie_with_token(
                response, api_settings.JWT_AUTH_COOKIE, self.issued_token
            )

        return response


class ObtainJSONWebTokenView(BaseJSONWebTokenAPIView):
    """
    로그인할 유저의 username/password를 POST 요청으로 받아서
    인증에 통과할 경우 JSON Web Token를 반환하는 APIView
    """

    serializer_class = JSONWebTokenSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        IssuedToken.inactive_all_and_create(self.current_user, self.issued_token)
        return response

    def delete(self, request, *args, **kwargs):
        """
        로그아웃: 현재 인증에 사용된 Token을 폐기합니다.
        """

        if not request.user.is_authenticated:
            raise PermissionDenied

        # 기존에 발급된 모든 토큰들을 비활성화시킵니다.
        IssuedToken.objects.filter(user=self.current_user).update(is_active=False)

        return Response(status=status.HTTP_204_NO_CONTENT)


# FIXME: 수시로 갱신할 경우 얼마나 많은 IssuedToken이 생성이 될까?
class RefreshJSONWebTokenView(BaseJSONWebTokenAPIView):
    """
    API View that returns a refreshed token (with new expiration) based on
    existing token
    If 'orig_iat' field (original issued-at-time) is found it will first check
    if it's within expiration window, then copy it to the new token.
    """

    serializer_class = RefreshAuthTokenSerializer


@api_view(["GET"])
@authentication_classes([TransferringUserJWTAuthentication])
def jwt_authentication_view(request):
    obj = {
        "username": request.user.username,
    }
    if hasattr(request, "orig_user"):
        obj["orig_username"] = request.orig_user.username
    return JsonResponse(obj)


class LogoutView(BaseJSONWebTokenAPIView):
    """
    로그인할 유저의 username/password를 POST 요청으로 받아서
    인증에 통과할 경우 JSON Web Token를 반환하는 APIView
    """

    serializer_class = JSONWebTokenSerializer
    authentication_classes = [TransferringUserJWTAuthentication]

    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            raise PermissionDenied

        # 기존에 발급된 모든 토큰들을 삭제시킵니다.
        IssuedToken.objects.filter(user=request.user).delete()

        # return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"success": ("Successfully logged out.")}, status=status.HTTP_200_OK
        )
