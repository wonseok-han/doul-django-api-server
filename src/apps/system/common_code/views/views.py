from apps.system.models import SystemCommonCodeMaster, SystemCommonCodeDetail
from core.mixins import CoreMixin
from django.http import Http404
from rest_framework.viewsets import ModelViewSet
from ..serializers import (
    SystemCommonCodeMasterSerializer,
    SystemCommonCodeDetailSerializer,
)


class SystemCommonCodeMasterViewSet(CoreMixin, ModelViewSet):
    queryset = SystemCommonCodeMaster.objects.all()
    serializer_class = SystemCommonCodeMasterSerializer


class SystemCommonCodeDetailViewSet(CoreMixin, ModelViewSet):
    queryset = SystemCommonCodeDetail.objects.all()
    serializer_class = SystemCommonCodeDetailSerializer

    search_fields = ["common_cd_key"]

    def list(self, request, *args, **kwargs):
        """
        리스트를 조회합니다.
        """
        queryset = self.get_queryset()

        common_cd_key = request.query_params.get("common_cd_key")
        if common_cd_key is None:
            raise Http404("공통코드 쿼리스트링이 누락되었습니다.")

        conditions = {}
        for field_name, value in self.request.query_params.items():
            if field_name in self.search_fields:
                conditions[field_name] = value

        queryset = queryset.filter(**conditions)

        return super().list(request, queryset=queryset)
