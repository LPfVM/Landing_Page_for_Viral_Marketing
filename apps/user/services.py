from django.contrib.auth import get_user_model
from django.core.signing import (
    TimestampSigner,
    dumps,
    loads,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from utils.email import send_email

User = get_user_model()


def send_verification_email(user, request):
    signer = TimestampSigner()
    signed_user_email = signer.sign(user.email)
    signer_dump = dumps(signed_user_email)

    url = f"{request.scheme}://{request.get_host()}/users/verify/?code={signer_dump}"
    subject = "[Landing_page_for_Viral_Marketing] 이메일 인증을 완료해주세요"
    message = f"다음 링크를 클릭해주세요 {url}"
    send_email(subject, message, user.email)


def verify_email_code(code):
    signer = TimestampSigner()
    decoded_user_email = loads(code)
    email = signer.unsign(decoded_user_email, max_age=60 * 30)
    return email


def activate_email_user(email):
    user = get_object_or_404(User, email=email, is_active=False)
    user.is_active = True
    user.save()
    return user


def deactivate_user(user):
    user.is_active = False
    user.save()


def res_tokens(user):
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    return refresh, access


def set_refresh_to_cookie(response, refresh_token):
    response.set_cookie(
        key="refresh_token",
        value=str(refresh_token),
        httponly=True,
        samesite="Strict",
        # secure=True,
        # https 에서만 사용가능하게하는 옵션
    )

    return response


def get_user_or_404(pk, request):
    user = get_object_or_404(User, pk=pk)
    if request.user != user:
        raise PermissionDenied("권환 없음")
    return user


def user_logout(request):
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        raise ValueError("refresh 토큰이 없습니다.")
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError as e:
        raise ValueError("유효하지 않은 토큰 입니다.") from e


def refresh_access_token(request):
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        raise ValueError("refresh 토큰이 없습니다.")
    try:
        refresh = RefreshToken(refresh_token)
        return str(refresh.access_token)
    except TokenError as e:
        raise ValueError("유효하지 않은 토큰입니다.") from e
