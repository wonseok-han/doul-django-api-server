from apps.system.models import SystemMenu
from core.mixins import CoreMixinViewSet
from rest_framework.viewsets import ModelViewSet
from ..serializers import SystemMenuSerializer


class SystemMenuViewSet(CoreMixinViewSet, ModelViewSet):
    queryset = SystemMenu.objects.all()
    serializer_class = SystemMenuSerializer
