from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.account.serializers import AccountCreateSerializer, AccountDetailSerializer
from apps.account.services import (
    create_account,
    delete_account,
    get_account,
    get_account_list,
)


@extend_schema(tags=["Account"])
class AccountSwaggerView(APIView):
    pass


class AccountCreateView(AccountSwaggerView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AccountCreateSerializer)
    def post(self, request):
        serializer = AccountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account = create_account(
            user=request.user,
            validated_data=serializer.validated_data,
        )

        return Response(
            {
                "message": "계좌가 성공적으로 생성되었습니다.",
                "data": AccountDetailSerializer(account).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AccountDetailView(AccountSwaggerView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=AccountDetailSerializer)
    def get(self, request, pk):
        account = get_account(user=request.user, pk=pk)
        serializer = AccountDetailSerializer(account)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AccountDeleteView(AccountSwaggerView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        delete_account(user=request.user, pk=pk)
        return Response(
            {"message": "계좌가 성공적으로 삭제되었습니다."},
            status=status.HTTP_200_OK,
        )


class AccountListView(AccountSwaggerView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = get_account_list(user=request.user)
        serializer = AccountDetailSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
