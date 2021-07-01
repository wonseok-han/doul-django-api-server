from django.utils.translation import gettext as _

from rest_framework.exceptions import PermissionDenied
from rest_framework_jwt.authentication import (
    JSONWebTokenAuthentication as OrigJSONWebTokenAuthentication,
)

from .models import SystemUser


class JSONWebTokenAuthentication(OrigJSONWebTokenAuthentication):
    def authenticate(self, request):
        # token 값 자체에 대한 검증
        user_and_token = super().authenticate(request)
        if user_and_token is None:
            return None

        # token 값 자체에 대한 검증 후처리
        system_user: SystemUser
        system_user, token_from_request = user_and_token

        if system_user.token != token_from_request:
            msg = _("등록되지 않은 토큰입니다.")
            raise PermissionDenied(msg)

        return system_user, system_user.token


class TransferringUserJWTAuthentication(JSONWebTokenAuthentication):
    def authenticate(self, request):
        user_and_token = super().authenticate(request)
        if user_and_token is None:
            return None

        system_user, token = user_and_token

        transfer_username: str = request.META.get("X-Transfer-User", None)
        if transfer_username:
            # TODO: 사용자 전환 권한 체킹하고, 권한이 없으면 PermissionDenied 예외 발생

            transfer_user = (
                SystemUser.objects.exclude(username=system_user.username)
                .filter(username=transfer_username)
                .first()
            )
            if transfer_user is None:
                raise PermissionDenied(_("사용자 전환 계정을 찾을 수 없습니다."))
            # if transfer_user.is_active:  # TODO: FG 플래그 필드와 BooleanField 체킹
            #     raise PermissionDenied(_("사용자 전환 계정이 비활성화되어있습니다."))

            request.orig_user = system_user
            system_user = transfer_user
        else:
            request.orig_user = system_user

        return system_user, token
