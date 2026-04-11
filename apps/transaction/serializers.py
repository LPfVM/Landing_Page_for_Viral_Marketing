from rest_framework import serializers

from apps.transaction.models import Transaction


# 리스트 조회용 시리얼라이저
class TransactionListSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source="account.bank_name")

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
        read_only_fields = ["id", "bank_name"]


# 상세, 생성, 수정 시리얼라이저
class TransactionDetailSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source="account.bank_name")

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
        read_only_fields = ["id", "bank_name"]
