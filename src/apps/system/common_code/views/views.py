from apps.system.models import SystemCommonCodeMaster, SystemCommonCodeDetail
from core.mixins import CoreMixin
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
