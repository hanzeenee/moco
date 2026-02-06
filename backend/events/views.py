from django.http import JsonResponse
from .models import Event

def event_list(request, event_type):
    qs = Event.objects.filter(event_type=event_type, is_active=True).order_by("order")
    data = [{"id": e.id, "title": e.title} for e in qs]
    return JsonResponse({"type": event_type, "items": data})
