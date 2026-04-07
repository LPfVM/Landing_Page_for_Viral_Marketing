from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.views import APIView

from apps.account.models import Account
from apps.account.serializers import AccountCreateSerializer, AccountDetailSerializer


class AccountCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AccountCreateSerializer(
            data = request.data,
            context = {'request': request}
        )

        if serializer.is_valid():
            account = serializer.save()
            return Response(AccountCreateSerializer(account).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self,user,pk):
        return get_object_or_404(Account,pk=pk,user=user)

    def get(self, request,pk):
        account = self.get_object(request.user,pk)
        serializer = AccountDetailSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AccountDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self,user,pk):
        return get_object_or_404(Account,pk=pk,user=user)

    def delete(self,request,pk):
        account = self.get_object(request.user,pk)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AccountListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = Account.objects.filter(user=request.user).order_by("-id")
        serializer = AccountDetailSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

