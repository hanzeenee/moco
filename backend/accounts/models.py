from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string


def generate_referral_code():
    return get_random_string(
        10,
        allowed_chars="ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    )


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    name = models.CharField(max_length=50)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    bank_account = models.CharField(max_length=50, blank=True)

    is_paid_user = models.BooleanField(default=False)   # 회원/비회원
    quiz_completed = models.BooleanField(default=False)

    referral_code = models.CharField(
        max_length=10,
        unique=True,
        default=generate_referral_code,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"
