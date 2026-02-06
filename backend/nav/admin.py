from django.contrib import admin
from .models import NavLink

@admin.register(NavLink)
class NavLinkAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "url", "is_active", "order")
    list_editable = ("url", "is_active", "order")
    ordering = ("order",)
