from django.contrib.auth import get_user_model
from django.core.signing import (
    BadSignature,
    SignatureExpired,
)
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenVerifyView,
)

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


@extend_schema(tags=["User"])
class UserSwaggerView(APIView):
    pass


@extend_schema(tags=["Auth"])
class AuthSwaggerView(APIView):
    pass


@extend_schema(tags=["Auth"])
class CustomTokenVerifyView(TokenVerifyView):
    pass


class UserSignUpView(UserSwaggerView):
    permission_classes = [AllowAny]

    @extend_schema(request=UserSignUPSerializer)
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


class EmailVerifyView(UserSwaggerView):
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


class UserLoginView(AuthSwaggerView):
    permission_classes = [AllowAny]

    @extend_schema(request=UserLoginSerializer)
    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            response = Response(
                {
                    "access": str(refresh.access_token),
                }
            )
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                samesite="Strict",
                # secure=True,
                # https 에서만 사용가능하게하는 옵션
            )
            return response
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserProfileView(UserSwaggerView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        user = get_object_or_404(User, pk=pk)
        if self.request.user != user:
            raise PermissionDenied("권환 없음")
        return user

    @extend_schema(responses=UserProfileSerializer)
    def get(self, request, pk):
        user = self.get_object(pk=pk)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    @extend_schema(request=UserProfileSerializer)
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


class UserLogoutView(AuthSwaggerView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        # refresh가 None이거나 빈 문자열일 때 통과가 돼서 추가함
        if not refresh_token:
            return Response(
                {"message": "refresh 토큰이 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
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


class UserRefreshTokenView(AuthSwaggerView):
    # refresh token 테스트 코드
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"message": "refresh 토큰이 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            refresh = RefreshToken(refresh_token)
            return Response({"access": str(refresh.access_token)})
        except TokenError:
            return Response(
                {"message": "유효하지 않은 토큰입니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
