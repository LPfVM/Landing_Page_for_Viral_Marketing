from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.user.serializers import UserSignUPSerializer

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
    def test_is_valid_missing_fields(self):
        self.data.pop("email")
        serializer = UserSignUPSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_is_valid_missing_field2(self):
        self.data.pop("password")
        serializer = UserSignUPSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    # email 필드를 빈 값으로 했을 때 valid 한지
    def test_is_valid_blank_fields(self):
        self.data["email"] = ""
        serializer = UserSignUPSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_is_valid_blank_field2(self):
        self.data["password"] = ""
        serializer = UserSignUPSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

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
