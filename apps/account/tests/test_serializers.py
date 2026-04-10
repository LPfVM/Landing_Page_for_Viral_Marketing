from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.account.models import Account
from apps.account.serializers import AccountCreateSerializer, AccountDetailSerializer

User = get_user_model()


class TestAccountCreateSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", nickname="test", password="test_password"
        )
        self.user.is_active = True
        self.user.save()
        request = APIRequestFactory().post("/")
        request.user = self.user
        self.context = {"request": request}
        self.data = {
            "password": "account_password",
            "bank_name": "bank_name",
            "account_number": "account_number",
            "balance": 1,
            "account_type": "INCOME",
        }

    # data가 valid한지
    def test_is_valid(self):
        serializer = AccountCreateSerializer(data=self.data, context=self.context)
        self.assertTrue(serializer.is_valid())

    # validated_data가 self.data와 같은지
    def test_validated_data(self):
        serializer = AccountCreateSerializer(data=self.data, context=self.context)
        serializer.is_valid()
        self.assertEqual(serializer.validated_data, self.data)

    # create의 결과가 의도한 바와 같은지
    def test_create(self):
        serializer = AccountCreateSerializer(data=self.data, context=self.context)
        serializer.is_valid()
        account = serializer.create(serializer.validated_data)
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(account.user, self.user)
        self.assertEqual(account.password, self.data["password"])
        self.assertEqual(account.bank_name, self.data["bank_name"])
        self.assertEqual(account.account_number, self.data["account_number"])
        self.assertEqual(account.balance, self.data["balance"])
        self.assertEqual(account.account_type, self.data["account_type"])

    # save()가 잘 되는지
    def test_save(self):
        serializer = AccountCreateSerializer(data=self.data, context=self.context)
        serializer.is_valid()
        serializer.save()
        self.assertEqual(Account.objects.count(), 1)


class TestAccountDetailSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", nickname="test", password="test_password"
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
        self.account = Account.objects.create(**self.data)

    # serializer_data(읽기용 데이터)가 의도한 것과 일치하는지
    def test_serializer_data(self):
        serializer = AccountDetailSerializer(instance=self.account)
        self.assertEqual(serializer.data["id"], self.account.pk)
        self.assertEqual(serializer.data["user_id"], self.account.user.pk)
        self.assertEqual(serializer.data["bank_name"], self.account.bank_name)
        self.assertEqual(serializer.data["account_number"], self.account.account_number)
        self.assertEqual(Decimal(serializer.data["balance"]), self.account.balance)
        self.assertEqual(serializer.data["account_type"], self.account.account_type)
