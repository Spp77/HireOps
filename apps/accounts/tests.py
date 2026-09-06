from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        self.me_url = reverse('me')

        self.candidate_data = {
            'email': 'candidate@example.com',
            'username': 'candidate',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'role': User.Role.CANDIDATE,
            'password': 'Password123!',
        }

        self.recruiter_data = {
            'email': 'recruiter@example.com',
            'username': 'recruiter',
            'first_name': 'John',
            'last_name': 'Smith',
            'role': User.Role.RECRUITER,
            'password': 'Password123!',
        }

    def test_register_candidate_success(self):
        response = self.client.post(self.register_url, self.candidate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'candidate@example.com')
        self.assertEqual(response.data['role'], User.Role.CANDIDATE)
        self.assertTrue(User.objects.filter(email='candidate@example.com').exists())

    def test_register_recruiter_success(self):
        response = self.client.post(self.register_url, self.recruiter_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], User.Role.RECRUITER)

    def test_register_duplicate_email_fails(self):
        self.client.post(self.register_url, self.candidate_data, format='json')
        response = self.client.post(self.register_url, self.candidate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        User.objects.create_user(
            email='user@example.com',
            username='user',
            password='Password123!',
            role=User.Role.CANDIDATE,
        )
        login_data = {'email': 'user@example.com', 'password': 'Password123!'}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_get_me_authenticated(self):
        user = User.objects.create_user(
            email='me@example.com',
            username='meuser',
            password='Password123!',
            first_name='Alice',
            last_name='Wonder',
            role=User.Role.CANDIDATE,
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'me@example.com')
        self.assertEqual(response.data['first_name'], 'Alice')

    def test_get_me_unauthenticated_fails(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
