from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SystemMenuViewSet


router = DefaultRouter()
router.register("system_menu", SystemMenuViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
