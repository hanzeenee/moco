from django.core.validators import RegexValidator
from django.db import models


class UtilityAccessAccount(models.Model):
    account_number = models.CharField(
        "인피녹스 계좌번호", max_length=20, unique=True,
        validators=[RegexValidator(r"^[0-9]{1,20}$", "계좌번호는 숫자만 입력해 주세요.")],
    )
    is_active = models.BooleanField("이용 허용", default=True)
    note = models.CharField("관리 메모", max_length=200, blank=True)
    created_at = models.DateTimeField("등록일", auto_now_add=True)

    class Meta:
        verbose_name = "유틸리티 이용 계좌"
        verbose_name_plural = "유틸리티 이용 계좌"
        ordering = ["-created_at"]

    def __str__(self):
        return "등록 계좌 · " + self.account_number[-4:]
