import json, jinja2
from django.shortcuts import render
from django.core.mail import send_mail
from django.http import JsonResponse
from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import get_token
from django.contrib.auth.hashers import make_password, check_password
from .models import EmailVerification

from users.models import User
from settings.models import UserPermission

from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import check_require, require
from utils.utils_time import EMAIL_VERIFICATION_EXPIRE_TIME, EMAIL_VERIFICATION_SEND_INTERVAL, get_timestamp
from utils.utils_password import MAX_PASSWORD_LENGTH
from utils.utils_permission import PERMISSION_FORUM_POST

from django.views.decorators.csrf import ensure_csrf_cookie

email_template = jinja2.Template(open("users/email_template.html").read())

# 获取 CSRF Token
@ensure_csrf_cookie
def get_csrf_token(request):
    """ 让前端获取 CSRF Token """
    return request_success({"csrfToken": get_token(request)})

# 发送验证码
@check_require
def send_verification_code(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD

    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    email = require(body, "email", "string", err_msg="Missing or error type of [email]")
    if not (email.endswith("@tsinghua.edu.cn") or email.endswith("@mails.tsinghua.edu.cn")):
        return request_success({
            "code": 1011,
            "msg": "Please use Tsinghua email address"
        })
    if User.objects.filter(email=email).exists():
        return request_success({
            "code": 1012,
            "msg": "Email already exists"
        })
    if EmailVerification.objects.filter(email=email).exists():
        created_at = EmailVerification.objects.get(email=email).created_at
        if get_timestamp() - created_at < EMAIL_VERIFICATION_SEND_INTERVAL:
            return request_success({
                "code": 1013,
                "msg": "Verification code already sent in 1 minute"
            })

    verification_code = EmailVerification.generate_verification_code()

    # 用邮箱发送验证码
    subject = "TsingLeap Email Verification Code"
    message = f"Please use the verification code below."
    html_message = email_template.render(
        verification_code=verification_code, 
        expire_time=EMAIL_VERIFICATION_EXPIRE_TIME // 60
    )
    send_mail(subject, message, "tsingleap-auth@foxmail.com", [email], html_message=html_message)

    EmailVerification.objects.update_or_create(
        email=email,
        defaults={"verification_code": verification_code, "created_at": get_timestamp()},
    )

    return request_success({ 
        "code": 0,
        "msg": "Verification code sent successfully"
    })

@check_require
def register(req: HttpRequest) :
    if req.method != "POST":
        return BAD_METHOD

    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    username = require(body, "username", "string", err_msg="Missing or error type of [username]")
    email = require(body, "email", "string", err_msg="Missing or error type of [email]")
    password1 = require(body, "password1", "string", err_msg="Missing or error type of [password1]")
    password2 = require(body, "password2", "string", err_msg="Missing or error type of [password2]")
    verification_code = require(body, "verification_code", "string", err_msg="Missing or error type of [verification_code]")

    #检查密码长度是否符合要求
    if len(password1) > MAX_PASSWORD_LENGTH:
        return request_success({
            "code": 1001,
            "msg": "Password too long"
        })
    # 检查两次输入的密码是否一致
    if password1 != password2:
        return request_success({
            "code": 1002,
            "msg": "Password mismatch"
        })
    # 检查用户名是否存在
    if User.objects.filter(username=username).exists():
        return request_success({
            "code": 1003,
            "msg": "Username already exists"
        })
    # 检查邮箱是否存在
    if User.objects.filter(email=email).exists():
        return request_success({
            "code": 1004,
            "msg": "Email already exists"
        })
    # 检查邮箱是否为清华邮箱
    if not (email.endswith("@tsinghua.edu.cn") or email.endswith("@mails.tsinghua.edu.cn")):
        return request_success({
            "code": 1005,
            "msg": "Please use Tsinghua email address"
        })
    
    obj = EmailVerification.objects.filter(email=email).first() # 验证邮箱
    if not obj:
        return request_success({
            "code": 1006,
            "msg": "Unverified email"
        })
    # 检查验证码是否正确
    if obj.verification_code != verification_code:
        return request_success({
            "code": 1007,
            "msg": "Invalid verification code"
        })
    if get_timestamp() - obj.created_at > EMAIL_VERIFICATION_EXPIRE_TIME:
        return request_success({
            "code": 1008,
            "msg": "Verification code expired"
        })
    obj.delete() # 删除验证码记录

    # password 加密
    user = User.objects.create(username=username, email=email, nickname=username, password=make_password(password1)) 
    UserPermission.objects.create(user=user, permission=PERMISSION_FORUM_POST)

    return request_success({
        'code': 0,
        'msg': "Register successfully",
        'data': {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'email': user.email,
        },
    })
    
# 登录
@check_require
def login(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    body = json.loads(req.body.decode("utf-8")) if req.body else {}

    username = require(body, "username", "string", err_msg="Missing or error type of [username]")
    password = require(body, "password", "string", err_msg="Missing or error type of [password]")

    user = User.objects.filter(username=username).first() 
    if not user:
        return request_success({
            "code": 1009,
            "msg": "User not found"
        })
    if not check_password(password, user.password):
        return request_success({
            "code": 1010,
            "msg": "Wrong password"
        })
    
    return request_success({
        'code': 0,
        'msg': "Login successfully",
        'data': {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'email': user.email,
        },
    })