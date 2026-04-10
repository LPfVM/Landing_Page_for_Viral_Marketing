import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.account.models import Account
from apps.transaction.models import Transaction
from apps.transaction.serializers import TransactionSerializer

User = get_user_model()


class TestTransactionSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="tests@tests.com", nickname="tests", password="test_password"
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
            "account": self.account.pk,
            "title": "title",
            "description": "description",
            "category": "category",
            "transaction_type": "INCOME",
            "transaction_amount": 1,
            "transaction_date": "2026-04-08",
        }

    def test_is_valid(self):
        serializer = TransactionSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_validated_data(self):
        serializer = TransactionSerializer(data=self.data)
        serializer.is_valid()

        self.assertEqual(serializer.validated_data["account"], self.account)
        self.assertEqual(serializer.validated_data["title"], self.data["title"])
        self.assertEqual(
            serializer.validated_data["description"], self.data["description"]
        )
        self.assertEqual(serializer.validated_data["category"], self.data["category"])
        self.assertEqual(
            serializer.validated_data["transaction_type"], self.data["transaction_type"]
        )
        self.assertEqual(
            serializer.validated_data["transaction_amount"],
            self.data["transaction_amount"],
        )
        self.assertEqual(
            serializer.validated_data["transaction_date"], datetime.date(2026, 4, 8)
        )

    def test_save(self):
        serializer = TransactionSerializer(data=self.data)
        serializer.is_valid()
        transaction = serializer.save()
        transaction.refresh_from_db()
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(transaction.account, self.account)
        self.assertEqual(transaction.title, self.data["title"])
        self.assertEqual(transaction.description, self.data["description"])
        self.assertEqual(transaction.category, self.data["category"])
        self.assertEqual(transaction.transaction_type, self.data["transaction_type"])
        self.assertEqual(
            transaction.transaction_amount, self.data["transaction_amount"]
        )
        self.assertEqual(transaction.transaction_date, datetime.date(2026, 4, 8))

    def test_serializer_data(self):
        serializer = TransactionSerializer(data=self.data)
        serializer.is_valid()
        serializer.save()
        self.assertEqual(serializer.data["account"], self.account.pk)
        self.assertEqual(serializer.data["title"], self.data["title"])
        self.assertEqual(serializer.data["description"], self.data["description"])
        self.assertEqual(serializer.data["category"], self.data["category"])
        self.assertEqual(
            serializer.data["transaction_type"], self.data["transaction_type"]
        )
        self.assertEqual(
            serializer.data["transaction_amount"], self.data["transaction_amount"]
        )
        self.assertEqual(
            serializer.data["transaction_date"], self.data["transaction_date"]
        )
