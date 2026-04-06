"""Tests for snip_og_image.models."""

from snip_og_image.models import OgImageData, SitePreview


class TestOgImageData:
    def test_is_frozen(self) -> None:
        data = OgImageData(
            title="Test",
            short_code="abc",
            click_count=0,
            redirect_base_url="http://localhost",
        )
        try:
            data.title = "changed"  # type: ignore[misc]
            raise AssertionError("should have raised FrozenInstanceError")
        except AssertionError:
            raise
        except Exception:
            pass

    def test_target_url_defaults_to_none(self) -> None:
        data = OgImageData(
            title=None,
            short_code="abc",
            click_count=0,
            redirect_base_url="http://localhost",
        )
        assert data.target_url is None


class TestSitePreview:
    def test_defaults_to_empty(self) -> None:
        preview = SitePreview()
        assert preview.thumbnail is None
        assert preview.favicon is None
        assert preview.domain == ""
