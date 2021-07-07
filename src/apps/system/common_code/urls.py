from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SystemCommonCodeMasterViewSet, SystemCommonCodeDetailViewSet


router = DefaultRouter()
router.register("system_common_code_master", SystemCommonCodeMasterViewSet)
router.register("system_common_code_detail", SystemCommonCodeDetailViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
