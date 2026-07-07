"""Tests for the Broken Images page — identify working vs. broken images."""

import pytest
from pages.broken_images_page import BrokenImagesPage


class TestBrokenImages:
    """Verify the page contains exactly 1 working image and 2 broken images."""

    def test_all_images_identified(self, broken_images_page: BrokenImagesPage):
        """There should be exactly 3 images on the page (1 working, 2 broken)."""
        images = broken_images_page.get_all_images()
        assert len(images) == 3, (
            f"Expected 3 images on the page, found {len(images)}"
        )

    def test_working_image_has_dimensions(self, broken_images_page: BrokenImagesPage):
        """The non-broken image should have non-zero natural dimensions."""
        working = broken_images_page.working_images
        assert len(working) == 1, (
            f"Expected exactly 1 working image, found {len(working)}"
        )
        img = working[0]
        assert img["natural_width"] > 0, (
            f"Working image has naturalWidth=0: {img['src']}"
        )
        assert img["natural_height"] > 0, (
            f"Working image has naturalHeight=0: {img['src']}"
        )

    def test_working_image_src_is_valid_image(self, broken_images_page: BrokenImagesPage):
        """The working image should point to a real image resource (JavaScript logo)."""
        working = broken_images_page.working_images
        src = working[0]["src"]
        assert "javascript-logo" in src or src.endswith((".jpg", ".png", ".jpeg", ".gif", ".svg")), (
            f"Working image src does not look like a valid image: {src}"
        )

    def test_two_broken_images(self, broken_images_page: BrokenImagesPage):
        """There should be exactly 2 broken images with naturalWidth=0."""
        broken = broken_images_page.broken_images
        assert len(broken) == 2, (
            f"Expected exactly 2 broken images, found {len(broken)}"
        )
        for img in broken:
            assert img["is_broken"] is True, f"Image marked as not broken: {img['src']}"
            assert img["natural_width"] == 0, (
                f"Broken image has non-zero naturalWidth: {img['src']}"
            )
            assert img["natural_height"] == 0, (
                f"Broken image has non-zero naturalHeight: {img['src']}"
            )

    def test_broken_images_have_relative_src(self, broken_images_page: BrokenImagesPage):
        """The broken images should reference relative paths (1.jpg, 2.jpg)."""
        broken = broken_images_page.broken_images
        for img in broken:
            src = img["src"]
            alt = img["alt"]
            assert not src.startswith("http"), (
                f"Broken image src looks absolute, expected relative: {src}"
            )
            assert alt and "broken" in alt.lower(), (
                f"Broken image alt text should indicate its broken state: '{alt}'"
            )

    def test_image_order_is_consistent(self, broken_images_page: BrokenImagesPage):
        """Verify the working image comes first, then broken images (1.jpg, 2.jpg)."""
        images = broken_images_page.get_all_images()
        assert len(images) == 3
        assert not images[0]["is_broken"], "First image (javascript-logo) should be working"
        assert images[1]["is_broken"], "Second image should be broken (1.jpg)"
        assert images[2]["is_broken"], "Third image should be broken (2.jpg)"
