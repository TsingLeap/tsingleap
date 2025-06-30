from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
import unittest
import json

from users.models import User
from settings.models import UserPermission
from utils.utils_permission import PERMISSION_USER_IS_ADMIN
from utils.utils_require import ErrorCode

CONTENT_TYPE = "application/json"

VALID_USERNAME = "testuser"
VALID_PASSWORD = "password123"
VALID_EMAIL = "testuser@mails.tsinghua.edu.cn"
VALID_NICKNAME = "Test User"
VALID_PERMISSION_NAME = "test_permission"
VALID_PERMISSION_INFO = ""

class ChangePasswordTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = VALID_USERNAME
        self.password = VALID_PASSWORD
        self.new_password = "newpassword123"
        self.long_password = VALID_PASSWORD * 10
        User.objects.create(
            username=self.username,
            email=VALID_EMAIL,
            password=make_password(self.password),
            nickname=VALID_NICKNAME
        )

    # 修改密码方式不为POST
    def test_change_password_bad_method(self):
        response = self.client.get(reverse('change_password'))
        self.assertEqual(response.status_code, 405)

    # 缺失参数
    def test_change_password_lack_params(self):
        response = self.client.post(reverse('change_password'))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], -2)

    # 用户名不存在
    def test_change_password_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "password": self.password,
            "new_password": self.new_password
        }
        response = self.client.post(
            reverse('change_password'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    # 密码不正确
    def test_change_password_incorrect_password(self):
        data = {
            "username": self.username,
            "password": "wrongpassword",
            "new_password": self.new_password
        }
        response = self.client.post(
            reverse('change_password'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1014)
        self.assertEqual(data["msg"], "Password is incorrect")

    # 新密码过长
    def test_change_password_long_password(self):
        data = {
            "username": self.username,
            "password": self.password,
            "new_password": self.long_password
        }
        response = self.client.post(
            reverse('change_password'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1016)
        self.assertEqual(data["msg"], "Password too long")

    # 成功修改密码
    def test_change_password_success(self):
        data = {
            "username": self.username,
            "password": self.password,
            "new_password": self.new_password
        }
        response = self.client.post(
            reverse('change_password'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Password changed successfully")

        # 验证新密码是否生效
        user = User.objects.get(username=self.username)
        self.assertTrue(check_password(self.new_password, user.password))

class ChangeNicknameTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = VALID_USERNAME
        self.password = VALID_PASSWORD
        self.nickname = VALID_NICKNAME
        self.new_nickname = "New Test User"
        User.objects.create(
            username=self.username,
            email=VALID_EMAIL,
            password=make_password(self.password),
            nickname=self.nickname
        )

    # 修改昵称方式不为POST
    def test_change_nickname_bad_method(self):
        response = self.client.get(reverse('change_nickname'))
        self.assertEqual(response.status_code, 405)

    # 缺失参数
    def test_change_nickname_lack_params(self):
        response = self.client.post(reverse('change_nickname'))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], -2)

    # 用户名不存在
    def test_change_nickname_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "nickname": self.new_nickname
        }
        response = self.client.post(
            reverse('change_nickname'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    # 成功修改昵称
    def test_change_nickname_success(self):
        data = {
            "username": self.username,
            "nickname": self.new_nickname
        }
        response = self.client.post(
            reverse('change_nickname'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Nickname changed successfully")

        # 验证昵称是否已更新
        user = User.objects.get(username=self.username)
        self.assertEqual(user.nickname, self.new_nickname)

class GetUserInfoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = VALID_USERNAME
        self.password = VALID_PASSWORD
        self.email = VALID_EMAIL
        self.nickname = VALID_NICKNAME
        User.objects.create(
            username=self.username,
            email=self.email,
            password=make_password(self.password),
            nickname=self.nickname
        )

    # 获取用户信息方式不为GET
    def test_get_user_info_bad_method(self):
        response = self.client.post(reverse('get_user_info'))
        self.assertEqual(response.status_code, 405)

    # 缺失参数
    def test_get_user_info_lack_params(self):
        response = self.client.get(reverse('get_user_info'))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], -2)

    # 用户名不存在
    def test_get_user_info_user_not_exists(self):
        data = {"username": "nonexistentuser"}
        response = self.client.get(
            reverse('get_user_info'),
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    # 成功获取用户信息
    def test_get_user_info_success(self):
        data = {"username": self.username}
        response = self.client.get(
            reverse('get_user_info'),
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Get user info successfully")
        self.assertEqual(data["data"]["username"], self.username)
        self.assertEqual(data["data"]["nickname"], self.nickname)
        self.assertEqual(data["data"]["email"], self.email)

class UserPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = VALID_USERNAME
        self.password = VALID_PASSWORD
        self.email = VALID_EMAIL
        self.nickname = VALID_NICKNAME
        self.permission_name = VALID_PERMISSION_NAME
        self.permission_info = VALID_PERMISSION_INFO
        
        # 创建普通用户
        self.user = User.objects.create(
            username=self.username,
            email=self.email,
            password=make_password(self.password),
            nickname=self.nickname
        )
        
        # 创建管理员用户
        self.admin_username = "adminuser"
        self.admin = User.objects.create(
            username=self.admin_username,
            email="admin@mails.tsinghua.edu.cn",
            password=make_password(self.password),
            nickname="Admin User"
        )
        
        # 给管理员添加管理员权限
        UserPermission.objects.create(
            user=self.admin,
            permission=PERMISSION_USER_IS_ADMIN,
            permission_info=""
        )
        
        # 给普通用户添加测试权限
        UserPermission.objects.create(
            user=self.user,
            permission=self.permission_name,
            permission_info=self.permission_info
        )

    # 添加权限方式不为POST
    def test_user_add_permission_bad_method(self):
        response = self.client.get(reverse('user_add_permission'))
        self.assertEqual(response.status_code, 405)

    # 添加权限缺失参数
    def test_user_add_permission_lack_params(self):
        response = self.client.post(reverse('user_add_permission'))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], -2)

    # 操作者不存在
    def test_user_add_permission_operator_not_exists(self):
        data = {
            "operator": "nonexistentoperator",
            "username": self.username,
            "permission_name": "new_permission",
            "permission_info": "New permission info"
        }
        response = self.client.post(
            reverse('user_add_permission'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    # 用户不存在
    def test_user_add_permission_user_not_exists(self):
        data = {
            "operator": self.admin_username,
            "username": "nonexistentuser",
            "permission_name": "new_permission",
            "permission_info": "New permission info"
        }
        response = self.client.post(
            reverse('user_add_permission'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    # 操作者没有权限
    def test_user_add_permission_no_permission(self):
        # 创建一个没有管理员权限的用户
        no_permission_user = User.objects.create(
            username="nopermission",
            email="nopermission@mails.tsinghua.edu.cn",
            password=make_password(self.password),
            nickname="No Permission User"
        )
        
        data = {
            "operator": "nopermission",
            "username": self.username,
            "permission_name": "new_permission",
            "permission_info": ""
        }
        response = self.client.post(
            reverse('user_add_permission'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    # 成功添加权限
    def test_user_add_permission_success(self):
        new_permission_name = "new_permission"
        new_permission_info = ""
        data = {
            "operator": self.admin_username,
            "username": self.username,
            "permission_name": new_permission_name,
            "permission_info": new_permission_info
        }
        response = self.client.post(
            reverse('user_add_permission'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Permission added successfully")

        # 验证权限是否已添加
        self.assertTrue(UserPermission.objects.filter(
            user=self.user,
            permission=new_permission_name,
            permission_info=new_permission_info
        ).exists())

    # 删除权限方式不为POST
    def test_user_remove_permission_bad_method(self):
        response = self.client.get(reverse('user_remove_permission'))
        self.assertEqual(response.status_code, 405)

    # 删除权限缺失参数
    def test_user_remove_permission_lack_params(self):
        response = self.client.post(reverse('user_remove_permission'))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], -2)

    # 操作者不存在
    def test_user_remove_permission_operator_not_exists(self):
        data = {
            "operator": "nonexistentoperator",
            "username": self.username,
            "permission_name": self.permission_name,
            "permission_info": self.permission_info
        }
        response = self.client.post(
            reverse('user_remove_permission'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    # 用户不存在
    def test_user_remove_permission_user_not_exists(self):
        data = {
            "operator": self.admin_username,
            "username": "nonexistentuser",
            "permission_name": self.permission_name,
            "permission_info": self.permission_info
        }
        response = self.client.post(
            reverse('user_remove_permission'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    # 操作者没有权限
    def test_user_remove_permission_no_permission(self):
        # 创建一个没有管理员权限的用户
        no_permission_user = User.objects.create(
            username="nopermission",
            email="nopermission@mails.tsinghua.edu.cn",
            password=make_password(self.password),
            nickname="No Permission User"
        )
        
        data = {
            "operator": "nopermission",
            "username": self.username,
            "permission_name": self.permission_name,
            "permission_info": self.permission_info
        }
        response = self.client.post(
            reverse('user_remove_permission'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    # 权限不存在
    def test_user_remove_permission_not_found(self):
        data = {
            "operator": self.admin_username,
            "username": self.username,
            "permission_name": "nonexistentpermission",
            "permission_info": ""
        }
        response = self.client.post(
            reverse('user_remove_permission'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1021)
        self.assertEqual(data["msg"], "Permission not found")

    # 成功删除权限
    def test_user_remove_permission_success(self):
        data = {
            "operator": self.admin_username,
            "username": self.username,
            "permission_name": self.permission_name,
            "permission_info": self.permission_info
        }
        response = self.client.post(
            reverse('user_remove_permission'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Permission removed successfully")

        # 验证权限是否已删除
        self.assertFalse(UserPermission.objects.filter(
            user=self.user,
            permission=self.permission_name,
            permission_info=self.permission_info
        ).exists())

    # 获取权限信息方式不为GET
    def test_get_user_permission_info_bad_method(self):
        response = self.client.post(reverse('get_user_permission_info'))
        self.assertEqual(response.status_code, 405)

    # 获取权限信息缺失参数
    def test_get_user_permission_info_lack_params(self):
        response = self.client.get(reverse('get_user_permission_info'))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], -2)

    # 用户名不存在
    def test_get_user_permission_info_user_not_exists(self):
        data = {"username": "nonexistentuser"}
        response = self.client.get(
            reverse('get_user_permission_info'),
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    # 成功获取权限信息
    def test_get_user_permission_info_success(self):
        data = {"username": self.username}
        response = self.client.get(
            reverse('get_user_permission_info'),
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["username"], self.username)
        self.assertEqual(data["data"][0]["permission_name"], self.permission_name)
        self.assertEqual(data["data"][0]["permission_info"], self.permission_info)
