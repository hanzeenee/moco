from django.db import models


class NavLink(models.Model):
    """
    상단바 단순 링크용 (home/youtube/cafe/ea/pt)
    """
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

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.title} ({self.key})"


class Lecture(models.Model):
    """
    강의: 제목/설명/url
    """
    title = models.CharField(max_length=50, verbose_name="강의 제목")
    description = models.TextField(verbose_name="강의 설명")
    url = models.URLField(unique=True, verbose_name="강의 URL")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "id"]

    def __str__(self):
        return self.title


class Quiz(models.Model):
    """
    강의 1개당 퀴즈 1개 (문항 4개)
    """
    lecture = models.OneToOneField(
        Lecture,
        on_delete=models.CASCADE,
        related_name="quiz",
        verbose_name="강의",
    )

    question_1 = models.TextField(verbose_name="문항 1")
    question_2 = models.TextField(verbose_name="문항 2")
    question_3 = models.TextField(verbose_name="문항 3")
    question_4 = models.TextField(verbose_name="문항 4")

    def __str__(self):
        return f"{self.lecture.title} 퀴즈"


class Event(models.Model):
    """
    이벤트: event1 / event2 (상세 컬럼은 추후 확장)
    """
    KEY_CHOICES = [
        ("event1", "Event 1"),
        ("event2", "Event 2"),
    ]

    key = models.CharField(max_length=20, choices=KEY_CHOICES, unique=True)
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)  # 필요 없으면 나중에 삭제 가능
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.get_key_display()}"