from django.urls import path
from .views import (
    JobListAPIView,
    JobDetailAPIView,
    JobCreateAPIView,
    JobUpdateDeleteAPIView,
    RecruiterMyJobsView,
    similar_jobs,
)

urlpatterns = [
    # ── Public / Candidate ───────────────────────────────────────
    path('',                        JobListAPIView.as_view(),        name='job-list'),
    path('<uuid:id>/',              JobDetailAPIView.as_view(),      name='job-detail'),
    path('<uuid:id>/similar/',      similar_jobs,                    name='job-similar'),

    # ── Recruiter ────────────────────────────────────────────────
    path('create/',                 JobCreateAPIView.as_view(),      name='job-create'),
    path('<uuid:id>/manage/',       JobUpdateDeleteAPIView.as_view(), name='job-manage'),
    path('my/',                     RecruiterMyJobsView.as_view(),   name='recruiter-my-jobs'),
]