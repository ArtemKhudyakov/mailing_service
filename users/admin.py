from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "username",
        "email",
        "country",
        "phone",
        "avatar",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("username", "email", "phone")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_verified", "groups")
    ordering = ("username",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    list_editable = (
        "username",
        "email",
        "country",
        "phone",
        "avatar",
        "is_staff",
        "is_superuser",
    )
