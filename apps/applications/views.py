from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import IntegrityError
from .models import Application, SavedJob
from .serializers import (
    ApplicationSerializer,
    ApplicationStatusSerializer,
    SavedJobSerializer,
    ApplicationDetailSerializer,
)
from apps.accounts.models import User
from apps.common.exceptions import error_response
from apps.common.error_codes import ErrorCode
from apps.notifications.services import notify
from apps.notifications.models import Notification


# ─────────────────────────────────────────────────────────────────
# Permissions
# ─────────────────────────────────────────────────────────────────

class IsCandidate(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.CANDIDATE


class IsRecruiterOfJob(permissions.BasePermission):
    """Allow only the recruiter who owns the job's company."""
    def has_object_permission(self, request, view, obj):
        return obj.job.company.recruiter == request.user


# ─────────────────────────────────────────────────────────────────
# Candidate — Apply / View / Withdraw
# ─────────────────────────────────────────────────────────────────

class ApplyJobView(generics.CreateAPIView):
    """Candidate applies to a job. Fires notification to recruiter."""
    serializer_class = ApplicationSerializer
    permission_classes = [IsCandidate]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            application = serializer.save(candidate=request.user)

            # Notify the recruiter
            recruiter = application.job.company.recruiter
            notify(
                recipient=recruiter,
                notification_type=Notification.Type.APPLICATION_RECEIVED,
                title="New Application Received",
                message=(
                    f"{request.user.get_full_name() or request.user.email} "
                    f"applied for '{application.job.title}'."
                ),
                link=f"/api/v1/applications/{application.id}/status/",
            )

            return Response(ApplicationSerializer(application).data, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return error_response(
                ErrorCode.VALIDATION_ERROR,
                "You have already applied to this job.",
                status.HTTP_409_CONFLICT,
            )
        except Exception as e:
            return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


class MyApplicationsView(generics.ListAPIView):
    """Candidate: list all their own applications."""
    serializer_class = ApplicationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Application.objects
            .filter(candidate=self.request.user)
            .select_related('job', 'job__company')
        )


class WithdrawApplicationView(generics.DestroyAPIView):
    """Candidate withdraws (soft-deletes) their application by setting status=WITHDRAWN."""
    permission_classes = [IsCandidate]
    lookup_field = 'id'

    def get_queryset(self):
        return Application.objects.filter(candidate=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status in (Application.Status.ACCEPTED, Application.Status.REJECTED):
            return error_response(
                ErrorCode.VALIDATION_ERROR,
                "Cannot withdraw an already accepted or rejected application.",
                status.HTTP_400_BAD_REQUEST,
            )
        instance.status = Application.Status.WITHDRAWN
        instance.save(update_fields=['status'])
        return Response({'detail': 'Application withdrawn successfully.'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────
# Recruiter — View Applicants / Update Status
# ─────────────────────────────────────────────────────────────────

class JobApplicantsView(generics.ListAPIView):
    """Recruiter: list all applicants for one of their jobs."""
    serializer_class = ApplicationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        job_id = self.kwargs['job_id']
        return (
            Application.objects
            .filter(job__id=job_id, job__company__recruiter=self.request.user)
            .select_related('candidate', 'job', 'job__company')
            .exclude(status=Application.Status.WITHDRAWN)
        )


class ApplicationStatusUpdateView(generics.UpdateAPIView):
    """Recruiter updates the status of an application. Fires notification to candidate."""
    serializer_class = ApplicationStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Application.objects.select_related('job__company', 'candidate').all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.job.company.recruiter != request.user:
                return error_response(
                    ErrorCode.PERMISSION_DENIED,
                    "Not authorized to update this application.",
                    status.HTTP_403_FORBIDDEN,
                )
            kwargs['partial'] = True
            old_status = instance.status
            response = super().update(request, *args, **kwargs)

            # Refresh from DB to get new status
            instance.refresh_from_db()
            if instance.status != old_status:
                notify(
                    recipient=instance.candidate,
                    notification_type=Notification.Type.STATUS_CHANGED,
                    title="Application Status Updated",
                    message=(
                        f"Your application for '{instance.job.title}' at "
                        f"'{instance.job.company.name}' has been moved to "
                        f"'{instance.get_status_display()}'."
                    ),
                    link=f"/api/v1/applications/my/",
                )
            return response

        except Exception as e:
            return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


# ─────────────────────────────────────────────────────────────────
# Candidate — Save / Unsave Jobs
# ─────────────────────────────────────────────────────────────────

class SaveJobView(generics.CreateAPIView):
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(candidate=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return error_response(ErrorCode.VALIDATION_ERROR, "Job already saved.", status.HTTP_409_CONFLICT)
        except Exception as e:
            return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


class SavedJobsListView(generics.ListAPIView):
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            SavedJob.objects
            .filter(candidate=self.request.user)
            .select_related('job', 'job__company')
        )


class UnsaveJobView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return SavedJob.objects.filter(candidate=self.request.user)
