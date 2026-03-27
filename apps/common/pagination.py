"""
apps/common/pagination.py
─────────────────────────────────────────────────────────────────
Cursor-based pagination is preferred over OFFSET pagination for
large datasets because it doesn't require the DB to scan and skip
rows — every page is O(log n) using the index on created_at.

Use CursorPagination on all high-traffic list endpoints.
"""
from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response


class StandardCursorPagination(CursorPagination):
    """
    Default paginator — uses cursor on 'created_at', newest first.
    Stable for large tables (no OFFSET scans).
    """
    page_size             = 20
    page_size_query_param = 'page_size'
    max_page_size         = 100
    ordering              = '-created_at'

    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'next':     self.get_next_link(),
                'previous': self.get_previous_link(),
                'count':    None,    # cursor pagination doesn't scan for total count
            },
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'pagination': {
                    'type': 'object',
                    'properties': {
                        'next':     {'type': 'string', 'nullable': True},
                        'previous': {'type': 'string', 'nullable': True},
                    },
                },
                'results': schema,
            },
        }


class JobListPagination(StandardCursorPagination):
    """Slightly larger page for job browse endpoints."""
    page_size     = 25
    max_page_size = 200


class SmallResultsPagination(StandardCursorPagination):
    """Tight pagination for sub-resources like notifications."""
    page_size     = 10
    max_page_size = 50
