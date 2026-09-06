from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.companies.models import Company
from apps.jobs.models import Job
from apps.jobs.selectors import get_active_jobs, get_similar_jobs, get_jobs_for_recruiter

User = get_user_model()


class JobsAPITests(APITestCase):
    def setUp(self):
        self.recruiter = User.objects.create_user(
            email='recruiter@jobtest.com',
            username='recruiter_job',
            password='Password123!',
            role=User.Role.RECRUITER,
        )
        self.candidate = User.objects.create_user(
            email='candidate@jobtest.com',
            username='candidate_job',
            password='Password123!',
            role=User.Role.CANDIDATE,
        )

        self.company = Company.objects.create(
            name='JobCorp',
            email='jobs@jobcorp.com',
            description='Tech company',
            website='https://jobcorp.com',
            location='San Francisco, CA',
            recruiter=self.recruiter,
        )

        self.active_job = Job.objects.create(
            title='Backend Engineer',
            company=self.company,
            location='San Francisco, CA',
            description='Django backend developer role',
            requirements='Python, Django, PostgreSQL',
            salary_min=100000,
            salary_max=140000,
            job_type=Job.JobType.FULL_TIME,
            experience_level=Job.ExperienceLevel.MID,
            status=Job.Status.ACTIVE,
        )

        self.draft_job = Job.objects.create(
            title='Draft Engineer',
            company=self.company,
            location='San Francisco, CA',
            description='Unpublished draft role',
            requirements='Python',
            status=Job.Status.DRAFT,
        )

    def test_list_active_jobs_public(self):
        url = reverse('job-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        titles = [j['title'] for j in results]
        self.assertIn('Backend Engineer', titles)
        self.assertNotIn('Draft Engineer', titles)

    def test_get_job_detail_increments_views(self):
        url = reverse('job-detail', kwargs={'id': self.active_job.id})
        initial_views = self.active_job.view_count
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Backend Engineer')
        self.active_job.refresh_from_db()
        self.assertEqual(self.active_job.view_count, initial_views + 1)

    def test_recruiter_can_create_job(self):
        self.client.force_authenticate(user=self.recruiter)
        url = reverse('job-create')
        data = {
            'title': 'Frontend Developer',
            'company': str(self.company.id),
            'location': 'Remote',
            'description': 'React UI specialist',
            'requirements': 'React, JavaScript, CSS',
            'salary_min': 90000,
            'salary_max': 120000,
            'job_type': Job.JobType.REMOTE,
            'experience_level': Job.ExperienceLevel.MID,
            'status': Job.Status.ACTIVE,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Job.objects.filter(title='Frontend Developer').exists())

    def test_candidate_cannot_create_job(self):
        self.client.force_authenticate(user=self.candidate)
        url = reverse('job-create')
        data = {
            'title': 'Illegal Job',
            'company': str(self.company.id),
            'location': 'Remote',
            'description': 'Descr',
            'requirements': 'Reqs',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_similar_jobs(self):
        similar_job = Job.objects.create(
            title='Senior Backend Dev',
            company=self.company,
            location='San Francisco, CA',
            description='Senior Django dev',
            requirements='Python, Django',
            job_type=Job.JobType.FULL_TIME,
            experience_level=Job.ExperienceLevel.MID,
            status=Job.Status.ACTIVE,
        )
        url = reverse('job-similar', kwargs={'id': self.active_job.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        job_ids = [j['id'] for j in response.data]
        self.assertIn(str(similar_job.id), job_ids)
        self.assertNotIn(str(self.active_job.id), job_ids)

    def test_selectors(self):
        active_qs = get_active_jobs()
        self.assertEqual(active_qs.count(), 1)
        recruiter_qs = get_jobs_for_recruiter(self.recruiter)
        self.assertEqual(recruiter_qs.count(), 2)
