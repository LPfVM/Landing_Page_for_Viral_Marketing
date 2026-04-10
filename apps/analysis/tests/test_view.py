from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.account.models import Account
from apps.analysis.models import Analysis
from apps.transaction.models import Transaction

User = get_user_model()


class AnalysisViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nickname="test",
            email="test@etest.com",
            password="testpassword",
            is_active=True,
        )
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

        self.account = Account.objects.create(
            user=self.user,
            bank_name="test_bank",
            account_number="111-222-333",
            account_type="INCOME",
        )
        self.transaction = Transaction.objects.create(
            account=self.account,
            title="test_title",
            transaction_amount=10000,
            transaction_type="INCOME",
            transaction_date="2026-04-09",
        )
        self.data = {
            "user": self.user,
            "about": "INCOME",
            "type": "weekly",
            "description": "테스트 분석",
            "period_start": "2026-04-05",
            "period_end": "2026-04-11",
            "result_image": "analysis/test.png",
        }

    def test_analysis_create(self):
        """그래프가 생성돼는지 확인"""
        post_data = {
            "about": "INCOME",
            "period_type": "weekly",
            "period_start": "2026-04-05",
            "period_end": "2026-04-11",
        }
        url = reverse("analysis_create")
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_analysis_list(self):
        """생성된 그래프들의 리스트 모음"""
        self.analysis = Analysis.objects.create(**self.data)

        url = reverse("analysis_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_analysis_get(self):
        """생성된 그래프 확인"""
        self.analysis = Analysis.objects.create(**self.data)
        url = reverse("analysis_detail", kwargs={"pk": self.analysis.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("result_image", response.data)
        self.assertTrue(response.data["result_image"])

    def test_analysis_invalid(self):
        """값이 유효하지 않았을떄"""
        post_data = {
            "about": "INVALID",
            "period_type": "weekly",
            "period_start": "2026-04-05",
            "period_end": "2026-04-11",
        }
        url = reverse("analysis_create")
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_analysis_create_no_transaction(self):
        post_data = {
            "about": "INCOME",
            "period_type": "weekly",
            "period_start": "2023-04-05",
            "period_end": "2023-04-11",
        }
        url = reverse("analysis_create")
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
