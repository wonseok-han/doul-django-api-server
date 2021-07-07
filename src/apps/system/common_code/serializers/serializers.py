from apps.system.models import SystemCommonCodeMaster, SystemCommonCodeDetail
from core.serializers import CoreHyperlinkedSerializer


class SystemCommonCodeMasterSerializer(CoreHyperlinkedSerializer):
    class Meta:
        model = SystemCommonCodeMaster
        fields = "__all__"


class SystemCommonCodeDetailSerializer(CoreHyperlinkedSerializer):
    class Meta:
        model = SystemCommonCodeDetail
        fields = ["__all__"]
