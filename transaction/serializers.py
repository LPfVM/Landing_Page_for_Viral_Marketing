from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "title",
            "description",
            "category",
            "transaction_type",
            "transaction_amount",
            "transaction_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at"]
