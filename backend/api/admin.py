from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from api.models import (
    ChatMessage,
    Expense,
    GroupExpenseSplit,
    GroupInvitation,
    GroupMembership,
    Notification,
    SpendGroup,
    User,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("username",)
    list_display = ("username", "email", "display_name", "is_staff")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Profile", {"fields": ("email", "display_name", "first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "email", "password1", "password2")}),
    )


admin.site.register(SpendGroup)
admin.site.register(GroupMembership)
admin.site.register(GroupInvitation)
admin.site.register(Expense)
admin.site.register(GroupExpenseSplit)
admin.site.register(Notification)
admin.site.register(ChatMessage)
