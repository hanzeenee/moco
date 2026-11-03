from django.core.validators import RegexValidator
from django.db import models

PROGRAM_PATTERN = r"^[a-z0-9][a-z0-9_-]{0,63}$"


class UtilityAccessAccount(models.Model):
    account_number = models.CharField(
        "인피녹스 계좌번호", max_length=20, unique=True,
        validators=[RegexValidator(r"^[0-9]{1,20}$", "계좌번호는 숫자만 입력해 주세요.")],
    )
    ea_enabled = models.BooleanField(
        "MT5 프로그램 이용 허용", default=True,
        help_text="등록된 활성 계좌는 활성화된 EA·지표 프로그램을 이용할 수 있습니다. 서버명 등록은 필요하지 않습니다.",
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


class EAProgram(models.Model):
    code = models.CharField("프로그램 ID", max_length=64, unique=True, validators=[RegexValidator(PROGRAM_PATTERN)])
    name = models.CharField("프로그램 이름", max_length=120)
    program_type = models.CharField("프로그램 종류", max_length=12, choices=[("ea", "EA"), ("indicator", "인디케이터")], default="ea")
    is_active = models.BooleanField("실행 허용", default=True)
    created_at = models.DateTimeField("등록일", auto_now_add=True)

    class Meta:
        verbose_name = "MT5 프로그램"
        verbose_name_plural = "MT5 프로그램"
        ordering = ["code"]

    def __str__(self):
        return self.name
