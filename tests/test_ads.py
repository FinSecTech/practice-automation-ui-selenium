"""
Tests for the Ads page (https://practice-automation.com/ads/).

Verifies:
1. The ad modal is visible on page load (auto-opened)
2. The modal title is "Hi"
3. The modal content is "I am an ad."
4. The close button works and hides the modal
"""


def test_ad_modal_visible_on_page_load(ads_page):
    """The ad modal should become visible after the auto-open delay."""
    ads_page.wait_for_ad_modal_visible()
    assert ads_page.is_ad_modal_visible(), (
        "Ad modal should be visible after the auto-open delay"
    )


def test_ad_modal_title(ads_page):
    """The ad modal title should be 'Hi'."""
    ads_page.wait_for_ad_modal_visible()
    assert ads_page.get_ad_modal_title() == "Hi", (
        "Ad modal title should be 'Hi'"
    )


def test_ad_modal_content(ads_page):
    """The ad modal content should be 'I am an ad.'."""
    ads_page.wait_for_ad_modal_visible()
    content = ads_page.get_ad_modal_content()
    assert content == "I am an ad.", (
        f"Ad modal content should be 'I am an ad.', got: {content}"
    )


def test_ad_modal_close(ads_page):
    """Closing the ad modal should hide it."""
    ads_page.wait_for_ad_modal_visible()
    assert ads_page.is_ad_modal_visible(), (
        "Ad modal should be visible before closing"
    )

    ads_page.close_ad_modal()

    assert ads_page.wait_for_ad_modal_closed(), (
        "Ad modal should be hidden after clicking close"
    )
