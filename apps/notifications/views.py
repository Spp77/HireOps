from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """Return the authenticated user's notifications, latest first."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class MarkNotificationReadView(generics.UpdateAPIView):
    """Mark a single notification as read."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save(update_fields=['is_read'])
        return Response(NotificationSerializer(instance).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_read(request):
    """Bulk-mark all unread notifications as read."""
    updated = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).update(is_read=True)
    return Response({'marked_read': updated})
