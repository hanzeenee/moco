import re
import sys
from django.core.management.base import BaseCommand, CommandError
from utilities.models import UtilityAccessAccount


class Command(BaseCommand):
    help = "표준 입력으로 받은 계좌번호를 유틸리티 허용 목록에 등록합니다."

    def handle(self, *args, **options):
        number = sys.stdin.read().strip()
        if not re.fullmatch(r"[0-9]{1,20}", number):
            raise CommandError("유효한 계좌번호를 표준 입력으로 전달해 주세요.")
        UtilityAccessAccount.objects.update_or_create(account_number=number, defaults={"is_active": True, "ea_enabled": True})
        self.stdout.write("유틸리티 이용 계좌 등록을 완료했습니다.")
