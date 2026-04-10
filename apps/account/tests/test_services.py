from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.account.models import Account
from apps.account.services import create_account, get_account

User = get_user_model()


class AccountServiceTest(TestCase):
    def setUp(self):
        # 1. 유저 생성
        self.user = User.objects.create_user(
            email="user1@example.com", nickname="회원1", password="password123"
        )
        self.other_user = User.objects.create_user(
            email="user2@example.com", nickname="회원2", password="password123"
        )

        # 2. Account 모델 필드에 맞춘 데이터
        self.account_data = {
            "bank_name": "파이썬은행",
            "account_number": "1234567890",
            "password": "account_password123",
            "account_type": "INCOME",
            "balance": 1000,
        }

    def test_create_account_success(self):
        """계좌 생성 서비스가 정상적으로 작동하는지 테스트"""
        account = create_account(user=self.user, validated_data=self.account_data)

        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(account.account_number, "1234567890")
        self.assertEqual(account.bank_name, "파이썬은행")
        self.assertEqual(account.user, self.user)

    def test_create_account_duplicate_fail(self):
        """중복된 계좌번호 생성 시 ValidationError가 발생하는지 테스트"""
        create_account(user=self.user, validated_data=self.account_data)

        with self.assertRaises(ValidationError) as cm:
            create_account(user=self.user, validated_data=self.account_data)

        self.assertEqual(cm.exception.detail[0], "이미 존재하는 계좌번호입니다.")

    def test_get_account_owner_only(self):
        """본인의 계좌는 조회 가능하지만, 남의 계좌는 404 에러가 나야 함"""
        account = create_account(user=self.user, validated_data=self.account_data)

        # 본인 조회 성공
        fetched_account = get_account(user=self.user, pk=account.pk)
        self.assertEqual(fetched_account, account)

        # 타인 조회 실패 (404)
        from django.http import Http404

        with self.assertRaises(Http404):
            get_account(user=self.other_user, pk=account.pk)
