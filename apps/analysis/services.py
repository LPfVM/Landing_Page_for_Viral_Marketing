import io

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from django.core.files.base import ContentFile

from apps.transaction.models import Transaction

from .models import Analysis

matplotlib.use("Agg")  # 서버 환경에서 GUI 없이 실행
plt.rcParams["font.family"] = "AppleGothic"  # Mac 한글 폰트
plt.rcParams["axes.unicode_minus"] = False


class AnalysisService:
    TYPE_MAP = {
        Analysis.AboutChoices.INCOME: "INCOME",
        Analysis.AboutChoices.EXPENSE: "EXPENSE",
    }
    LABEL_MAP = {
        Analysis.AboutChoices.INCOME: "입금",
        Analysis.AboutChoices.EXPENSE: "출금",
    }

    def __init__(self, user, about, type_of_time, period_start, period_end):
        self.user = user
        self.about = about  # "income" or "expense"
        self.type_of_time = type_of_time  # "weekly" or "monthly"
        self.period_start = period_start
        self.period_end = period_end

    def _get_transactions(self):
        return Transaction.objects.filter(
            account__user=self.user,
            transaction_type=self.TYPE_MAP[self.about],
            transaction_date__range=(self.period_start, self.period_end),
        ).values("transaction_date", "transaction_amount")

    def _build_dataframe(self, transactions):
        df = pd.DataFrame(list(transactions))
        if df.empty:
            return df
        df["transaction_date"] = pd.to_datetime(df["transaction_date"])
        df = df.groupby("transaction_date")["transaction_amount"].sum().reset_index()
        return df

    def _build_graph(self, df):
        label = self.LABEL_MAP[self.about]
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.bar(
            df["transaction_date"].dt.strftime("%m-%d"),
            df["transaction_amount"],
            label=label,
        )
        ax.set_title(f"{self.period_start} ~ {self.period_end} {label} 분석")
        ax.set_xlabel("날짜")
        ax.set_ylabel("금액 (원)")
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        plt.close(fig)
        buffer.seek(0)
        return buffer

    def run(self):
        transactions = self._get_transactions()
        df = self._build_dataframe(transactions)

        if df.empty:
            return None

        buffer = self._build_graph(df)
        image_name = (
            f"analysis_{self.user.id}_{self.about}"
            f"_{self.period_start}_{self.period_end}.png"
        )
        label = self.LABEL_MAP[self.about]
        analysis = Analysis(
            user=self.user,
            about=self.about,
            type=self.type_of_time,
            period_start=self.period_start,
            period_end=self.period_end,
            description=f"{self.period_start} ~ {self.period_end} {label} 분석",
        )
        analysis.result_image.save(image_name, ContentFile(buffer.read()), save=True)
        return analysis
