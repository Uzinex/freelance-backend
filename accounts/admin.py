from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "id",
        "username",
        "email",
        "phone",
        "role",
        "is_staff",
        "is_active",
    )
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "phone")
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("phone", "role")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("phone", "role")}),
    )
    ordering = ("id",)
