from django.conf import settings
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.transaction.models import Transaction

from ..account.models import Account
from .services import create_notification


# 유저가 새로 가입하면 notification 테이블에 가입 메시지 저장.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def notify_on_user_created(sender, instance, created, **kwargs):
    if not created:
        return
    create_notification(
        user=instance,
        message="가입을 환영합니다! 🎉",
    )


# 거래내역 테이블에 새 데이터가 저장되면 결제, 입금 메시지
@receiver(post_save, sender=Transaction)
def notify_on_transaction_created(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.account.user
    amount = f"{instance.transaction_amount:,}원"

    if instance.transaction_type == "EXPENSE":
        message = f"{amount}이 결제되었습니다. 💸"

    else:  # INCOME
        message = f"{amount}이 입금되었습니다. 💰"

    create_notification(user=user, message=message)


# 거래내역에서 발생한 금액만큼 account 테이블의 balance 변화
@receiver(post_save, sender=Transaction)
def update_account_balance(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.transaction_type == "INCOME":
        Account.objects.filter(pk=instance.account_id).update(
            balance=F("balance") + instance.transaction_amount
        )
    else:  # EXPENSE
        Account.objects.filter(pk=instance.account_id).update(
            balance=F("balance") - instance.transaction_amount
        )
