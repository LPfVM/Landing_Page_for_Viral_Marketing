from django.conf import settings
from django.db import models


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ("INCOME", "입금"),
        ("EXPENSE", "출금"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts"
    )
    password = models.CharField(max_length=128, blank=True, null=False)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"
