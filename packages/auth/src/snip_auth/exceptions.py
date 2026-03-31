"""Auth domain exceptions."""


class AuthError(Exception):
    """Base class for all auth exceptions."""


class AuthenticationError(AuthError):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Authentication failed") -> None:
        super().__init__(detail)
        self.detail = detail


class OrganizationRequiredError(AuthError):
    """Raised when no organization is selected."""

    def __init__(
        self,
        detail: str = "No organization selected. Please select or create an organization.",
    ) -> None:
        super().__init__(detail)
        self.detail = detail
