from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.notifications.models import Notification

User = get_user_model()


class NotificationsAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='notif@example.com',
            username='notifuser',
            password='Password123!',
        )
        self.notif1 = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.Type.GENERAL,
            title='Welcome to HireOps',
            message='Thanks for joining.',
        )
        self.notif2 = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.Type.JOB_RECOMMENDED,
            title='Job match found',
            message='Check out new Python roles.',
        )

        self.list_url = reverse('notification-list')
        self.mark_all_url = reverse('notifications-mark-all-read')

    def test_list_notifications(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_mark_single_notification_read(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-read', kwargs={'id': self.notif1.id})
        response = self.client.put(url, {'is_read': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notif1.refresh_from_db()
        self.assertTrue(self.notif1.is_read)

    def test_mark_all_notifications_read(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.mark_all_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['marked_read'], 2)
        self.assertFalse(Notification.objects.filter(recipient=self.user, is_read=False).exists())
