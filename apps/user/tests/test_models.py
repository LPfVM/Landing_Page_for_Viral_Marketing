from django.contrib.auth import get_user_model
from django.db import DataError, IntegrityError
from django.test import TestCase

User = get_user_model()


class TestUserManager(TestCase):
    def setUp(self):
        self.data = {
            "email": "test@test.com",
            "password": "test_password",
            "nickname": "test_name",
        }


# create_user() 테스트
    def test_create_user(self):
        self.assertEqual(User.objects.count(), 0)

        user = User.objects.create_user(**self.data)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, self.data["email"])
        self.assertTrue(user.check_password(self.data["password"]))
        self.assertEqual(user.nickname, self.data["nickname"])
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_superuser)
        self.assertIsNone(user.last_login)


# email 없을 때
    def test_invalid_email(self):
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                email="",
                password=self.data["password"],
                nickname=self.data["nickname"],
            )
        self.assertEqual(str(context.exception), "이메일은 필수입니다.")


# normalize_email 테스트
    def test_normalize_email(self):
        user = User.objects.create_user(
            email="TEST@TEST.COM",
            password=self.data["password"],
            nickname=self.data["nickname"],
        )
        self.assertEqual(user.email, "TEST@test.com")


# create_superuser 테스트
    def test_create_superuser(self):
        user = User.objects.create_superuser(**self.data)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, self.data["email"])
        self.assertTrue(user.check_password(self.data["password"]))
        self.assertEqual(user.nickname, self.data["nickname"])
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_superuser)
        self.assertIsNone(user.last_login)


class TestUser(TestCase):
    def setUp(self):
        self.data = {
            "email": "test@test.com",
            "password": "test_password",
            "nickname": "test_name",
        }

# nickname 유니크 조건 테스트
    def test_unique_nickname(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.data)
            User.objects.create_user(
                email="test2@test.com",
                password="test2_password",
                nickname=self.data["nickname"],
            )


# nickname 최대 길이 테스트 50자
    def test_valid_max_length_nickname(self):
        User.objects.create_user(
            email=self.data["email"],
            password=self.data["password"],
            nickname="test2" * 10,
        )
        self.assertEqual(User.objects.count(), 1)

# nickname 최대 길이 테스트 51자
    def test_invalid_max_length_nickname(self):
        with self.assertRaises(DataError):
            User.objects.create_user(
                email=self.data["email"],
                password=self.data["password"],
                nickname="test2" * 10 + "t",
            )

# email 유니크 조건 테스트
    def test_unique_email(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.data)
            User.objects.create_user(
                email=self.data["email"],
                password="test2_password",
                nickname="test2_name",
            )


# email 최대 길이 테스트 255자
    def test_valid_max_length_email(self):
        User.objects.create_user(
            email="t" * 246 + "@test.com",
            password=self.data["password"],
            nickname=self.data["nickname"],
        )
        self.assertEqual(User.objects.count(), 1)

# email 최대 길이 조건 테스트 256자
    def test_invalid_max_length_email(self):
        with self.assertRaises(DataError):
            User.objects.create_user(
                email="t" * 247 + "@test.com",

# has_perm 테스트
    def test_has_perm(self):
        user = User.objects.create_user(**self.data)
        admin = User.objects.create_superuser(
            email="admin@admin.com",
            password="admin_password",
            nickname="admin_name",
        )
        self.assertFalse(user.has_perm("test"))
        self.assertTrue(admin.has_perm("test"))

# has_module_perms 테스트
    def test_has_module_perms(self):
        user = User.objects.create_user(**self.data)
        admin = User.objects.create_superuser(
            email="admin@admin.com",
            password="admin_password",
            nickname="admin_name",
        )
        self.assertFalse(user.has_module_perms("test"))
        self.assertTrue(admin.has_module_perms("test"))
