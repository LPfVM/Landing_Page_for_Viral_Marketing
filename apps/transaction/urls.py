from django.urls import path

from apps.transaction.views import (
    TransactionDetailAPIView,
    TransactionListCreateAPIView,
)

app_name = "transaction"

urlpatterns = [
    path(
        "accounts/<int:account_id>/transcations/",
        TransactionListCreateAPIView.as_view(),
        name="list_create",
    ),
    path("transactions/<int:pk>/", TransactionDetailAPIView.as_view(), name="detail"),
]
