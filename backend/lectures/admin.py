from django.contrib import admin
from .models import Lecture, Quiz


class QuizInline(admin.StackedInline):
    model = Quiz
    extra = 0
    max_num = 1  # OneToOne 관계이므로 1개만
    can_delete = True
    fields = ("question_1", "question_2", "question_3", "question_4")


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "url", "has_quiz", "created_at")
    list_display_links = ("id", "title")
    search_fields = ("title", "url", "description")
    list_filter = ("created_at",)
    ordering = ("-id",)
    inlines = (QuizInline,)

    @admin.display(boolean=True, description="퀴즈")
    def has_quiz(self, obj):
        # related_name="quiz" 기준
        return hasattr(obj, "quiz")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "lecture", "lecture_url",)
    search_fields = ("lecture__title", "lecture__url", "question_1", "question_2", "question_3", "question_4")
    ordering = ("-id",)

    @admin.display(description="강의 URL")
    def lecture_url(self, obj):
        return obj.lecture.url
