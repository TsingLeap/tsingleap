from functools import wraps
from utils.utils_require import ErrorCode
from settings.models import UserPermission
from utils.utils_request import request_failed, request_success

PERMISSION_USER_IS_ADMIN = "user.is_superadmin"

PERMISSION_MATCH_MANAGE_MATCH = "match.manage_match"
PERMISSION_MATCH_UPDATE_MATCH_INFO = "match.update_match_info"

PERMISSION_FORUM_MANAGE_FORUM = "forum.manage_forum"
PERMISSION_FORUM_POST = "forum.post"
PERMISSION_FORUM_POST_HIGHLIGHT = "forum.post_highlight"

PERMISSION_TAG_MANAGE_TAG = "tag.manage_tag"

def has_permission(user, permission_name, permission_info = "_Default"):
    if permission_info == "_Default":
        return UserPermission.objects.filter(user=user,
                                             permission=permission_name).exists()
    return UserPermission.objects.filter(user=user, 
                                         permission=permission_name, 
                                         permission_info=permission_info).exists()
    
def require_permission(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not has_permission(request.user, permission_name):
                return request_failed(403, "No permission", 403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def add_permission(operator, user, permission_name, permission_info = ""):
    operator_has_permission = has_permission(operator, PERMISSION_USER_IS_ADMIN)
    if permission_name == PERMISSION_MATCH_UPDATE_MATCH_INFO:
        operator_has_permission = has_permission(operator, PERMISSION_MATCH_MANAGE_MATCH)
    if permission_name == PERMISSION_FORUM_POST:
        operator_has_permission = operator_has_permission or has_permission(operator, PERMISSION_FORUM_MANAGE_FORUM)
    if not operator_has_permission:
        return ErrorCode.NO_PERMISSION
    if not UserPermission.objects.filter(user=user, 
                                         permission=permission_name, 
                                         permission_info=permission_info).exists():
        UserPermission.objects.create(user=user, 
                                     permission=permission_name, 
                                     permission_info=permission_info)
    return {"code": 0, 
            "msg": "Permission added successfully"}

def remove_permission(operator, user, permission_name, permission_info = ""):
    operator_has_permission = has_permission(operator, PERMISSION_USER_IS_ADMIN)
    if permission_name == PERMISSION_MATCH_UPDATE_MATCH_INFO:
        operator_has_permission = has_permission(operator, PERMISSION_MATCH_MANAGE_MATCH)
    if permission_name == PERMISSION_FORUM_POST:
        operator_has_permission = operator_has_permission or has_permission(operator, PERMISSION_FORUM_MANAGE_FORUM)
    if not operator_has_permission:
        return ErrorCode.NO_PERMISSION
    if not UserPermission.objects.filter(user=user, 
                                         permission=permission_name, 
                                         permission_info=permission_info).exists():
        return {"code": 1021, 
                "msg": "Permission not found"}
    UserPermission.objects.filter(user=user, 
                                 permission=permission_name, 
                                 permission_info=permission_info).delete()
    return {"code": 0, 
            "msg": "Permission removed successfully"}