from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.account.models import Account
from apps.analysis.tasks import run_monthly_analysis, run_weekly_analysis
from apps.transaction.models import Transaction

User = get_user_model()


class TestAnalysisTasks(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nickname="test",
            password="testpassword",
            email="test@test.com",
        )
        self.account = Account.objects.create(
            user=self.user,
            bank_name="test_bank",
            account_number="111-222-333",
        )
        self.transaction = Transaction.objects.create(
            account=self.account,
            title="test_title",
            transaction_amount=10000,
            transaction_type="INCOME",
            transaction_date="2026-04-09",
        )

    def test_task_weekly(self):
        run_weekly_analysis.run()

    def test_task_monthly(self):
        run_monthly_analysis.run()
