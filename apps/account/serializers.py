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
        ]

        read_only_fields = ["id"]

    def create(self, validated_data):
        user = self.context["request"].user
        account = Account.objects.create(user=user, **validated_data)
        return account

    # 예외처리
    def validate_bank_name(self, value):
        if not value:
            raise serializers.ValidationError("은행명은 비워둘 수 없습니다.")
        return value

    def validate_account_number(self, value):
        if not value:
            raise serializers.ValidationError("계좌번호는 비워둘 수 없습니다. ")
        return value

    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("잔액은 0보다 작을 수 없습니다.")
        return value


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
        ]
