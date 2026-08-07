"""Domain exceptions, translated to HTTP responses by the handlers
registered in app/main.py. Services raise these; routers never build
HTTPException directly, so the error contract stays consistent and
services stay web-framework-agnostic (reusable from Celery tasks etc).
"""


class DomainError(Exception):
    """Base class for all expected/business-level errors."""

    status_code = 400
    error_code = "domain_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(DomainError):
    status_code = 404
    error_code = "not_found"


class ConflictError(DomainError):
    status_code = 409
    error_code = "conflict"


class AuthenticationError(DomainError):
    status_code = 401
    error_code = "authentication_failed"


class AuthorizationError(DomainError):
    status_code = 403
    error_code = "forbidden"


class ValidationDomainError(DomainError):
    status_code = 422
    error_code = "validation_error"
