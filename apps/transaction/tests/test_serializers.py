import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.account.models import Account
from apps.transaction.models import Transaction
from apps.transaction.serializers import (
    TransactionDetailSerializer,
    TransactionListSerializer,
)

User = get_user_model()


class TestTransactionListSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", nickname="test", password="test_password"
        )
        self.account = Account.objects.create(
            user=self.user,
            password="account_password",
            bank_name="bank_name",
            account_number="account_number",
            balance=1000000,
            account_type="INCOME",
        )
        self.data = {
            "account": self.account,
            "title": "title",
            "description": "description",
            "category": "category",
            "transaction_type": "INCOME",
            "transaction_amount": 1,
            "transaction_date": "2026-04-08",
        }
        Transaction.objects.create(**self.data)
        Transaction.objects.create(**self.data)
        self.transactions = Transaction.objects.all().select_related("account")

    # 리스트에 표시될 정보들이 의도한 것과 일치하는지
    def test_list(self):
        serializer = TransactionListSerializer(instance=self.transactions, many=True)
        self.assertEqual(len(serializer.data), 2)
        self.assertEqual(serializer.data[0]["bank_name"], self.account.bank_name)
        self.assertEqual(serializer.data[0]["title"], self.data["title"])
        self.assertEqual(serializer.data[0]["category"], self.data["category"])
        self.assertEqual(
            serializer.data[0]["transaction_type"], self.data["transaction_type"]
        )
        self.assertEqual(serializer.data[0]["transaction_amount"], "1.00")
        self.assertEqual(
            set(serializer.data[0].keys()),
            {
                "id",
                "bank_name",
                "title",
                "category",
                "transaction_type",
                "transaction_amount",
            },
        )


class TestTransactionDetailSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", nickname="test", password="test_password"
        )
        self.account = Account.objects.create(
            user=self.user,
            password="account_password",
            bank_name="bank_name",
            account_number="account_number",
            balance=1000000,
            account_type="INCOME",
        )
        self.data = {
            "title": "title",
            "description": "description",
            "category": "category",
            "transaction_type": "INCOME",
            "transaction_amount": 1,
            "transaction_date": "2026-04-08",
        }

    # 데이터가 유효한지
    def test_create_valid_data(self):
        serializer = TransactionDetailSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    # read_only 조건이 잘 작동하는지
    def test_create_read_only_fields(self):
        self.data["id"] = 20
        serializer = TransactionDetailSerializer(data=self.data)
        serializer.is_valid()
        self.assertNotIn("id", serializer.validated_data)

    # 저장한 데이터가 의도한 것과 일치하는지
    def test_create_save(self):
        serializer = TransactionDetailSerializer(data=self.data)
        serializer.is_valid()
        transaction = serializer.save(account=self.account)
        transaction.refresh_from_db()
        self.assertEqual(transaction.title, self.data["title"])
        self.assertEqual(transaction.description, self.data["description"])
        self.assertEqual(transaction.category, self.data["category"])
        self.assertEqual(transaction.transaction_type, self.data["transaction_type"])
        self.assertEqual(transaction.transaction_amount, Decimal("1.00"))
        self.assertEqual(transaction.transaction_date, datetime.date(2026, 4, 8))

    # 조회용 데이터가 의도한 것과 일치하는지
    def test_get_serializer_data(self):
        transaction = Transaction.objects.create(**self.data, account=self.account)
        serializer = TransactionDetailSerializer(instance=transaction)
        self.assertEqual(
            serializer.data["bank_name"], self.account.bank_name
        )  # read_only 필드도 확인 가능
        self.assertEqual(serializer.data["title"], self.data["title"])
        self.assertEqual(serializer.data["description"], self.data["description"])
        self.assertEqual(serializer.data["category"], self.data["category"])
        self.assertEqual(
            serializer.data["transaction_type"], self.data["transaction_type"]
        )
        self.assertEqual(serializer.data["transaction_amount"], "1.00")
        self.assertEqual(serializer.data["transaction_date"], "2026-04-08")
        self.assertEqual(
            set(serializer.data.keys()),
            {
                "id",
                "bank_name",
                "title",
                "description",
                "category",
                "transaction_type",
                "transaction_amount",
                "transaction_date",
            },
        )

    # 전체 수정이 잘 작동하는지
    def test_update(self):
        transaction = Transaction.objects.create(**self.data, account=self.account)
        data = {
            "title": "title2",
            "description": "description2",
            "category": "category2",
            "transaction_type": "INCOME",
            "transaction_amount": 2,
            "transaction_date": "2026-04-09",
        }
        serializer = TransactionDetailSerializer(instance=transaction, data=data)
        serializer.is_valid()
        updated = serializer.save()
        updated.refresh_from_db()
        self.assertEqual(updated.title, data["title"])
        self.assertEqual(updated.description, data["description"])
        self.assertEqual(updated.category, data["category"])
        self.assertEqual(updated.transaction_type, data["transaction_type"])
        self.assertEqual(updated.transaction_amount, Decimal("2.00"))
        self.assertEqual(updated.transaction_date, datetime.date(2026, 4, 9))

    # 부분 수정이 잘 되는지
    def test_partial_update(self):
        transaction = Transaction.objects.create(**self.data, account=self.account)
        data = {
            "title": "title2",
        }
        serializer = TransactionDetailSerializer(
            instance=transaction, data=data, partial=True
        )
        serializer.is_valid()
        updated = serializer.save()
        updated.refresh_from_db()
        self.assertEqual(updated.title, data["title"])
        self.assertEqual(updated.description, self.data["description"])
        self.assertEqual(updated.category, self.data["category"])
        self.assertEqual(updated.transaction_type, self.data["transaction_type"])
        self.assertEqual(updated.transaction_amount, Decimal("1.00"))
        self.assertEqual(updated.transaction_date, datetime.date(2026, 4, 8))
