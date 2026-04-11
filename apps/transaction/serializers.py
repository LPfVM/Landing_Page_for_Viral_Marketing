from rest_framework import serializers

from apps.transaction.models import Transaction


# 리스트 조회용 시리얼라이저
class TransactionListSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source="account.bank_name", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "bank_name",
            "title",
            "category",
            "transaction_type",
            "transaction_amount",
        ]


# 상세, 생성, 수정 시리얼라이저
class TransactionDetailSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source="account.bank_name", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "bank_name",
            "title",
            "description",
            "category",
            "transaction_type",
            "transaction_amount",
            "transaction_date",
        ]
