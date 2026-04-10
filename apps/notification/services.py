from django.shortcuts import get_object_or_404

from apps.notification.models import Notification


# 알람 생성
def create_notification(*, user, message: str) -> Notification:
    return Notification.objects.create(
        user=user,
        message=message,
    )


# 안 읽은 알람 불러오기
def get_unread_notifications(*, user):
    return Notification.objects.filter(
        user=user,
        is_read=False,
    ).order_by("-created_at")


# 읽음 처리
def mark_notification_read(*, user, notification_id: int) -> Notification:
    notification = get_object_or_404(
        Notification,
        pk=notification_id,
        user=user,
    )
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return notification
