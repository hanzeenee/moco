from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    name = models.CharField(max_length=50, verbose_name="이름")
    birth = models.CharField(max_length=6, verbose_name="생년월일 6자리")
    phone = models.CharField(max_length=20, verbose_name="휴대폰번호")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "id"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"
