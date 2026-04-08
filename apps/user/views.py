from django.contrib.auth import get_user_model, login
from django.core.signing import (
    BadSignature,
    SignatureExpired,
)
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
    UserSignUPSerializer,
)
from .service import (
    activate_email_user,
    deactivate_user,
    send_verifi,
    verify_email_code,
)

User = get_user_model()


class UserSignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSignUPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verifi(user, request)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"message": "email 인증 링크를 발송했습니다."},
            status=status.HTTP_201_CREATED,
        )


class EmailVerifyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get("code", None)
        try:
            email = verify_email_code(code)
        except (TypeError, SignatureExpired, BadSignature):
            return Response(
                {"message": "유효하지 않은 인증 링크입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        activate_email_user(email)

        return Response(
            {"message": "회원가입이 성공적으로 완료되었습니다."},
            status=status.HTTP_200_OK,
        )


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            return Response({"message": "로그인 성공"})
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserProfileView(APIView):
    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    def get(self, request, pk):
        user = self.get_object(pk=pk)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(pk=pk)
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk=pk)
        deactivate_user(user)

        return Response(
            {"message": "Deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
