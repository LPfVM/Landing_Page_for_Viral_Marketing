import uuid
from unittest import TestCase

from django.contrib.auth import get_user_model
from django.http import Http404

from apps.notification.models import Notification
from apps.notification.services import get_unread_notifications, mark_notification_read

User = get_user_model()


class NotificationServiceTest(TestCase):
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
            message="읽지 않은 메시지",
            is_read=False,
        )
        self.read_notification = Notification.objects.create(
            user=self.user,
            message="이미 읽은 메세지",
            is_read=True,
        )
        self.other_user_notification = Notification.objects.create(
            user=self.other_user,
            message="다른 사람 메시지",
            is_read=False,
        )

    # 안읽은 알람만 오는지 테스트
    def test_get_unread_notifications(self):
        notifications = get_unread_notifications(user=self.user)

        self.assertEqual(notifications.count(), 1)
        self.assertEqual(notifications.first(), self.unread_notification)

    # 읽음 처리 잘 되는지
    def test_mark_notification_read(self):
        notifications = mark_notification_read(
            user=self.user, notification_id=self.unread_notification.id
        )

        self.unread_notification.refresh_from_db()

        self.assertEqual(notifications.id, self.unread_notification.id)
        self.assertTrue(self.unread_notification.is_read)

    # 다른 사람 알림은 못읽게
    def test_mark_notification_other_user(self):
        with self.assertRaises(Http404):
            mark_notification_read(
                user=self.user, notification_id=self.other_user_notification.id
            )
