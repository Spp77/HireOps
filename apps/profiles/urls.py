from django.urls import path
from .views import (
    MyProfileView,
    WorkExperienceListCreateView,
    WorkExperienceDetailView,
    EducationListCreateView,
    EducationDetailView,
)

urlpatterns = [
    # ── Profile ──────────────────────────────────────────────────
    path('me/',                                 MyProfileView.as_view(),               name='my-profile'),

    # ── Work Experience ──────────────────────────────────────────
    path('me/experience/',                      WorkExperienceListCreateView.as_view(), name='work-exp-list'),
    path('me/experience/<uuid:id>/',            WorkExperienceDetailView.as_view(),     name='work-exp-detail'),

    # ── Education ────────────────────────────────────────────────
    path('me/education/',                       EducationListCreateView.as_view(),      name='education-list'),
    path('me/education/<uuid:id>/',             EducationDetailView.as_view(),          name='education-detail'),
]
