"""Base test case with async transactional rollback per test.

Each test runs inside a transaction that is rolled back after the test,
so no data leaks between tests and no cleanup is needed.

Usage:
    class TestLinkStore(BaseDBTestCase):
        async def test_create(self) -> None:
            store = LinkStore(self.session)
            link = await store.create(org_id="org1", ...)
            assert link.id is not None
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.usefixtures("_db_session")
class BaseDBTestCase:
    """Inherit from this class for tests that need a real async database session.

    ``self.session`` is available in every test method — it is rolled back
    automatically after each test so tests are fully isolated.
    """

    session: AsyncSession

    @pytest.fixture(autouse=True)
    async def _inject_session(self, _db_session: AsyncSession) -> None:
        self.session = _db_session
