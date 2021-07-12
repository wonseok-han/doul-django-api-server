from apps.system.models import SystemMenu
from core.mixins import CoreMixin
from rest_framework.viewsets import ModelViewSet
from ..serializers import SystemMenuSerializer


class SystemMenuViewSet(CoreMixin, ModelViewSet):
    queryset = SystemMenu.objects.all()
    serializer_class = SystemMenuSerializer
