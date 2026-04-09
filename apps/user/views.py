from django.contrib.auth import get_user_model
from django.core.signing import (
    BadSignature,
    SignatureExpired,
)
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
    UserSignUPSerializer,
)
from .service import (
    activate_email_user,
    deactivate_user,
    send_verification_email,
    verify_email_code,
)

User = get_user_model()


class UserSignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSignUPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user, request)
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
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        user = get_object_or_404(User, pk=pk)
        if self.request.user != user:
            raise PermissionDenied("권환 없음")
        return user

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


class UserLogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"message": "유효하지 않은 토큰 입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "message": "로그아웃 되었습니다.",
            },
            status=status.HTTP_200_OK,
        )
