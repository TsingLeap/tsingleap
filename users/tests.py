from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from utils import utils_time
import unittest
import json

from users.models import User, EmailVerification

CONTENT_TYPE = "application/json"

VALID_EMAIL = "user@mails.tsinghua.edu.cn"
INVALID_EMAIL = "user@gmail.com"
RESENT_EMAIL = "resent_user@mails.tsinghua.edu.cn"
EXIST_EMAIL = "exist_user@mails.tsinghua.edu.cn"
VERIFICATION_CODE = "123456"
VALID_PASSWORD = "password123"

class CSRFTokenTests(TestCase):
    def setUp(self):
        self.client = Client()

    #返回JSON中应该包含'csrfToken'
    def test_get_csrf_token(self):
        response = self.client.get(reverse('get_csrf_token'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn("csrfToken", data)

class SendVerificationCodeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.valid_email = VALID_EMAIL
        self.invalid_email = INVALID_EMAIL
        self.resent_email = RESENT_EMAIL
        self.exist_email = EXIST_EMAIL
        EmailVerification.objects.create(
            email = self.resent_email, 
            verification_code = VERIFICATION_CODE,
            created_at = utils_time.get_timestamp()
        )
        User.objects.create(
            username = "exist_user",
            email = self.exist_email,
            password = make_password(VALID_PASSWORD)
        )

    #发送验证码方式不为POST
    def test_send_verification_code_bad_method(self):
        response = self.client.get(reverse('send_verification_code')) 
        self.assertEqual(response.status_code, 405)

    #缺失参数
    def test_send_verification_code_lack_email(self):
        response = self.client.post(reverse('send_verification_code'))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], -2)

    #邮箱不是清华邮箱
    def test_send_verification_code_invalid_email(self):
        data = {"email": self.invalid_email}
        response = self.client.post(
            reverse('send_verification_code'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1011)
        self.assertEqual(data["msg"], "Please use Tsinghua email address")

    #邮箱已存在
    def test_send_verification_code_email_exists(self):
        data = {"email": self.exist_email}
        response = self.client.post(
            reverse('send_verification_code'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1012)
        self.assertEqual(data["msg"], "Email already exists")

    #验证码1分钟内已发送
    def test_send_verification_code_sent_recently(self):
        EmailVerification.objects.filter(email=self.resent_email).update(created_at=utils_time.get_timestamp()-30)
        data = {"email": self.resent_email}
        response = self.client.post(
            reverse('send_verification_code'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1013)
        self.assertEqual(data["msg"], "Verification code already sent in 1 minute")

    #成功发送验证码
    def test_send_verification_code_success(self):
        data = {"email": self.valid_email}
        response = self.client.post(
            reverse('send_verification_code'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["msg"], "Verification code sent successfully")

class RegisterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.valid_email = VALID_EMAIL
        self.invalid_email = INVALID_EMAIL
        self.verification_code = VERIFICATION_CODE
        self.valid_password = VALID_PASSWORD
        self.invalid_password = VALID_PASSWORD * 5
        EmailVerification.objects.create(
            email = self.valid_email, 
            verification_code = self.verification_code,
            created_at = utils_time.get_timestamp()
        )

    #注册方式不为POST
    def test_register_bad_method(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 405)

    #缺失参数
    def test_register_lack_params(self):
        response = self.client.post(reverse('register'))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], -2)
    
    #密码过长
    def test_register_long_password(self):
        data = {
            "username": "user",
            "email": self.valid_email,
            "password1": self.invalid_password,
            "password2": self.invalid_password,
            "verification_code": self.verification_code
        }
        response = self.client.post(
            reverse('register'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1001)
        self.assertEqual(data["msg"], "Password too long")
    
    #两次密码不一致
    def test_register_password_mismatch(self):
        data = {
            "username": "user",
            "email": self.valid_email,
            "password1": self.valid_password,
            "password2": "differentpassword",
            "verification_code": self.verification_code
        }
        response = self.client.post(
            reverse('register'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1002)
        self.assertEqual(data["msg"], "Password mismatch")

    #用户名已存在
    def test_register_username_exists(self):
        User.objects.create(
            username = "existuser",
            email = self.valid_email,
            password = self.valid_password
        )
        data = {
            "username": "existuser",
            "email": self.valid_email,
            "password1": self.valid_password,
            "password2": self.valid_password,
            "verification_code": self.verification_code
        }
        response = self.client.post(
            reverse('register'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1003)
        self.assertEqual(data["msg"], "Username already exists")

    #邮箱已存在
    def test_register_email_exists(self):
        User.objects.create(
            username = "user",
            email = self.valid_email,
            password = self.valid_password
        )
        data = {
            "username": "newuser",
            "email": self.valid_email,
            "password1": self.valid_password,
            "password2": self.valid_password,
            "verification_code": self.verification_code
        }
        response = self.client.post(
            reverse('register'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1004)
        self.assertEqual(data["msg"], "Email already exists")
    
    #邮箱不是清华邮箱
    def test_register_invalid_email(self):
        data = {
            "username": "user",
            "email": self.invalid_email,
            "password1": self.valid_password,
            "password2": self.valid_password,
            "verification_code": self.verification_code
        }
        response = self.client.post(
            reverse('register'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1005)
        self.assertEqual(data["msg"], "Please use Tsinghua email address")
    
    #邮箱未验证
    def test_register_unverified_email(self):
        EmailVerification.objects.filter(email=self.valid_email).delete()
        data = {
            "username": "user",
            "email": self.valid_email,
            "password1": self.valid_password,
            "password2": self.valid_password,
            "verification_code": self.verification_code
        }
        response = self.client.post(
            reverse('register'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1006)
        self.assertEqual(data["msg"], "Unverified email")
    
    #验证码错误
    def test_register_invalid_verification_code(self):
        data = {
            "username": "user",
            "email": self.valid_email,
            "password1": self.valid_password,
            "password2": self.valid_password,
            "verification_code": "654321"
        }
        response = self.client.post(
            reverse('register'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1007)
        self.assertEqual(data["msg"], "Invalid verification code")
    
    #验证码过期
    def test_register_verification_code_expired(self):
        EmailVerification.objects.filter(email=self.valid_email).update(created_at=utils_time.get_timestamp()-601)
        data = {
            "username": "user",
            "email": self.valid_email,
            "password1": self.valid_password,
            "password2": self.valid_password,
            "verification_code": self.verification_code
        }
        response = self.client.post(
            reverse('register'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1008)
        self.assertEqual(data["msg"], "Verification code expired")
    
    #注册成功
    def test_register_success(self):
        data = {
            "username": "user",
            "email": self.valid_email,
            "password1": self.valid_password,
            "password2": self.valid_password,
            "verification_code": self.verification_code
        }
        response = self.client.post(
            reverse('register'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["msg"], "Register successfully")

class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = VALID_EMAIL
        self.wrong_email = "wronguser@mails.tsinghua.edu.cn"
        self.password = VALID_PASSWORD
        self.wrong_password = "differentpassword"
        User.objects.create(
            username = "user",
            email = self.email,
            password = make_password(self.password)
        )
    
    #登录方式不为POST
    def test_login_bad_method(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 405)
    
    #缺失参数
    def test_login_lack_params(self):
        response = self.client.post(reverse('login'))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], -2)
    
    #用户不存在
    def test_login_user_not_exists(self):
        data = {
            "username": "wronguser",
            "password": self.password
        }
        response = self.client.post(
            reverse('login'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1009)
        self.assertEqual(data["msg"], "User not found")
    
    #密码错误
    def test_login_wrong_password(self):
        data = {
            "username": "user",
            "password": self.wrong_password
        }
        response = self.client.post(
            reverse('login'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1010)
        self.assertEqual(data["msg"], "Wrong password")

    #登录成功
    def test_login_success(self):
        data = {
            "username": "user",
            "password": self.password
        }
        response = self.client.post(
            reverse('login'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["msg"], "Login successfully")
