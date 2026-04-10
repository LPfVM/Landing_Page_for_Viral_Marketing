import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.account.models import Account
from apps.transaction.models import Transaction

User = get_user_model()


class TestTransaction(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", nickname="test", password="test_password"
        )
        self.account = Account.objects.create(
            user=self.user,
            password="account_password",
            bank_name="test_bank",
            account_number="test_account_number",
            balance=1000000,
            account_type="INCOME",
        )
        self.data = {
            "account": self.account,
            "title": "test_title",
            "description": "test_description",
            "category": "test_category",
            "transaction_type": "INCOME",
            "transaction_amount": 1,
            "transaction_date": "2026-04-08",
        }

    # 생성 테스트
    def test_create_transaction(self):
        self.assertEqual(Transaction.objects.count(), 0)
        transaction = Transaction.objects.create(**self.data)
        transaction.refresh_from_db()
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(transaction.account, self.data["account"])
        self.assertEqual(transaction.title, self.data["title"])
        self.assertEqual(transaction.description, self.data["description"])
        self.assertEqual(transaction.category, self.data["category"])
        self.assertEqual(
            transaction.transaction_amount, self.data["transaction_amount"]
        )
        self.assertEqual(transaction.transaction_type, self.data["transaction_type"])
        self.assertEqual(
            str(transaction.transaction_date), self.data["transaction_date"]
        )
        self.assertEqual(transaction.transaction_date, datetime.date(2026, 4, 8))

    # CASCADE 테스트
    def test_CASCADE(self):
        Transaction.objects.create(**self.data)
        self.account.delete()
        self.assertEqual(Transaction.objects.count(), 0)

    # related_name 테스트
    def test_related_fields(self):
        transaction = Transaction.objects.create(**self.data)
        self.assertEqual(transaction.account, self.account)
        self.assertEqual(self.account.transactions.first(), transaction)

    # default 조건 테스트
    def test_default_fields(self):
        self.data.pop("transaction_type")
        transaction = Transaction.objects.create(**self.data)
        self.assertEqual(transaction.transaction_type, "EXPENSE")

    # 지정된 type 이외의 값을 넣었을 때 에러가 나는지
    def test_invalid_transaction_type(self):
        self.data["transaction_type"] = "FAKEINCOME"
        transaction = Transaction.objects.create(**self.data)
        with self.assertRaises(ValidationError):
            transaction.full_clean()

    # blank=True 테스트
    def test_blank_true_fields(self):
        self.data.pop("category")
        transaction = Transaction.objects.create(**self.data)
        self.assertEqual(transaction.category, "")

    # IntegerField가 float을 어떻게 취급하는지
    def test_integer_fields(self):
        self.data["transaction_amount"] = 1.9
        transaction = Transaction.objects.create(**self.data)
        transaction.refresh_from_db()
        self.assertEqual(transaction.transaction_amount, 1)
