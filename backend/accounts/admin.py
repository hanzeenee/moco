from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "phone_number",
        "is_paid_user",
        "quiz_completed",
        "referral_code",
    )
    search_fields = ("user__username", "name", "phone_number")
