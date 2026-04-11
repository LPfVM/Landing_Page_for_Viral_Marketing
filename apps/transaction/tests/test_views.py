from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.account.models import Account
from apps.transaction.models import Transaction

User = get_user_model()


class TestTransactionListCreateAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com",
            nickname="test",
            password="test_password",
            is_active=True,
        )
        self.account = Account.objects.create(
            user=self.user,
            password="account_password",
            bank_name="test_bank",
            account_number="111-111-111",
            balance=1,
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
        self.url = reverse(
            "transaction:list_create", kwargs={"account_id": self.account.pk}
        )
        self.client.force_authenticate(user=self.user)

    # 로그인되지 않은 유저가 get 요청을 보냈을 때 실패하는지
    def test_get_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 로그인되지 않은 유저가 post 요청을 보냈을 때 실패하는지
    def test_post_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # get 요청에 list serializer를 사용하는지
    def test_get_list_serializer(self):
        Transaction.objects.create(**self.data, account=self.account)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data["results"][0].keys()),
            {
                "id",
                "bank_name",
                "title",
                "category",
                "transaction_type",
                "transaction_amount",
            },
        )

    # post 요청에 detail serializer를 사용하는지
    def test_post_detail_serializer(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(response.data.keys()),
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

    # 본인 계좌의 트랜잭션만 가져오는지
    def test_get_only_own_transactions(self):
        Transaction.objects.create(**self.data, account=self.account)
        user = User.objects.create_user(
            email="test2@test.com",
            nickname="test2",
            password="test2_password",
            is_active=True,
        )
        account = Account.objects.create(
            user=user,
            password="account_password",
            bank_name="other_bank",
            account_number="222-222-222",
            balance=1,
            account_type="INCOME",
        )
        Transaction.objects.create(**self.data, account=account)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertNotEqual(account.bank_name, response.data["results"][0]["bank_name"])

    # 본인이 소유하지 않은 계죄로 get 요청을 보냈을 때 실패하는지
    def test_get_other_user_404(self):
        Transaction.objects.create(**self.data, account=self.account)
        user = User.objects.create_user(
            email="test2@test.com",
            nickname="test2",
            password="test2_password",
            is_active=True,
        )
        account = Account.objects.create(
            user=user,
            password="account_password",
            bank_name="other_bank",
            account_number="222-222-222",
            balance=1,
            account_type="INCOME",
        )
        url = reverse("transaction:list_create", kwargs={"account_id": account.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 트랜잭션 생성에 성공하는지
    def test_create_transaction(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(Transaction.objects.first().account, self.account)

    # 다른 유저 소유 계좌로 post 요청을 보냈을 때 실패하는지
    def test_post_other_user_account(self):
        user = User.objects.create_user(
            email="test2@test.com",
            nickname="test2",
            password="test2_password",
            is_active=True,
        )
        account = Account.objects.create(
            user=user,
            password="account_password",
            bank_name="other_bank",
            account_number="222-222-222",
            balance=1,
            account_type="INCOME",
        )
        url = reverse("transaction:list_create", kwargs={"account_id": account.pk})
        response = self.client.post(url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Transaction.objects.count(), 0)
