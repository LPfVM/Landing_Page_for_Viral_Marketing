import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.account.models import Account
from apps.analysis.models import Analysis
from apps.transaction.models import Transaction

User = get_user_model()


class TestAnalysis(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nickname="test",
            email="test@test.com",
            password="testpassword",
            is_active=True,
        )
        self.account = Account.objects.create(
            user=self.user,
            bank_name="test_bank",
            account_number="111-222-333",
            balance=100000,
        )
        self.transaction = Transaction.objects.create(
            account=self.account,
            title="test_title",
            transaction_amount=10000,
            transaction_date=datetime.date(2026, 4, 9),
        )

    def test_create_analysis(self):
        analysis = Analysis.objects.create(
            user=self.user,
            about="INCOME",
            period_start=datetime.date(2026, 4, 8),
            period_end=datetime.date(2026, 4, 10),
            description="테스트 분석",
            result_image="analysis/test.png",
        )
        self.assertEqual(Analysis.objects.count(), 1)
        self.assertEqual(analysis.user, self.user)
        self.assertEqual(analysis.about, "INCOME")
        self.assertEqual(analysis.period_start, datetime.date(2026, 4, 8))
        self.assertEqual(analysis.period_end, datetime.date(2026, 4, 10))
        self.assertEqual(analysis.description, "테스트 분석")
