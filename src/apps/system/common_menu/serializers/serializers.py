from apps.system.models import SystemMenu
from core.serializers import CoreHyperlinkedSerializer


class SystemMenuSerializer(CoreHyperlinkedSerializer):
    class Meta:
        model = SystemMenu
        fields = "__all__"
