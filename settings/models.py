from django.db import models
from users.models import User

# Create your models here.
class UserPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.CharField(max_length=255)
    permission_info = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.permission} {self.permission_info}"