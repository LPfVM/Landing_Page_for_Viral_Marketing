from django.shortcuts import get_object_or_404

from apps.account.models import Account
from apps.transaction.models import Transaction


def get_transactions(account_id, user):
    account = get_object_or_404(Account, pk=account_id, user=user)
    return Transaction.objects.filter(account=account).select_related("account")


def get_account(account_id, user):
    return get_object_or_404(Account, pk=account_id, user=user)


def get_transaction(user, pk):
    queryset = Transaction.objects.select_related("account")
    return get_object_or_404(queryset, pk=pk, account__user=user)
