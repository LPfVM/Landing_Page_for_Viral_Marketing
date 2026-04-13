from django.conf import settings
from django.db import models


class Analysis(models.Model):
    class AboutChoices(models.TextChoices):
        INCOME = ("INCOME", "입금")
        EXPENSE = ("EXPENSE", "출금")

    class TypeOfTimeChoices(models.TextChoices):
        WEEKLY = ("weekly", "매주")
        MONTHLY = ("monthly", "매월")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analysis"
    )
    about = models.CharField(
        choices=AboutChoices, max_length=50, blank=True, default=""
    )
    type = models.CharField(
        choices=TypeOfTimeChoices, max_length=50, blank=True, default=""
    )
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    description = models.TextField()
    result_image = models.ImageField(upload_to="analysis/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.about} ({self.period_start} ~ {self.period_end})"
