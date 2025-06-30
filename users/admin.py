from django.contrib import admin

# Register your models here.
from .models import EmailVerification, User

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'verification_code', 'created_at')  # 列表显示的字段
    search_fields = ('email',)  # 添加搜索功能
    list_filter = ('created_at',)  # 添加筛选器

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')  # 在后台列表中显示的字段
    search_fields = ('username', 'email')  # 允许通过用户名或邮箱搜索
    list_filter = ('email',)  # 通过 email 筛选