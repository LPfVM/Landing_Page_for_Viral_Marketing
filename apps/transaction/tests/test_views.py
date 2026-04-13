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
        )
        url = reverse("transaction:list_create", kwargs={"account_id": account.pk})
        response = self.client.post(url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Transaction.objects.count(), 0)


class TestTransactionDetailAPIView(APITestCase):
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
        )
        self.data = {
            "title": "title",
            "description": "description",
            "category": "category",
            "transaction_type": "INCOME",
            "transaction_amount": 1,
            "transaction_date": "2026-04-08",
        }
        self.other_user = User.objects.create_user(
            email="test2@test.com",
            nickname="test2",
            password="test2_password",
            is_active=True,
        )
        self.other_account = Account.objects.create(
            user=self.other_user,
            password="account_password",
            bank_name="other_bank",
            account_number="222-222-222",
            balance=1,
        )
        self.transaction = Transaction.objects.create(**self.data, account=self.account)
        self.other_transaction = Transaction.objects.create(
            **self.data, account=self.other_account
        )
        self.url = reverse("transaction:detail", kwargs={"pk": self.transaction.pk})
        self.other_url = reverse(
            "transaction:detail", kwargs={"pk": self.other_transaction.pk}
        )
        self.client.force_authenticate(user=self.user)

    # 로그인되지 않은 유저가 get 요청을 보냈을 때 실패하는지
    def test_get_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 로그인되지 않은 유저가 post 요청을 보냈을 때 실패하는지
    def test_put_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.put(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 로그인되지 않은 유저가 delete 요청을 보냈을 때 실패하는지
    def test_delete_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_own_transaction_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.transaction.pk)
        self.assertEqual(response.data["bank_name"], self.account.bank_name)
        self.assertEqual(response.data["title"], self.transaction.title)
        self.assertEqual(response.data["description"], self.transaction.description)
        self.assertEqual(response.data["category"], self.transaction.category)
        self.assertEqual(
            response.data["transaction_type"], self.transaction.transaction_type
        )
        self.assertEqual(response.data["transaction_amount"], "1.00")
        self.assertEqual(
            response.data["transaction_date"], self.transaction.transaction_date
        )
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

    # 다른 사람의 트랜잭션에 접근했을 때 실패하는지
    def test_get_other_users_transaction_returns_404(self):
        response = self.client.get(self.other_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 없는 pk로 요청을 보냈을 때 에러가 나는지
    def test_get_nonexist_transaction_returns_404(self):
        url = reverse("transaction:detail", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 부분 수정이 잘 되는지
    def test_patch_own_transaction_returns_200(self):
        data = {
            "title": "title2",
        }
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.title, "title2")

    # 읽기 전용 필드가 잘 작동하는지
    def test_patch_read_only_fields_are_ignored(self):
        data = {"bank_name": "bank_name2", "id": 9999}
        response = self.client.patch(self.url, data=data)
        self.transaction.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bank_name"], self.transaction.account.bank_name)
        self.assertEqual(response.data["id"], self.transaction.pk)

    # 다른 사람의 트랜잭션에 patch 요청을 했을 때 에러가 나는지
    def test_patch_other_users_transaction_returns_404(self):
        data = {"title": "title"}
        response = self.client.patch(self.other_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # put 요청이 잘 되는지
    def test_put_own_transaction_returns_200(self):
        updated = {
            "title": "updated",
            "description": "updated",
            "category": "updated",
            "transaction_type": "EXPENSE",
            "transaction_amount": 2,
            "transaction_date": "2026-06-06",
        }
        response = self.client.put(self.url, updated)
        self.transaction.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.transaction.title, updated["title"])
        self.assertEqual(self.transaction.description, updated["description"])
        self.assertEqual(self.transaction.category, updated["category"])
        self.assertEqual(self.transaction.transaction_type, updated["transaction_type"])
        self.assertEqual(
            self.transaction.transaction_amount, updated["transaction_amount"]
        )
        self.assertEqual(
            str(self.transaction.transaction_date), updated["transaction_date"]
        )

    # 내 트랜잭션의 삭제가 잘 되는지
    def test_delete_own_transaction_returns_204(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Transaction.objects.filter(pk=self.transaction.pk).exists())

    # 다른 유저의 트랜잭션 삭제가 실패하는지
    def test_delete_other_users_transaction_returns_404(self):
        response = self.client.delete(self.other_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            Transaction.objects.filter(pk=self.other_transaction.pk).exists()
        )
