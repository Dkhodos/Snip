"""Tests for domain exceptions."""

from dashboard_backend.exceptions import (
    AuthenticationError,
    DomainError,
    InvalidSortFieldError,
    LinkExpiredError,
    LinkNotFoundError,
    OrganizationRequiredError,
    ShortCodeCollisionError,
)


class TestExceptions:
    def test_domain_error_is_base(self) -> None:
        assert issubclass(LinkNotFoundError, DomainError)
        assert issubclass(LinkExpiredError, DomainError)
        assert issubclass(ShortCodeCollisionError, DomainError)
        assert issubclass(InvalidSortFieldError, DomainError)
        assert issubclass(AuthenticationError, DomainError)
        assert issubclass(OrganizationRequiredError, DomainError)

    def test_default_messages(self) -> None:
        assert LinkNotFoundError().detail == "Link not found"
        assert LinkExpiredError().detail == "Link has expired"
        assert ShortCodeCollisionError().detail == "Short code already in use"
        assert AuthenticationError().detail == "Authentication failed"
        assert "organization" in OrganizationRequiredError().detail.lower()

    def test_custom_messages(self) -> None:
        e = LinkNotFoundError("custom msg")
        assert e.detail == "custom msg"

    def test_invalid_sort_field(self) -> None:
        e = InvalidSortFieldError({"a", "b", "c"})
        assert "a" in e.detail
        assert "b" in e.detail
        assert "c" in e.detail
