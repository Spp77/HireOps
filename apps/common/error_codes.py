class ErrorCode:
    """
    Centralized error codes for the application.
    These codes are returned in API error responses to allow frontends
    to handle specific error states programmatically without parsing strings.
    """
    # ── General ──────────────────────────────────────────────────────
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    NOT_FOUND = "NOT_FOUND"
    SERVER_ERROR = "SERVER_ERROR"

    # ── Accounts ─────────────────────────────────────────────────────
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    REGISTER_FAILED = "REGISTER_FAILED"

    # ── Companies ────────────────────────────────────────────────────
    COMPANY_ALREADY_EXISTS = "COMPANY_ALREADY_EXISTS"
    COMPANY_CREATE_FAILED = "COMPANY_CREATE_FAILED"
    COMPANY_UPDATE_FAILED = "COMPANY_UPDATE_FAILED"
    COMPANY_DELETE_FAILED = "COMPANY_DELETE_FAILED"

    # ── Jobs ─────────────────────────────────────────────────────────
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    JOB_CREATE_FAILED = "JOB_CREATE_FAILED"
    JOB_UPDATE_FAILED = "JOB_UPDATE_FAILED"
    JOB_DELETE_FAILED = "JOB_DELETE_FAILED"