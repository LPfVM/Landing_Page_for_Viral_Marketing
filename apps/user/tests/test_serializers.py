from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.user.serializers import UserProfileSerializer, UserSignUPSerializer

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

    # patch 메소드인 경우, 필드가 하나 비어도 update가 제대로 동작하는지
    def test_patch_update(self):
        updated_data = {
            "email": self.data["email"],
            "password": self.data["password"] + "2",
        }
        serializer = UserProfileSerializer(
            instance=self.user, data=updated_data, partial=True
        )
        serializer.is_valid()
        updated_user = serializer.save()
        self.assertEqual(updated_user.email, updated_data["email"])
        self.assertEqual(updated_user.nickname, self.data["nickname"])
        self.assertTrue(updated_user.check_password(updated_data["password"]))
