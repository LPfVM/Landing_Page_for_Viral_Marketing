from django.db import models


class Transaction(models.Model):
    # 거래 유형 정의
    TRANSACTION_TYPES = [
        ("INCOME", "수입"),
        ("EXPENSE", "지출"),
    ]

    # account 앱의 Account 모델과 연결 (문자열 참조로 순환 참조 방지)
    account = models.ForeignKey(
        "account.Account", on_delete=models.CASCADE, related_name="transactions"
    )

    # 기본 정보
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # 분류용 필드 추가
    category = models.CharField(max_length=50, blank=True, verbose_name="카테고리")

    # 거래 유형 및 금액
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPES, default="EXPENSE"
    )

    # 금액
    transaction_amount = models.IntegerField(verbose_name="거래 금액")

    transaction_date = models.DateField(verbose_name="거래 일자")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-transaction_date", "-created_at"]

    def __str__(self):
        amount_with_comma = format(self.transaction_amount, ",")
        return (
            f"[{self.get_transaction_type_display()}] "
            f"{self.title} - {amount_with_comma}원"
        )
