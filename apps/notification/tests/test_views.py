import uuid

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.notification.models import Notification

User = get_user_model()


class NotificationViewTest(APITestCase):
    def setUp(self):
        unique_id = uuid.uuid4()

        self.user = User.objects.create_user(
            nickname=f"test_{unique_id}",
            email=f"test_{unique_id}@test.com",
            password="testpassword1234",
        )
        self.other_user = User.objects.create_user(
            nickname=f"other_{unique_id}",
            email=f"other_{unique_id}@test.com",
            password="testpassword1234",
        )

        self.unread_notification = Notification.objects.create(
            user=self.user,
            message="읽지 않은 알림",
            is_read=False,
        )
        self.read_notification = Notification.objects.create(
            user=self.user,
            message="이미 읽은 알림",
            is_read=True,
        )
        self.other_user_notification = Notification.objects.create(
            user=self.other_user,
            message="다른 유저 알림",
            is_read=False,
        )

        self.list_url = reverse("notification-list")
        self.read_url = reverse(
            "notification-read",
            kwargs={"pk": self.unread_notification.pk},
        )

    def test_authenticated_user_can_get_unread_notifications(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.unread_notification.id)
        self.assertEqual(response.data[0]["message"], self.unread_notification.message)
        self.assertEqual(response.data[0]["is_read"], False)

    def test_read_notifications_are_not_included_in_list(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_ids = [item["id"] for item in response.data]

        self.assertIn(self.unread_notification.id, response_ids)
        self.assertNotIn(self.read_notification.id, response_ids)

    def test_other_users_notifications_are_not_included_in_list(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_ids = [item["id"] for item in response.data]

        self.assertNotIn(self.other_user_notification.id, response_ids)

    def test_authenticated_user_can_mark_notification_as_read(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(self.read_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "알림을 읽음 처리했습니다.")

        self.unread_notification.refresh_from_db()
        self.assertTrue(self.unread_notification.is_read)

    def test_user_cannot_mark_other_users_notification_as_read(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "notification-read",
            kwargs={"pk": self.other_user_notification.pk},
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_get_notifications(self):
        response = self.client.get(self.list_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_unauthenticated_user_cannot_mark_notification_as_read(self):
        response = self.client.patch(self.read_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )
