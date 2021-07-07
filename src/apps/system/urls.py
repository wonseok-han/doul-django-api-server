from django.urls import include, path

urlpatterns = [
    path("common_code/", include("apps.system.common_code.urls")),
    path("common_menu/", include("apps.system.common_menu.urls")),
]
