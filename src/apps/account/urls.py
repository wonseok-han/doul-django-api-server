from django.urls import include, path

from . import views


urlpatterns = [
    path("login/", views.ObtainJSONWebTokenView.as_view(), name="obtain-jwt-token"),
    path(
        "token/refresh/",
        views.RefreshJSONWebTokenView.as_view(),
        name="refresh-jwt-token",
    ),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "jwt-authentication-view/",
        views.jwt_authentication_view,
        name="jwt-authentication-view",
    ),
]
