from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import serializers

from apps.user.serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
    UserSignUPSerializer,
)

User = get_user_model()


class TestUserSignUPSerializer(TestCase):
    def setUp(self):
        self.data = {
            "email": "test@test.com",
            "nickname": "test",
            "password": "test_password",
        }

    # data가 valid한지 테스트
    def test_is_valid(self):
        serializer = UserSignUPSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    # email 필드를 data에서 삭제했을 때 valid한지
    def test_missing_fields(self):
        self.data.pop("email")
        serializer = UserSignUPSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    # email 필드를 빈 값으로 했을 때 valid 한지
    def test_blank_fields(self):
        self.data["email"] = ""
        serializer = UserSignUPSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    # is_valid()를 통과했을 때 validate_data와 self.data의 값이 같은지
    def test_validated_data(self):
        self.data["is_admin"] = False
        serializer = UserSignUPSerializer(data=self.data)
        serializer.is_valid()
        self.assertEqual(serializer.validated_data["email"], self.data["email"])
        self.assertEqual(serializer.validated_data["nickname"], self.data["nickname"])
        self.assertEqual(serializer.validated_data["password"], self.data["password"])
        self.assertNotIn("is_admin", serializer.validated_data)

    # serializer.save() 가 잘 동작하는지
    def test_save(self):
        serializer = UserSignUPSerializer(data=self.data)
        serializer.is_valid()
        user = serializer.save()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(serializer.validated_data["email"], user.email)
        self.assertEqual(serializer.validated_data["nickname"], user.nickname)
        self.assertTrue(user.check_password(serializer.validated_data["password"]))

    # write_only 옵션이 잘 동작 하는지
    def test_write_only_fields(self):
        serializer = UserSignUPSerializer(data=self.data)
        serializer.is_valid()
        serializer.save()
        self.assertNotIn("password", serializer.data)
        self.assertIn("email", serializer.data)


