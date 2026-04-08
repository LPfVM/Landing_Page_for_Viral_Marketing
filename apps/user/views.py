from django.contrib.auth import get_user_model, login
from django.core.signing import (
    BadSignature,
    SignatureExpired,
    TimestampSigner,
    dumps,
    loads,
)
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.email import send_email

from .serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
    UserSignUPSerializer,
)

User = get_user_model()


class UserSignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSignUPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            signer = TimestampSigner()
            signed_user_email = signer.sign(user.email)
            signer_dump = dumps(signed_user_email)

            url = (
                f"{self.request.scheme}://{self.request.META['HTTP_HOST']}"
                f"/users/verify/?code={signer_dump}"
            )
            subject = "[Landing_page_for_Viral_Marketing] 이메일 인증을 완료해주세요"
            message = f"다음 링크를 클릭해주세요 {url}"
            send_email(subject, message, user.email)
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
        signer = TimestampSigner()
        try:
            decoded_user_email = loads(code)
            email = signer.unsign(decoded_user_email, max_age=60 * 30)
        except (TypeError, SignatureExpired, BadSignature):
            return Response(
                {"message": "유효하지 않은 인증 링크입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = get_object_or_404(User, email=email, is_active=False)
        user.is_active = True
        user.save()
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
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
