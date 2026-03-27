from django.urls import path
from .views import NotificationListView, MarkNotificationReadView, mark_all_read

urlpatterns = [
    path('',                       NotificationListView.as_view(),    name='notification-list'),
    path('mark-all-read/',         mark_all_read,                     name='notifications-mark-all-read'),
    path('<uuid:id>/read/',        MarkNotificationReadView.as_view(), name='notification-read'),
]
