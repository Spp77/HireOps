from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import IntegrityError
from .models import Company, CompanyFollow
from .serializers import CompanySerializer, CompanyFollowSerializer
from apps.accounts.models import User
from apps.common.exceptions import error_response
from apps.common.error_codes import ErrorCode


# ─────────────────────────────────────────────────────────────────
# Permissions
# ─────────────────────────────────────────────────────────────────

class IsRecruiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.RECRUITER

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.recruiter == request.user


# ─────────────────────────────────────────────────────────────────
# Company CRUD
# ─────────────────────────────────────────────────────────────────

class CompanyListCreateView(generics.ListCreateAPIView):
    serializer_class = CompanySerializer
    search_fields = ['name', 'location', 'industry']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        return Company.objects.select_related('recruiter').all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsRecruiter()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(recruiter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return error_response(ErrorCode.COMPANY_ALREADY_EXISTS, "A company with this name already exists.", status.HTTP_409_CONFLICT)
        except Exception as e:
            return error_response(ErrorCode.COMPANY_CREATE_FAILED, str(e))


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsRecruiter]
    queryset = Company.objects.select_related('recruiter').all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        try:
            kwargs['partial'] = True
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return error_response(ErrorCode.COMPANY_UPDATE_FAILED, str(e))

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return error_response(ErrorCode.COMPANY_DELETE_FAILED, str(e))


# ─────────────────────────────────────────────────────────────────
# Company Follow / Unfollow
# ─────────────────────────────────────────────────────────────────

class FollowCompanyView(generics.CreateAPIView):
    """Candidate follows a company."""
    serializer_class = CompanyFollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(candidate=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return error_response(ErrorCode.VALIDATION_ERROR, "You already follow this company.", status.HTTP_409_CONFLICT)
        except Exception as e:
            return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


class UnfollowCompanyView(generics.DestroyAPIView):
    """Candidate unfollows a company."""
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return CompanyFollow.objects.filter(candidate=self.request.user)


class MyFollowedCompaniesView(generics.ListAPIView):
    """List all companies the current user follows."""
    serializer_class = CompanyFollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CompanyFollow.objects.filter(candidate=self.request.user).select_related('company')
