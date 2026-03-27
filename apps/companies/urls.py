from django.urls import path
from .views import (
    CompanyListCreateView,
    CompanyDetailView,
    FollowCompanyView,
    UnfollowCompanyView,
    MyFollowedCompaniesView,
)

urlpatterns = [
    # ── Company CRUD ─────────────────────────────────────────────
    path('',                            CompanyListCreateView.as_view(),  name='company-list-create'),
    path('<uuid:id>/',                  CompanyDetailView.as_view(),      name='company-detail'),

    # ── Follow / Unfollow ────────────────────────────────────────
    path('follow/',                     FollowCompanyView.as_view(),      name='company-follow'),
    path('<uuid:id>/unfollow/',         UnfollowCompanyView.as_view(),    name='company-unfollow'),
    path('following/',                  MyFollowedCompaniesView.as_view(), name='company-following'),
]
