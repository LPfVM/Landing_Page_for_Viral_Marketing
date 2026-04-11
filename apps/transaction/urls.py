from django.urls import path

from apps.transaction.views import TransactionListCreateAPIView

app_name = "transaction"

urlpatterns = [
    path(
        "accounts/<int:account_id>/transcations/",
        TransactionListCreateAPIView.as_view(),
        name="list_create",
    ),
]
