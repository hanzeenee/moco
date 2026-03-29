from django.contrib import admin
from .models import NavLink, Lecture, Quiz, Event, Comment


@admin.register(NavLink)
class NavLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "title", "url", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("key", "title", "url")
    ordering = ("order", "id")


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "url", "created_at")
    search_fields = ("title", "description", "url")
    ordering = ("-created_at", "id")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "lecture")
    search_fields = ("lecture__title",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "title", "url", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("key", "title", "description", "url")
    ordering = ("order", "id")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "lecture_id", "author_name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("author_name", "content")
    ordering = ("-created_at", "id")