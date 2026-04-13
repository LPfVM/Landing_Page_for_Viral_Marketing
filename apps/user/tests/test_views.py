import json
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.signing import TimestampSigner, dumps
from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class TestUserSignUpView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user:user_signup")
        self.data = {
            "email": "test@test.com",
            "nickname": "test",
            "password": "test_password",
        }

    # 필수 항목이 빠졌을 때 회원가입이 실패하는지
    def test_signup_missing_data(self):
        self.data.pop("password")
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(User.objects.count(), 0)

    # 필수 항목이 빈 값일 때 회원가입이 실패하는지
    def test_signup_blank_data(self):
        self.data["password"] = ""
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(User.objects.count(), 0)

    # valid한 데이터를 넣었을 때 성공하는지
    def test_signup_valid_data(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get("message"), "email 인증 링크를 발송했습니다."
        )
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().is_active, False)


class TestEmailVerifyView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user:email_verify")
        self.user = User.objects.create_user(
            email="test@test.com",
            nickname="test",
            password="test_password",
        )

    # code가 요청에 담겨있지 않을 때 예외처리 되는지
    def test_missing_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "유효하지 않은 인증 링크입니다.")

    # code가 빈 문자열일 때 예외처리 되는지
    def test_blank_code(self):
        code = ""
        response = self.client.get(self.url, {"code": code})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "유효하지 않은 인증 링크입니다.")

    # code가 서명값이 없는 임의의 문자열일 때 예외처리가 되는지
    def test_undecoded_code(self):
        code = "undecoded_code"
        response = self.client.get(self.url, {"code": code})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "유효하지 않은 인증 링크입니다.")

    # code가 만료됐을 때 예외처리가 되는지
    def test_expired_code(self):
        signer = TimestampSigner()
        signed_user_email = signer.sign(self.user.email)
        code = dumps(signed_user_email)
        with freeze_time(datetime.now() + timedelta(minutes=31)):
            response = self.client.get(self.url, {"code": code})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data.get("message"), "유효하지 않은 인증 링크입니다."
            )

    # 데이터베이스에 기록되지 않은 이메일을 사용했을 때 에러가 발생하는지
    def test_user_not_found(self):
        self.user.email = "invalid_test@test.com"
        signer = TimestampSigner()
        signed_user_email = signer.sign(self.user.email)
        code = dumps(signed_user_email)
        response = self.client.get(self.url, {"code": code})
        self.user.refresh_from_db()
        self.assertEqual(self.user.is_active, False)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("No User", response.data.get("detail"))

    # 올바른 이메일을 넣었을 때 성공하는지
    def test_valid_email(self):
        signer = TimestampSigner()
        signed_user_email = signer.sign(self.user.email)
        code = dumps(signed_user_email)
        response = self.client.get(self.url, {"code": code})
        self.user.refresh_from_db()
        self.assertEqual(self.user.is_active, True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("message"), "회원가입이 성공적으로 완료되었습니다."
        )


class TestUserLoginView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user:user_login")
        self.user = User.objects.create_user(
            email="test@test.com",
            nickname="test",
            password="test_password",
            is_active=True,
        )

        self.data = {
            "email": "test@test.com",
            "password": "test_password",
        }

    # 로그인 성공시 의도한 데이터가 나오는지
    def test_login(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["access"])
        self.assertIn("refresh_token", response.cookies)
        self.assertTrue(response.cookies["refresh_token"])

        # 없는 유저의 정보를 넣었을 때 예외처리가 되는지

    def test_user_not_found(self):
        self.data["email"] = "fake_test@test.com"
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"][0], "유저 정보가 맞지 않습니다."
        )

    # email이 빠졌을 때 예외처리가 되는지
    def test_missing_email(self):
        self.data.pop("email")
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "이 필드는 필수 항목입니다.")
        self.assertEqual(response.data["email"][0].code, "required")

    # email이 빈값일 때 예외처리가 되는지
    def test_blank_email(self):
        self.data["email"] = ""
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "이 필드는 blank일 수 없습니다.")
        self.assertEqual(response.data["email"][0].code, "blank")

    # email이 None일 때 예외처리가 되는지
    def test_none_email(self):
        self.data["email"] = None
        response = self.client.post(
            self.url, data=json.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "이 필드는 null일 수 없습니다.")
        self.assertEqual(response.data["email"][0].code, "null")

    # 유효하지 않은 email을 넣었을 때 예외처리가 되는지
    def test_invalid_email(self):
        self.data["email"] = "test_test_com"
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "유효한 이메일 주소를 입력하세요.")
        self.assertEqual(response.data["email"][0].code, "invalid")


class TestUserProfileView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com",
            nickname="test",
            password="test_password",
            is_active=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("user:user_profile", kwargs={"pk": self.user.pk})

    # 비로그인 유저가 접근했을 때 에러가 나는지
    def test_is_authenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # 본인이 아닌 다른 유저가 프로필에 접근했을 때 예외처리가 되는지
    def test_another_cannot_user_access_profile(self):
        another_user = User.objects.create_user(
            email="test2@test.com",
            nickname="test2",
            password="test2_password",
            is_active=True,
        )
        url = reverse("user:user_profile", kwargs={"pk": another_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "권환 없음")

    # 프로필 조회가 잘 되는지
    def test_get_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            list(response.data.values()), [self.user.nickname, self.user.email]
        )

    # 프로필 수정이 잘 되는지
    def test_put_profile(self):
        updated_data = {
            "nickname": "test2",
            "password": "test2_password",
        }
        response = self.client.put(self.url, data=updated_data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.nickname, updated_data["nickname"])
        self.assertEqual(self.user.check_password(updated_data["password"]), True)

    # 부분 수정이 잘 되는지
    def test_partial_put_profile(self):
        updated_data = {
            "password": "test2_password",
        }
        response = self.client.put(self.url, data=updated_data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.nickname, "test")
        self.assertEqual(self.user.check_password(updated_data["password"]), True)

    # delete가 잘 작동하는지
    def test_delete_profile(self):
        response = self.client.delete(self.url)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data.get("message"), "Deleted successfully")
        self.assertEqual(self.user.is_active, False)

    # put 메서드에 유효하지 않은 데이터가 들어왔을때
    def test_update_invalid(self):

        response = self.client.put(self.url, data={"nickname": "ascde" * 100})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUserLogoutView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com",
            nickname="test",
            password="test_password",
            is_active=True,
        )
        self.url = reverse("user:user_logout")

    # refresh가 없거나 빈 문자열인 경우 예외처리가 잘 되는지
    def test_none_refresh(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "refresh 토큰이 없습니다.")

    # refresh가 유효하지 않은 경우 예외처리가 잘 되는지
    def test_invalid_refresh(self):
        self.client.cookies["refresh_token"] = "fake_refresh"
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "유효하지 않은 토큰 입니다.")

    # 로그아웃이 잘 되는지
    def test_valid_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["refresh_token"] = str(refresh)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "로그아웃 되었습니다.")


class TestUserRefreshView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com",
            nickname="test",
            password="testpassword",
            is_active=True,
        )
        self.url = reverse("user:token_refresh")

    def test_no_cookie(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "refresh 토큰이 없습니다.")

    def test_token_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["refresh_token"] = str(refresh)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["access"])
