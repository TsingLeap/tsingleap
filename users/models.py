import secrets, string
from django.db import models
from django.contrib.auth.models import AbstractUser

from utils.utils_require import MAX_CHAR_LENGTH
from utils import utils_time

# Create your models here.

class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    verification_code = models.CharField(max_length=6)  # 6 位验证码
    created_at = models.FloatField(default=utils_time.get_timestamp)  # 生成时间
    
    @staticmethod
    def generate_verification_code():
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))

class User(models.Model):
    id = models.BigAutoField(primary_key=True) # 主键
    username = models.CharField(max_length=MAX_CHAR_LENGTH, unique=True) # 用户名
    nickname = models.CharField(max_length=MAX_CHAR_LENGTH) # 昵称
    password = models.CharField(max_length=MAX_CHAR_LENGTH) # 密码
    email = models.EmailField(unique=True) # 邮箱

    def __str__(self):
        return f"{self.username} ({self.nickname})"
