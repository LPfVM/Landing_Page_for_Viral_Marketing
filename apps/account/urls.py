from django.urls import path

from apps.account.views import (
    AccountCreateView,
    AccountDeleteView,
    AccountDetailView,
    AccountListView,
)

app_name = "account"

urlpatterns = [
    path("create/", AccountCreateView.as_view(), name="create"),
    path("<int:pk>/detail/", AccountDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", AccountDeleteView.as_view(), name="delete"),
    path("list/", AccountListView.as_view(), name="list"),
]
