import json
import sys

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from utilities.licensing import valid_account
from utilities.models import EAProgram, UtilityAccessAccount


class Command(BaseCommand):
    help = "표준 입력 JSON으로 기존 고객 계좌의 EA 이용 허용과 프로그램을 등록합니다."

    def handle(self, *args, **options):
        try:
            data = json.loads(sys.stdin.read(4097))
            if not isinstance(data, dict) or set(data) != {"account_number", "program_code", "program_name"}:
                raise ValueError()
            if not valid_account(data["account_number"]) or any(not isinstance(value, str) or not value.strip() for value in data.values()):
                raise ValueError()
            with transaction.atomic():
                account = UtilityAccessAccount.objects.select_for_update().get(account_number=data["account_number"], is_active=True)
                account.ea_enabled = True
                account.full_clean()
                program, _ = EAProgram.objects.get_or_create(code=data["program_code"], defaults={"name": data["program_name"], "is_active": True})
                program.name = data["program_name"]
                program.full_clean()
                program.save()
                account.save(update_fields=["ea_enabled"])
        except (ValueError, ValidationError, UtilityAccessAccount.DoesNotExist):
            raise CommandError("활성 등록 계좌와 유효한 프로그램 정보를 확인해 주세요.") from None
        self.stdout.write("계좌의 EA 이용 허용과 프로그램 등록을 완료했습니다.")
