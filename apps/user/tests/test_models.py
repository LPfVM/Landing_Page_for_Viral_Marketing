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

    def test_create_user(self):
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

    def test_invalid_email(self):
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                email="",
                password=self.data["password"],
                nickname=self.data["nickname"],
            )
        self.assertEqual(str(context.exception), "이메일은 필수입니다.")

    def test_normalize_email(self):
        user = User.objects.create_user(
            email="TEST@TEST.COM",
            password=self.data["password"],
            nickname=self.data["nickname"],
        )
        self.assertEqual(user.email, "TEST@test.com")

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
        self.user = User.objects.create_user(**self.data)

    def test_unique_nickname(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="test2@test.com",
                password="test2_password",
                nickname=self.data["nickname"],
            )

    def test_max_length_nickname(self):
        with self.assertRaises(DataError):
            User.objects.create_user(
                email="test2@test.com",
                password="test2_password",
                nickname="test2_name" * 10,
            )

    def test_unique_email(self):
        with self.assertRaises(IntegrityError):
            User.objects.create(
                email=self.data["email"],
                password="test2_password",
                nickname="test2_name",
            )

    def test_max_length_email(self):
        with self.assertRaises(DataError):
            User.objects.create(
                email="test2@test.com" * 50,
                password="test2_password",
                nickname="test2_name",
            )

    def test_has_perm(self):
        admin = User.objects.create_superuser(
            email="admin@admin.com",
            password="admin_password",
            nickname="admin_name",
        )
        self.assertFalse(self.user.has_perm("test"))
        self.assertTrue(admin.has_perm("test"))

    def test_has_module_perms(self):
        admin = User.objects.create_superuser(
            email="admin@admin.com",
            password="admin_password",
            nickname="admin_name",
        )
        self.assertFalse(self.user.has_module_perms("test"))
        self.assertTrue(admin.has_module_perms("test"))
