from django.urls import path
import settings.views as settings

urlpatterns = [
    path("change_password/", settings.change_password, name="change_password"),
    path("change_nickname/", settings.change_nickname, name="change_nickname"),
    path("get_user_info/", settings.get_user_info, name="get_user_info"),
    path("user_add_permission/", settings.user_add_permission, name="user_add_permission"),
    path("user_remove_permission/", settings.user_remove_permission, name="user_remove_permission"),
    path("get_user_permission_info/", settings.get_user_permission_info, name="get_user_permission_info"),
    path("search_username_settings/", settings.search_username_settings, name="search_username_settings"),
]
