from django.http import JsonResponse
from .models import Lecture

def lecture_list(request):
    lectures = Lecture.objects.all().order_by("-id")
    data = [
        {
            "id": l.id,
            "title": l.title,
            "description": l.description,
            "url": l.url,
        }
        for l in lectures
    ]
    return JsonResponse({"lectures": data})
