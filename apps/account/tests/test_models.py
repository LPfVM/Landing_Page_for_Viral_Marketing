from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import DataError, IntegrityError
from django.test import TestCase

from apps.account.models import Account

User = get_user_model()


class TestAccount(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="tests@tests.com", nickname="tests", password="test_password"
        )
        self.user.is_active = True
        self.user.save()
        self.data = {
            "user": self.user,
            "password": "account_password",
            "bank_name": "test_bank",
            "account_number": "111-111-111",
            "balance": 1,
            "account_type": "INCOME",
        }

    # 계좌 생성 테스트
    def test_create_account(self):
        self.assertEqual(Account.objects.count(), 0)
        account = Account.objects.create(**self.data)
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(account.user, self.data["user"])
        self.assertEqual(account.password, self.data["password"])
        self.assertEqual(account.bank_name, self.data["bank_name"])
        self.assertEqual(account.account_number, self.data["account_number"])
        self.assertEqual(account.balance, self.data["balance"])
        self.assertEqual(account.account_type, self.data["account_type"])

    # 유저가 삭제됐을 때 account가 삭제되는지 테스트
    def test_CASCADE(self):
        Account.objects.create(**self.data)
        self.user.delete()
        self.assertEqual(Account.objects.count(), 0)

    # related_name이 잘 작동하는지
    def test_related_name(self):
        account = Account.objects.create(**self.data)
        account.refresh_from_db()
        self.assertEqual(self.user.accounts.first(), account)

    # 패스워드에 빈 값을 넣었을 때 동작하는지 테스트
    def test_blank_password(self):
        self.data["password"] = ""
        account = Account.objects.create(**self.data)
        account.refresh_from_db()
        self.assertEqual(account.password, "")

    # 동일한 계좌번호로 계좌 생성 시도할 시 에러가 나는지
    def test_unique_account_number(self):
        Account.objects.create(**self.data)
        with self.assertRaises(IntegrityError):
            Account.objects.create(**self.data)

    # max_digits 조건을 어기면 에러가 발생하는지
    def test_max_digits(self):
        self.data["balance"] = 10000000000.00
        with self.assertRaises(DataError):
            Account.objects.create(**self.data)

    # decimal_places 조건이 잘 작동하는지
    def test_decimal_places(self):
        self.data["balance"] = 1.009
        account = Account.objects.create(**self.data)
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("1.01"))

    # default 조건이 잘 작동하는지
    def test_default(self):
        self.data.pop("balance")
        account = Account.objects.create(**self.data)
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("0"))

    # choices 조건을 어겼을 때 에러가 발생하는지
    def test_choices(self):
        self.data["account_type"] = "NOT_INCOME"
        account = Account.objects.create(**self.data)
        with self.assertRaises(ValidationError):
            account.full_clean()
