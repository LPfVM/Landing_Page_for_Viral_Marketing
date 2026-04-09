from django.urls import path

from apps.account.views import (
    AccountCreateView,
    AccountDeleteView,
    AccountDetailView,
    AccountListView,
)

app_name = "account"

urlpatterns = [
    path("accounts/create/", AccountCreateView.as_view(), name="create"),
    path("accounts/<int:pk>/detail/", AccountDetailView.as_view(), name="detail"),
    path("accounts/<int:pk>/delete/", AccountDeleteView.as_view(), name="delete"),
    path("accounts/list/", AccountListView.as_view(), name="list"),
]
