"""Domain exceptions for dashboard backend.

These exceptions are raised by managers and stores.
Routers catch them and map to appropriate HTTP responses.
"""


class DomainError(Exception):
    """Base class for all domain exceptions."""


class LinkNotFoundError(DomainError):
    """Raised when a link cannot be found or doesn't belong to the org."""

    def __init__(self, detail: str = "Link not found") -> None:
        super().__init__(detail)
        self.detail = detail


class LinkExpiredError(DomainError):
    """Raised when a link has expired."""

    def __init__(self, detail: str = "Link has expired") -> None:
        super().__init__(detail)
        self.detail = detail


class ShortCodeCollisionError(DomainError):
    """Raised when a short code already exists."""

    def __init__(self, detail: str = "Short code already in use") -> None:
        super().__init__(detail)
        self.detail = detail


class InvalidSortFieldError(DomainError):
    """Raised when an invalid sort field is requested."""

    def __init__(self, allowed: set[str]) -> None:
        detail = f"sort_by must be one of: {', '.join(sorted(allowed))}"
        super().__init__(detail)
        self.detail = detail


class AuthenticationError(DomainError):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Authentication failed") -> None:
        super().__init__(detail)
        self.detail = detail


class OrganizationRequiredError(DomainError):
    """Raised when no organization is selected."""

    def __init__(
        self,
        detail: str = "No organization selected. Please select or create an organization.",
    ) -> None:
        super().__init__(detail)
        self.detail = detail
