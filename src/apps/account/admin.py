from django.contrib import admin
from .models import User, IssuedToken


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(IssuedToken)
class IssuedTokenAdmin(admin.ModelAdmin):
    pass
