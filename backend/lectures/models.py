from django.db import models


class Lecture(models.Model):
    title = models.CharField(
        max_length=20,
        verbose_name="강의 제목"
    )
    url = models.URLField(
        unique=True,
        verbose_name="강의 URL"
    )
    description = models.TextField(
        verbose_name="강의 설명"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class Quiz(models.Model):
    lecture = models.OneToOneField(
        Lecture,
        on_delete=models.CASCADE,
        related_name="quiz",
        verbose_name="강의"
    )

    question_1 = models.TextField(verbose_name="문항 1")
    question_2 = models.TextField(verbose_name="문항 2")
    question_3 = models.TextField(verbose_name="문항 3")
    question_4 = models.TextField(verbose_name="문항 4")

    def __str__(self):
        return f"{self.lecture.title} 퀴즈"
