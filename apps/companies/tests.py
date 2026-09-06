from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.companies.models import Company, CompanyFollow

User = get_user_model()


class CompaniesAPITests(APITestCase):
    def setUp(self):
        self.recruiter = User.objects.create_user(
            email='recruiter@company.com',
            username='recruiter_comp',
            password='Password123!',
            role=User.Role.RECRUITER,
        )
        self.candidate = User.objects.create_user(
            email='candidate@comp.com',
            username='candidate_comp',
            password='Password123!',
            role=User.Role.CANDIDATE,
        )

        self.list_create_url = reverse('company-list-create')
        self.follow_url = reverse('company-follow')
        self.following_url = reverse('company-following')

    def test_recruiter_can_create_company(self):
        self.client.force_authenticate(user=self.recruiter)
        data = {
            'name': 'TechCorp',
            'email': 'contact@techcorp.com',
            'description': 'Leading technology enterprise',
            'website': 'https://techcorp.com',
            'location': 'San Francisco, CA',
            'industry': 'Software',
            'size': '500+',
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'TechCorp')
        self.assertTrue(Company.objects.filter(name='TechCorp').exists())

    def test_candidate_cannot_create_company(self):
        self.client.force_authenticate(user=self.candidate)
        data = {
            'name': 'CandidateCorp',
            'email': 'contact@candidatecorp.com',
            'description': 'Descr',
            'website': 'https://candidatecorp.com',
            'location': 'NYC',
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_follow_and_unfollow_company(self):
        company = Company.objects.create(
            name='Innovate Inc',
            email='contact@innovate.com',
            description='Innovative solutions',
            website='https://innovate.com',
            location='Austin, TX',
            recruiter=self.recruiter,
        )

        self.client.force_authenticate(user=self.candidate)
        follow_data = {'company': str(company.id)}
        response = self.client.post(self.follow_url, follow_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CompanyFollow.objects.filter(candidate=self.candidate, company=company).exists())

        # List followed companies
        resp_list = self.client.get(self.following_url)
        self.assertEqual(resp_list.status_code, status.HTTP_200_OK)

        # Unfollow
        follow_obj = CompanyFollow.objects.get(candidate=self.candidate, company=company)
        unfollow_url = reverse('company-unfollow', kwargs={'id': follow_obj.id})
        resp_unfollow = self.client.delete(unfollow_url)
        self.assertEqual(resp_unfollow.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CompanyFollow.objects.filter(candidate=self.candidate, company=company).exists())
