from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import TestCase

from apps.account.models import Account
from apps.transaction.models import Transaction
from apps.transaction.services import get_account, get_transaction, get_transactions

User = get_user_model()


class TestGetAccount(TestCase):
    def setUp(self):
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

    # get_account가 잘 작동하는지
    def test_get_account_success(self):
        account = get_account(self.account.pk, self.user)
        self.assertEqual(account, self.account)

    # 없는 account id로 조회를 했을 때 에러가 발생하는지
    def test_get_account_not_found(self):
        with self.assertRaises(Http404):
            get_account(99, self.user)

    # 어카운트 id가 빈 문자열일 경우 에러가 나는지
    def test_get_account_empty_id(self):
        with self.assertRaises(ValueError):
            get_account("", self.user)

    # 어카운트 id가 숫자가 아닐 경우 에러가 나는지
    def test_get_account_not_integer_id(self):
        with self.assertRaises(ValueError):
            get_account("abc", self.user)

    # 어카운트 id가 None인 경우 에러가 나는지
    def test_get_account_none_id(self):
        with self.assertRaises(Http404):
            get_account(None, self.user)

    # 작성자가 아닌 다른 유저가 접근한 경우 에러가 나는지
    def test_get_account_wrong_user(self):
        user = User.objects.create_user(
            email="test2@test.com",
            nickname="test2",
            password="test2_password",
            is_active=True,
        )
        with self.assertRaises(Http404):
            get_account(self.account.pk, user)


class TestGetTransactions(TestCase):
    def setUp(self):
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
        self.transaction1 = Transaction.objects.create(
            account=self.account, **self.data
        )
        self.transaction2 = Transaction.objects.create(
            account=self.account, **self.data
        )

    # 다른 유저가 거래내역 리스트에 접근했을 때 에러가 나는지
    def test_get_transactions_other_user_access(self):
        user = User.objects.create_user(
            email="test2@test.com",
            nickname="test2",
            password="test2_password",
            is_active=True,
        )
        with self.assertRaises(Http404):
            get_transactions(self.account.pk, user)

    # 어카운트 id가 none일 때 에러가 나는지
    def test_get_transactions_none_account_id(self):
        with self.assertRaises(Http404):
            get_transactions(None, self.user)

    # 어카운트 id가 빈 문자열일 때 에러가 나는지
    def test_get_transactions_empty_account_id(self):
        with self.assertRaises(ValueError):
            get_transactions("", self.user)

    # 어카운트 id에 숫자가 아닌 다른 값이 들어갔을 때 에러가 나는지
    def test_get_transactions_invalid_account_id(self):
        with self.assertRaises(ValueError):
            get_transactions("invalid", self.user)

    # 없는 어카운트 id를 넣었을 때 에러가 나는지
    def test_get_transactions_account_id_not_found(self):
        with self.assertRaises(Http404):
            get_transactions(999, self.user)

    # 거래내역 리스트가 의도한 데이터와 일치하는지
    def test_get_transactions_success(self):
        transactions = get_transactions(self.account.pk, self.user)
        self.assertEqual(transactions[0].id, self.transaction2.pk)
        self.assertEqual(
            transactions[0].account.bank_name, self.transaction2.account.bank_name
        )
        self.assertEqual(transactions[0].title, self.transaction2.title)
        self.assertEqual(transactions[0].category, self.transaction2.category)
        self.assertEqual(
            transactions[0].transaction_type, self.transaction2.transaction_type
        )
        self.assertEqual(
            transactions[0].transaction_amount, self.transaction2.transaction_amount
        )
        self.assertEqual(list(transactions), [self.transaction2, self.transaction1])


class TestGetTransaction(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            nickname="test",
            password="test_password",
            is_active=True,
        )
        self.user2 = User.objects.create_user(
            email="test2@test.com",
            nickname="test2",
            password="test2_password",
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
        self.transaction = Transaction.objects.create(account=self.account, **self.data)

    # transaction 가져오는 게 잘 성공하는지
    def test_get_own_transaction(self):
        transaction = get_transaction(self.user, self.transaction.pk)
        self.assertEqual(transaction, self.transaction)

    # 유저가 또다른 유저의 transaction에 접근할 때 에러가 나는지
    def test_other_user_access_fail(self):
        with self.assertRaises(Http404):
            get_transaction(self.user2, self.transaction.pk)

    # DB에 없는 pk로 쿼리를 보낼 때 에러가 나는지
    def test_transaction_not_found(self):
        with self.assertRaises(Http404):
            get_transaction(self.user, 9999)

    # pk를 빈 문자열로 보냈을 때 에러가 나는지
    def test_blank_pk(self):
        with self.assertRaises(ValueError):
            get_transaction(self.user, "")

    # pk를 None으로 보냈을 때 에러가 나는지
    def test_missing_pk(self):
        with self.assertRaises(Http404):
            get_transaction(self.user, None)

    # pk에 숫자가 아닌 값을 넣었을 때 에러가 나는지
    def test_invalid_pk(self):
        with self.assertRaises(ValueError):
            get_transaction(self.user, "invalid_pk")
