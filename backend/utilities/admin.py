from django.contrib import admin
from .models import UtilityAccessAccount


@admin.register(UtilityAccessAccount)
class UtilityAccessAccountAdmin(admin.ModelAdmin):
    list_display = ("account_number", "is_active", "note", "created_at")
    list_filter = ("is_active",)
    search_fields = ("account_number", "note")
    readonly_fields = ("created_at",)
