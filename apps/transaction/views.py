from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from apps.transaction.serializers import (
    TransactionDetailSerializer,
    TransactionListSerializer,
)
from apps.transaction.services import get_account, get_transaction, get_transactions


@extend_schema(tags=["Transaction"])
class TransactionListSwaggerView(ListCreateAPIView):
    pass


@extend_schema(tags=["Transaction"])
class TransactionDetailSwaggerView(RetrieveUpdateDestroyAPIView):
    pass


class TransactionListCreateAPIView(TransactionListSwaggerView):
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


class TransactionDetailAPIView(TransactionDetailSwaggerView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionDetailSerializer

    def get_object(self):
        return get_transaction(self.request.user, self.kwargs["pk"])
