from datetime import date, timedelta

from celery import shared_task
from django.contrib.auth import get_user_model

from .models import Analysis
from .services import AnalysisService

User = get_user_model()


@shared_task
def run_weekly_analysis():
    today = date.today()
    period_end = today - timedelta(days=1)
    period_start = period_end - timedelta(days=6)

    for user in User.objects.filter(is_active=True):
        for about in [Analysis.AboutChoices.INCOME, Analysis.AboutChoices.EXPENSE]:
            AnalysisService(
                user=user,
                about=about,
                type_of_time=Analysis.TypeOfTimeChoices.WEEKLY,
                period_start=period_start,
                period_end=period_end,
            ).run()


@shared_task
def run_monthly_analysis():
    today = date.today()
    period_end = today.replace(day=1) - timedelta(days=1)
    period_start = period_end.replace(day=1)
    for user in User.objects.filter(is_active=True):
        for about in [Analysis.AboutChoices.INCOME, Analysis.AboutChoices.EXPENSE]:
            AnalysisService(
                user=user,
                about=about,
                type_of_time=Analysis.TypeOfTimeChoices.MONTHLY,
                period_start=period_start,
                period_end=period_end,
            ).run()
