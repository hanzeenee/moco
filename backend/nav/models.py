from django.db import models

class NavLink(models.Model):
    KEY_CHOICES = [
        ("home", "홈"),
        ("youtube", "유튜브"),
        ("cafe", "카페"),
        ("ea", "EA"),
        ("pt", "PT"),
    ]

    key = models.CharField(max_length=20, choices=KEY_CHOICES, unique=True)
    title = models.CharField(max_length=50)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.key})"
