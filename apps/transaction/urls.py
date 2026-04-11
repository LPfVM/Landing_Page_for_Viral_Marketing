from django.urls import path

from apps.transaction.views import TransactionListCreateAPIView

urlpatterns = [
    path(
        "accounts/<int:account_id>/transcations/",
        TransactionListCreateAPIView.as_view(),
    ),
]
