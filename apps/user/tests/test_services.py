import re
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner, dumps
from django.test import TestCase
from freezegun import freeze_time
from rest_framework.test import APIRequestFactory

from apps.user.services import (
    activate_email_user,
    deactivate_user,
    send_verification_email,
    verify_email_code,
)

User = get_user_model()


class TestSendVerificationEmail(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", nickname="test", password="test_password"
        )
        self.request = APIRequestFactory().post("/")
        self.request.META["HTTP_HOST"] = self.request.get_host()

    # url이 의도한 것과 일치하는지
    def test_url(self):
        signer = TimestampSigner()
        signed_user_email = signer.sign(self.user.email)
        signer_dump = dumps(signed_user_email)
        url = (
            f"{self.request.scheme}://{self.request.META['HTTP_HOST']}"
            f"/users/verify/?code={signer_dump}"
        )
        self.assertEqual(url, f"http://testserver/users/verify/?code={signer_dump}")

    # 발송한 이메일의 수신자, 제목, 내용이 의도한 것과 일치하는지
    def test_send_verification_email(self):
        send_verification_email(self.user, self.request)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertEqual(
            mail.outbox[0].subject,
            "[Landing_page_for_Viral_Marketing] 이메일 인증을 완료해주세요",
        )
        self.assertIn("다음 링크를 클릭해주세요", mail.outbox[0].body)


class TestVerifyEmailCode(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", nickname="test", password="test_password"
        )
        signer = TimestampSigner()
        signed_user_email = signer.sign(self.user.email)
        self.code = dumps(signed_user_email)

    # verify_email_code의 반환값인 email이 발송한 email과 일치하는지
    def test_verify_email_code(self):
        email = verify_email_code(self.code)
        self.assertEqual(email, self.user.email)

    # 알고리즘으로 해독되지 않는 문자열을 code로 넣었을 경우 에러가 나는지
    def test_verify_email_code_invalid_code(self):
        self.code = "invalid_code"
        with self.assertRaises(BadSignature):
            verify_email_code(self.code)

    def test_verify_email_code_none(self):
        self.code = None
        with self.assertRaises(TypeError):
            verify_email_code(self.code)

    # verify_email_code의 시간 만료 설정이 잘 작동하는지
    def test_verify_email_code_expired(self):
        with freeze_time(datetime.now() + timedelta(minutes=31)):
            with self.assertRaises(SignatureExpired):
                verify_email_code(self.code)


class TestActivateEmailUser(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", nickname="test", password="test_password"
        )
        self.request = APIRequestFactory().post("/")
        self.request.META["HTTP_HOST"] = self.request.get_host()

    # activate_email_user까지의 일련의 과정이 성공적으로 동작하는지
    def test_successful_activate_user(self):
        send_verification_email(self.user, self.request)
        url = re.search(r"https?://\S+", mail.outbox[0].body).group()
        parsed_url = urlparse(url)
        code = parse_qs(parsed_url.query)["code"][0]
        email = verify_email_code(code)
        user = activate_email_user(email)
        self.assertEqual(user.email, self.user.email)
        self.assertEqual(user.is_active, True)


class TestDeactivateUser(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", nickname="test", password="test_password"
        )

    def test_deactivate_user(self):
        deactivate_user(user=self.user)
        self.assertEqual(self.user.is_active, False)
