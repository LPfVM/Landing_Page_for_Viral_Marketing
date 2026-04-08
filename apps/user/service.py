from django.contrib.auth import get_user_model
from django.core.signing import (
    TimestampSigner,
    dumps,
    loads,
)
from rest_framework.generics import get_object_or_404

from utils.email import send_email

User = get_user_model()


def send_verifi(user, request):
    signer = TimestampSigner()
    signed_user_email = signer.sign(user.email)
    signer_dump = dumps(signed_user_email)

    url = (
        f"{request.scheme}://{request.META['HTTP_HOST']}"
        f"/users/verify/?code={signer_dump}"
    )
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
