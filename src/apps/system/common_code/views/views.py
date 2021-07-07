from apps.system.models import SystemCommonCodeMaster, SystemCommonCodeDetail
from core.mixins import CoreMixinViewSet
from rest_framework.viewsets import ModelViewSet
from ..serializers import (
    SystemCommonCodeMasterSerializer,
    SystemCommonCodeDetailSerializer,
)


class SystemCommonCodeMasterViewSet(CoreMixinViewSet, ModelViewSet):
    queryset = SystemCommonCodeMaster.objects.all()
    serializer_class = SystemCommonCodeMasterSerializer


class SystemCommonCodeDetailViewSet(CoreMixinViewSet, ModelViewSet):
    queryset = SystemCommonCodeDetail.objects.all()
    serializer_class = SystemCommonCodeDetailSerializer
