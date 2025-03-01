from django.db import models
from django.contrib.auth.models import User


class TaskStatus(models.TextChoices):
    TODO = "todo", "진행 전"
    IN_PROGRESS = "in_progress", "진행 중"
    DONE = "done", "완료"


class Task(models.Model):
    title = models.CharField(max_length=200, verbose_name="제목")
    description = models.TextField(blank=True, null=True, verbose_name="설명")
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO,
        verbose_name="상태",
    )
    priority = models.IntegerField(default=0, verbose_name="우선순위")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    due_date = models.DateField(blank=True, null=True, verbose_name="마감일")
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="assigned_tasks",
        verbose_name="담당자",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tasks",
        verbose_name="생성자",
    )

    class Meta:
        ordering = ["priority", "-created_at"]
        verbose_name = "업무"
        verbose_name_plural = "업무"

    def __str__(self):
        return self.title
