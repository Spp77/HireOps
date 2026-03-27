from django.urls import path
from .views import (
    ApplyJobView,
    MyApplicationsView,
    WithdrawApplicationView,
    ApplicationStatusUpdateView,
    JobApplicantsView,
    SaveJobView,
    SavedJobsListView,
    UnsaveJobView,
)

urlpatterns = [
    # ── Candidate ────────────────────────────────────────────────
    path('apply/',                              ApplyJobView.as_view(),               name='apply-job'),
    path('my/',                                 MyApplicationsView.as_view(),         name='my-applications'),
    path('<uuid:id>/withdraw/',                 WithdrawApplicationView.as_view(),    name='withdraw-application'),

    # ── Recruiter ────────────────────────────────────────────────
    path('job/<uuid:job_id>/applicants/',       JobApplicantsView.as_view(),          name='job-applicants'),
    path('<uuid:id>/status/',                   ApplicationStatusUpdateView.as_view(), name='application-status'),

    # ── Saved Jobs ───────────────────────────────────────────────
    path('saved/',                              SavedJobsListView.as_view(),          name='saved-jobs'),
    path('saved/save/',                         SaveJobView.as_view(),                name='save-job'),
    path('saved/<uuid:id>/unsave/',             UnsaveJobView.as_view(),              name='unsave-job'),
]
