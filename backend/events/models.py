from django.db import models

class Event(models.Model):
    class EventType(models.TextChoices):
        EVENT1 = "event1", "Event 1"
        EVENT2 = "event2", "Event 2"

    event_type = models.CharField(max_length=10, choices=EventType.choices)
    title = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.title or 'untitled'}"
