from django.contrib import admin
from .models import EAProgram, UtilityAccessAccount


@admin.register(UtilityAccessAccount)
class UtilityAccessAccountAdmin(admin.ModelAdmin):
    list_display = ("account_number", "server_name", "ea_enabled", "is_active", "note", "created_at")
    list_filter = ("is_active", "ea_enabled", "server_name")
    search_fields = ("account_number", "server_name", "note")
    readonly_fields = ("created_at",)
    actions = ("enable_ea", "disable_ea")

    @admin.action(description="선택 계좌의 EA 이용 허용")
    def enable_ea(self, request, queryset):
        count = queryset.update(ea_enabled=True)
        self.message_user(request, f"{count}개 계좌의 EA 이용을 허용했습니다.")

    @admin.action(description="선택 계좌의 EA 이용 중지 (다음 초기화부터)")
    def disable_ea(self, request, queryset):
        count = queryset.update(ea_enabled=False)
        self.message_user(request, f"{count}개 계좌를 중지했습니다. 실행 중인 EA에는 다음 초기화부터 반영됩니다.")


@admin.register(EAProgram)
class EAProgramAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    readonly_fields = ("created_at",)
