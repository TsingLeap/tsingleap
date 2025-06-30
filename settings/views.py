import json

from utils.utils_request import BAD_METHOD, request_success
from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth.hashers import make_password, check_password
from utils.utils_require import check_require, require, ErrorCode
from utils.utils_params import get_user
from utils.utils_password import MAX_PASSWORD_LENGTH
from utils.utils_permission import add_permission, remove_permission 
from users.models import User
from .models import UserPermission

#修改密码
@check_require
def change_password(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD

    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    # 获取参数
    password = require(body, "password", "string")
    new_password = require(body, "new_password", "string")

    # 检查用户名和密码
    try:
        user = get_user(body, "username")
        if not check_password(password, user.password):
            return request_success({
                "code": 1014,
                "msg": "Password is incorrect"
            })
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)

    # 检查密码长度
    if len(new_password) > MAX_PASSWORD_LENGTH:
        return request_success({
            "code": 1016,
            "msg": "Password too long"
        })

    # 更新密码
    user.password = make_password(new_password)
    user.save()

    return request_success({
        "code": 0,
        "msg": "Password changed successfully"
    })

#修改昵称
@check_require
def change_nickname(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD

    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    # 获取参数
    nickname = require(body, "nickname", "string")

    # 检查用户名和昵称
    try:
        user = get_user(body, "username")
        user.nickname = nickname
        user.save()
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)

    return request_success({
        "code": 0,
        "msg": "Nickname changed successfully"
    })

#获取用户信息
@check_require
def get_user_info(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD

    # 检查用户名
    try:
        user = get_user(req.GET, "username")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)

    return request_success({
        "code": 0,
        "msg": "Get user info successfully",
        "data": {
            "nickname": user.nickname,
            "username": user.username,
            "email": user.email,
        }
    })

#添加权限
@check_require
def user_add_permission(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    #获取参数
    permission_name = require(body, "permission_name", "string")
    permission_info = require(body, "permission_info", "string")

    try:
        operator_user = get_user(body, "operator")
        user = get_user(body, "username")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)

    result = add_permission(operator = operator_user, 
                            user = user, 
                            permission_name = permission_name, 
                            permission_info = permission_info)

    return request_success(result)

#删除权限
@check_require
def user_remove_permission(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    #获取参数
    permission_name = require(body, "permission_name", "string")
    permission_info = require(body, "permission_info", "string")

    try:
        operator_user = get_user(body, "operator")
        user = get_user(body, "username")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)

    result = remove_permission(operator = operator_user, 
                               user = user, 
                               permission_name = permission_name, 
                               permission_info = permission_info)

    return request_success(result)

#获取权限信息
@check_require
def get_user_permission_info(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD

    try:
        user = get_user(req.GET, "username")
    except User.DoesNotExist:
        return request_success(ErrorCode.USER_DOES_NOT_EXIST)

    objs = UserPermission.objects.filter(user = user)

    result = []
    for obj in objs:
        result.append({
            "username": obj.user.username,
            "permission_name": obj.permission,
            "permission_info": obj.permission_info,
        })    

    return request_success({
        "code": 0,
        "data": result
    })


#搜索用户名前缀匹配
@check_require
def search_username_settings(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD

    username_prefix = require(req.GET, "username_prefix", "string") 
    
    users = User.objects.filter(username__startswith=username_prefix).values("username", "nickname")[:10]
    
    user_list = list(users)
    if len(user_list) == 0:
        return request_success({
            'code': 1019,
            'msg': "No user found",
            'data': {
                'users': user_list,
            },
        })

    return request_success({
        'code': 0,
        'msg': "Search successfully",
        'data': {
            'users': user_list,
        },
    })