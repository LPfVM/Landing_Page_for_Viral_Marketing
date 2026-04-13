from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notification.serializers import NotificationSerializer
from apps.notification.services import (
    get_unread_notifications,
    mark_notification_read,
)


@extend_schema(tags=["Notification"])
class NotificationSwaggerView(APIView):
    pass


class NotificationListAPIView(NotificationSwaggerView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = get_unread_notifications(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationReadAPIView(NotificationSwaggerView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        mark_notification_read(
            user=request.user,
            notification_id=pk,
        )
        return Response(
            {"detail": "알림을 읽음 처리했습니다."},
            status=status.HTTP_200_OK,
        )
