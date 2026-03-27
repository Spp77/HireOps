"""
apps/common/throttles.py
─────────────────────────────────────────────────────────────────
Role-aware throttle classes.

Burst:     short window (per-minute) — protects against request spikes
Sustained: long window  (per-day)   — protects against crawlers

Recruiters get their own higher limit since they legitimately make
more write requests (job postings, status updates, etc.).
"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


# ── Anonymous client throttles ────────────────────────────────────

class AnonBurstThrottle(AnonRateThrottle):
    scope = 'anon_burst'


class AnonSustainedThrottle(AnonRateThrottle):
    scope = 'anon_sustained'


# ── Authenticated user throttles ──────────────────────────────────

class UserBurstThrottle(UserRateThrottle):
    scope = 'user_burst'


class UserSustainedThrottle(UserRateThrottle):
    scope = 'user_sustained'


class RecruiterBurstThrottle(UserRateThrottle):
    """Higher limit for recruiters on write-heavy endpoints."""
    scope = 'recruiter_burst'

    def allow_request(self, request, view):
        # Fallback to standard user throttle if not a recruiter
        from apps.accounts.models import User
        if request.user.is_authenticated and request.user.role != User.Role.RECRUITER:
            self.scope = 'user_burst'
        return super().allow_request(request, view)
