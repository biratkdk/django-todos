from django.db import models
from django.utils import timezone

from authentication.models import User
from helpers.models import TrackingModel


class Todo(TrackingModel):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    due_date = models.DateField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.is_completed and self.completed_at is None:
            self.completed_at = timezone.now()
        if not self.is_completed:
            self.completed_at = None
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return bool(
            self.due_date
            and not self.is_completed
            and self.due_date < timezone.localdate()
        )

    def __str__(self):
        return self.title
