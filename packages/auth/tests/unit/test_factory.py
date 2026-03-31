"""Tests for auth client factory."""

import pytest

from snip_auth.factory import create_auth_client
from snip_auth.provider import AuthProvider
from snip_auth.providers.clerk.client import ClerkClient
from snip_auth.providers.dev.client import DevAuthClient


class TestCreateAuthClient:
    def test_dev_provider(self) -> None:
        client = create_auth_client(AuthProvider.DEV)
        assert isinstance(client, DevAuthClient)

    def test_clerk_provider(self) -> None:
        client = create_auth_client(AuthProvider.CLERK, publishable_key="pk_test_abc")
        assert isinstance(client, ClerkClient)

    def test_clerk_requires_publishable_key(self) -> None:
        with pytest.raises(ValueError, match="publishable_key"):
            create_auth_client(AuthProvider.CLERK)

    def test_clerk_empty_publishable_key(self) -> None:
        with pytest.raises(ValueError, match="publishable_key"):
            create_auth_client(AuthProvider.CLERK, publishable_key="")
