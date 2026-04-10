from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TransactionSerializer
from .services import TransactionService


class TransactionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            transaction = TransactionService.create_transaction(
                user=request.user, data=serializer.validated_data
            )
            return Response(
                TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
