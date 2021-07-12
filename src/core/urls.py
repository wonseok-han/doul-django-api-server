from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("batch/", views.batch, name="batch"),
]
