from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.companies.models import Company
from apps.jobs.models import Job
from apps.applications.models import Application, SavedJob

User = get_user_model()


class ApplicationsAPITests(APITestCase):
    def setUp(self):
        self.recruiter = User.objects.create_user(
            email='recruiter@apptest.com',
            username='recruiter_app',
            password='Password123!',
            role=User.Role.RECRUITER,
        )
        self.candidate = User.objects.create_user(
            email='candidate@apptest.com',
            username='candidate_app',
            password='Password123!',
            role=User.Role.CANDIDATE,
        )

        self.company = Company.objects.create(
            name='AppCorp',
            email='contact@appcorp.com',
            description='Test company',
            website='https://appcorp.com',
            location='New York, NY',
            recruiter=self.recruiter,
        )

        self.job = Job.objects.create(
            title='Python Developer',
            company=self.company,
            location='New York, NY',
            description='Backend engineer role',
            requirements='Python, Django',
            status=Job.Status.ACTIVE,
        )

    def test_candidate_apply_job(self):
        self.client.force_authenticate(user=self.candidate)
        url = reverse('apply-job')
        data = {
            'job': str(self.job.id),
            'cover_letter': 'I am deeply interested in this position.',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Application.objects.filter(candidate=self.candidate, job=self.job).exists())

    def test_duplicate_application_fails(self):
        Application.objects.create(candidate=self.candidate, job=self.job, cover_letter='First')
        self.client.force_authenticate(user=self.candidate)
        url = reverse('apply-job')
        data = {'job': str(self.job.id), 'cover_letter': 'Second'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_recruiter_view_and_update_application_status(self):
        app = Application.objects.create(candidate=self.candidate, job=self.job)
        self.client.force_authenticate(user=self.recruiter)

        # View applicants
        url_applicants = reverse('job-applicants', kwargs={'job_id': self.job.id})
        resp = self.client.get(url_applicants)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['results']), 1)

        # Update status
        url_update = reverse('application-status', kwargs={'id': app.id})
        resp_update = self.client.patch(url_update, {'status': Application.Status.SHORTLISTED}, format='json')
        self.assertEqual(resp_update.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.SHORTLISTED)

    def test_candidate_withdraw_application(self):
        app = Application.objects.create(candidate=self.candidate, job=self.job)
        self.client.force_authenticate(user=self.candidate)
        url = reverse('withdraw-application', kwargs={'id': app.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.WITHDRAWN)

    def test_save_and_unsave_job(self):
        self.client.force_authenticate(user=self.candidate)
        url_save = reverse('save-job')
        resp_save = self.client.post(url_save, {'job': str(self.job.id)}, format='json')
        self.assertEqual(resp_save.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SavedJob.objects.filter(candidate=self.candidate, job=self.job).exists())

        saved_obj = SavedJob.objects.get(candidate=self.candidate, job=self.job)
        url_unsave = reverse('unsave-job', kwargs={'id': saved_obj.id})
        resp_unsave = self.client.delete(url_unsave)
        self.assertEqual(resp_unsave.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SavedJob.objects.filter(candidate=self.candidate, job=self.job).exists())
