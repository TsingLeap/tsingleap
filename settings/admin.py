from django.contrib import admin

# Register your models here.
from .models import UserPermission

@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'user__username', 'permission', 'permission_info')
    search_fields = ('user__username', 'permission', 'permission_info')
    list_filter = ('user__username', 'permission', 'permission_info')