class TestUserProfileSerializer(TestCase):
    def setUp(self):
        self.data = {
            "email": "test@test.com",
            "nickname": "test",
            "password": "test_password",
        }
        self.user = User.objects.create_user(**self.data)

    # serializer.data(읽기용 데이터)의 필드가 시리얼라이저에서 정의한 것과 같은지
    def test_serializer_data(self):
        serializer = UserProfileSerializer(instance=self.user)
        self.assertEqual(serializer.data["email"], self.user.email)
        self.assertEqual(serializer.data["nickname"], self.user.nickname)
        self.assertNotIn("password", serializer.data)
        self.assertEqual(set(serializer.data.keys()), {"email", "nickname"})

    # updated_data가 valid 한지
    def test_is_valid_updated_data(self):
        updated_data = {
            "email": self.data["email"],
            "nickname": self.data["nickname"] + "2",
            "password": self.data["password"] + "2",
        }
        serializer = UserProfileSerializer(instance=self.user, data=updated_data)
        self.assertTrue(serializer.is_valid())

    # put 메소드인 경우, 요구하는 필드가 없을 때 에러가 나는지
    def test_put_missing_fields(self):
        updated_data = {
            "email": self.data["email"],
            "password": self.data["password"] + "2",
        }
        serializer = UserProfileSerializer(instance=self.user, data=updated_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("nickname", serializer.errors)

    # put 메소드인 경우, 요구하는 필드가 빈 값이었을 때 에러가 나는지
    def test_put_blank_fields(self):
        updated_data = {
            "email": self.data["email"],
            "nickname": "",
            "password": self.data["password"] + "2",
        }
        serializer = UserProfileSerializer(instance=self.user, data=updated_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("nickname", serializer.errors)

    # patch 메소드인 경우, 요구하는 필드가 없을 때 잘 작동하는지
    def test_patch_validated_data(self):
        updated_data = {
            "email": self.data["email"],
            "password": self.data["password"] + "2",
        }
        serializer = UserProfileSerializer(
            instance=self.user, data=updated_data, partial=True
        )
        self.assertTrue(serializer.is_valid())

    # read_only 필드가 제대로 작동하는지
    def test_read_only_fields(self):
        updated_data = {
            "email": "2" + self.data["email"],
            "nickname": self.data["nickname"],
            "password": self.data["password"],
        }
        # 바뀐 email 값을 시리얼라이저에 넣음
        serializer = UserProfileSerializer(instance=self.user, data=updated_data)
        serializer.is_valid()
        # serializer.data(읽기용 데이터)의 email은 여전히 기존 email과 같음
        self.assertEqual(serializer.data["email"], self.user.email)
        # serializer.validated_data(쓰기용 데이터)에 email 없음
        self.assertNotIn("email", serializer.validated_data)

    # put 메소드인 경우, update가 제대로 동작하는지
    def test_put_update(self):
        updated_data = {
            "email": self.data["email"],
            "nickname": self.data["nickname"] + "2",
            "password": self.data["password"] + "2",
        }
        serializer = UserProfileSerializer(instance=self.user, data=updated_data)
        serializer.is_valid()
        updated_user = serializer.save()
        self.assertEqual(updated_user.email, updated_data["email"])
        self.assertEqual(updated_user.nickname, updated_data["nickname"])
        self.assertTrue(updated_user.check_password(updated_data["password"]))

    # patch 메소드인 경우, 필드가 비어도 update가 제대로 동작하는지
    def test_patch_update(self):
        updated_data = {
            "password": self.data["password"] + "2",
        }
        serializer = UserProfileSerializer(
            instance=self.user, data=updated_data, partial=True
        )
        serializer.is_valid()
        updated_user = serializer.save()
        self.assertEqual(updated_user.email, self.data["email"])
        self.assertEqual(updated_user.nickname, self.data["nickname"])
        self.assertTrue(updated_user.check_password(updated_data["password"]))


class TestUserLoginSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            nickname="test",
            password="test_password",
        )
        self.user.is_active = True
        self.user.save()
        self.data = {
            "email": "test@test.com",
            "password": "test_password",
        }

    # data가 valid한지
    def test_data_is_valid(self):
        serializer = UserLoginSerializer(data=self.data, context={"request": None})
        self.assertTrue(serializer.is_valid())

    # 필수 data가 빠졌을 때 valid 한지
    def test_validate_missing_fields(self):
        data = {
            "email": self.data["email"],
        }
        serializer = UserLoginSerializer(data=data, context={"request": None})
        self.assertFalse(serializer.is_valid())

    # 필수 data가 빈 문자열일 때 valid 한지
    def test_validate_blank_fields(self):
        data = {
            "email": self.data["email"],
            "password": "",
        }
        serializer = UserLoginSerializer(data=data, context={"request": None})
        self.assertFalse(serializer.is_valid())

    # 필수 data가 None일 때 valid 한지
    def test_validate_None_fields(self):
        data = {
            "email": self.data["email"],
            "password": None,
        }
        serializer = UserLoginSerializer(data=data, context={"request": None})
        self.assertFalse(serializer.is_valid())

    # authenticate()가 각기 다른 data에 맞는 유저들을 잘 찾는지
    def test_validate_authenticate(self):
        user = User.objects.create_user(
            email="test2@test.com",
            nickname="test2",
            password="test2_password",
        )
        user.is_active = True
        user.save()
        data = {
            "email": "test2@test.com",
            "password": "test2_password",
        }
        serializer = UserLoginSerializer(data=self.data, context={"request": None})
        serializer2 = UserLoginSerializer(data=data, context={"request": None})
        serializer.is_valid()
        serializer2.is_valid()
        self.assertEqual(serializer.validated_data["user"], self.user)
        self.assertEqual(serializer2.validated_data["user"], user)

    # 잘못된 로그인 정보를 넣은 경우
    def test_validate_is_not_user(self):
        wrong_data = {
            "email": self.data["email"],
            "password": self.data["password"] + "2",
        }
        with self.assertRaises(serializers.ValidationError) as e:
            serializer = UserLoginSerializer(data=wrong_data, context={"request": None})
            serializer.is_valid(raise_exception=True)
        self.assertEqual(
            e.exception.detail["non_field_errors"][0], "유저 정보가 맞지 않습니다."
        )

    # PASSWORD가 없을 때 validate()가 잘 거르는지
    def test_validate_is_not_password(self):
        wrong_data = {"email": self.data["email"]}
        with self.assertRaises(serializers.ValidationError) as e:
            serializer = UserLoginSerializer(data=self.data, context={"request": None})
            serializer.validate(data=wrong_data)
        self.assertEqual(e.exception.detail[0], "이메일과 비밀번호는 필수입니다.")
        self.assertEqual(e.exception.detail[0].code, "authenticate")

    # email이 없을때 validate()가 잘 거르는지
    def test_validate_is_not_email(self):
        wrong_data = {"password": self.data["password"]}
        with self.assertRaises(serializers.ValidationError) as e:
            serializer = UserLoginSerializer(data=self.data, context={"request": None})
            serializer.validate(data=wrong_data)
        self.assertEqual(e.exception.detail[0], "이메일과 비밀번호는 필수입니다.")
        self.assertEqual(e.exception.detail[0].code, "authenticate")

    # validated_data가 의도한 것과 일치하는지
    def test_serializer_validated_data(self):
        serializer = UserLoginSerializer(data=self.data, context={"request": None})
        serializer.is_valid()
        self.assertEqual(serializer.validated_data["email"], self.data["email"])
        self.assertEqual(serializer.validated_data["password"], self.data["password"])
        self.assertEqual(serializer.validated_data["user"], self.user)
        self.assertEqual(
            set(serializer.validated_data.keys()), {"email", "password", "user"}
        )
