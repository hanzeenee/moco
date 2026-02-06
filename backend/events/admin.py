from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "title", "is_active", "order")
    list_filter = ("event_type", "is_active")
    ordering = ("event_type", "order")
