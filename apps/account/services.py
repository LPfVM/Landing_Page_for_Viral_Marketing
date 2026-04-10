from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.account.models import Account


def create_account(*, user, validated_data):
    account_number = validated_data["account_number"]

    if Account.objects.filter(account_number=account_number).exists():
        raise ValidationError("이미 존재하는 계좌번호입니다.")

    return Account.objects.create(user=user, **validated_data)


def get_account(*, user, pk):
    return get_object_or_404(Account, pk=pk, user=user)


def delete_account(*, user, pk):
    account = get_object_or_404(Account, pk=pk, user=user)
    account.delete()


def get_account_list(*, user):
    return Account.objects.filter(user=user).order_by("-id")
