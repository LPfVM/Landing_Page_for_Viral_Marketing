from rest_framework import serializers

from apps.account.models import Account


class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "password",
            "bank_name",
            "account_number",
            "balance",
            "account_type",
        ]

        read_only_fields = ["id"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

class AccountDetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Account
        fields = [
            "id",
            "user_id",
            "bank_name",
            "account_number",
            "balance",
            "account_type",
        ]