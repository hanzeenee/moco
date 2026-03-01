from django.contrib import admin
from .models import NavLink, Lecture, Quiz, Event

admin.site.register(NavLink)
admin.site.register(Lecture)
admin.site.register(Quiz)
admin.site.register(Event)