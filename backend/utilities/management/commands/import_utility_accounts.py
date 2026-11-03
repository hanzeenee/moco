import csv
import io
import sys

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from utilities.licensing import valid_account
from utilities.models import UtilityAccessAccount


class Command(BaseCommand):
    help = "표준 입력 UTF-8 CSV로 계좌를 일괄 추가/갱신합니다. 누락된 기존 계좌를 삭제하지 않습니다."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        text = sys.stdin.read(2_000_001).lstrip("\ufeff")
        if len(text) > 2_000_000:
            raise CommandError("CSV 크기는 2MB 이하여야 합니다.")
        reader = csv.DictReader(io.StringIO(text), strict=True)
        try:
            fields = set(reader.fieldnames or [])
        except csv.Error:
            raise CommandError("CSV 헤더 형식을 확인해 주세요.") from None
        if "account_number" not in fields or fields - {"account_number", "is_active", "ea_enabled", "note"}:
            raise CommandError("CSV 헤더에 account_number가 필요합니다. 선택 열은 is_active,ea_enabled,note입니다.")
        if len(reader.fieldnames) != len(fields):
            raise CommandError("CSV 헤더가 중복되었습니다.")
        rows = {}
        line = 2
        try:
            for line, row in enumerate(reader, start=2):
                if line > 20001 or None in row or any(value is None for value in row.values()):
                    raise ValueError()
                number = row["account_number"].strip()
                if not valid_account(number) or number in rows:
                    raise ValueError()
                updates = {}
                for field in ("is_active", "ea_enabled"):
                    if field in fields and row[field].strip():
                        value = row[field].strip().lower()
                        if value not in {"true", "false", "1", "0"}:
                            raise ValueError()
                        updates[field] = value in {"true", "1"}
                if "note" in fields:
                    updates["note"] = row["note"].strip()
                UtilityAccessAccount(account_number=number, **updates).full_clean(validate_unique=False)
                rows[number] = updates
        except (ValueError, ValidationError, csv.Error):
            raise CommandError(f"CSV {line}행의 값·중복·열 구성을 확인해 주세요. 저장하지 않았습니다.") from None
        if not rows:
            raise CommandError("등록할 행이 없습니다.")
        if options["dry_run"]:
            self.stdout.write(f"검사 완료: {len(rows)}개 행. 저장하지 않았습니다.")
            return
        with transaction.atomic():
            existing = {item.account_number: item for item in UtilityAccessAccount.objects.filter(account_number__in=rows)}
            additions, changes = [], []
            for number, updates in rows.items():
                if number in existing:
                    obj = existing[number]
                    for key, value in updates.items():
                        setattr(obj, key, value)
                    changes.append(obj)
                else:
                    additions.append(UtilityAccessAccount(account_number=number, **updates))
            UtilityAccessAccount.objects.bulk_create(additions, batch_size=250)
            UtilityAccessAccount.objects.bulk_update(changes, ["is_active", "ea_enabled", "note"], batch_size=100)
        self.stdout.write(f"일괄 등록 완료: 추가 {len(additions)}개, 갱신 {len(changes)}개.")
