from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from apps.transaction.serializers import (
    TransactionDetailSerializer,
    TransactionListSerializer,
)
from apps.transaction.services import get_account, get_transaction, get_transactions


class TransactionListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TransactionListSerializer
        return TransactionDetailSerializer

    def get_queryset(self):
        account_id = self.kwargs.get("account_id")
        return get_transactions(account_id, self.request.user)

    def perform_create(self, serializer):
        account_id = self.kwargs.get("account_id")
        account = get_account(account_id, self.request.user)
        serializer.save(account=account)


class TransactionDetailAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionDetailSerializer

    def get_object(self):
        return get_transaction(self.request.user, self.kwargs["pk"])
