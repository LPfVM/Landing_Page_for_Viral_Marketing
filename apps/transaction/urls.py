from django.urls import path

from .views import TransactionCreateView

urlpatterns = [
    path(
        "transactions/create/",
        TransactionCreateView.as_view(),
        name="transaction-create",
    ),
]
