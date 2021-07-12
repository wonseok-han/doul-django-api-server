from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core import views


router = DefaultRouter()
router.register("batch", views.batch, name="batch")

urlpatterns = [
    path("", include(router.urls)),
]
