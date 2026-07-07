"""
Tests for the File Download page
(https://practice-automation.com/file-download/).

Verifies:
1. Normal (unlocked) download button is present and has a valid URL
2. Password-protected download flow — clicking the locked button opens
   a lock iframe, accepting the correct password shows a success message,
   while an incorrect password is rejected.
"""

import pytest
import requests
from selenium.webdriver.support import expected_conditions as EC
import config


# ──────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────


def test_normal_download_button_present(file_download_page):
    """The normal (unlocked) download button is visible and contains a
    data-downloadurl attribute pointing to a real resource."""
    btn = file_download_page.find_element(file_download_page.NORMAL_DOWNLOAD_LINK)
    assert btn.is_displayed(), "Normal download button should be visible"

    download_url = btn.get_attribute("data-downloadurl")
    assert download_url, "data-downloadurl attribute should be present"
    assert download_url.startswith("https://practice-automation.com/"), (
        f"Unexpected download URL: {download_url}"
    )


def test_normal_download_url_reachable(file_download_page):
    """The download URL behind the normal button is a valid downloadable
    resource (returns a 200 status with a PDF-like content-type)."""
    download_url = file_download_page.get_normal_download_url()
    assert download_url, "No download URL found"

    resp = requests.get(download_url, timeout=15, allow_redirects=True)
    assert resp.status_code == 200, (
        f"Download URL returned HTTP {resp.status_code}"
    )
    content_type = resp.headers.get("Content-Type", "")
    assert "pdf" in content_type.lower() or "octet-stream" in content_type.lower(), (
        f"Unexpected Content-Type: {content_type}"
    )


def test_locked_download_opens_lock_iframe(file_download_page):
    """Clicking the password-protected Download button should display
    the WPDM lock iframe with a password input."""
    file_download_page.click_locked_download()

    assert file_download_page.is_lock_iframe_present(), (
        "Lock iframe did not appear after clicking locked download"
    )

    # Switch into the iframe and verify the password input becomes visible
    file_download_page.switch_to_lock_iframe()
    file_download_page.wait.until(
        EC.visibility_of_element_located(file_download_page.IFRAME_PASSWORD_INPUT)
    )

    file_download_page.switch_to_default_content()


def test_locked_download_wrong_password_rejected(file_download_page):
    """Entering an incorrect password into the lock iframe should not
    show the success message."""
    file_download_page.click_locked_download()
    assert file_download_page.is_lock_iframe_present(), "Lock iframe did not appear"

    file_download_page.switch_to_lock_iframe()
    file_download_page.enter_password_in_iframe("wrongpassword")
    file_download_page.submit_password_in_iframe()

    assert file_download_page.is_wrong_password_error_in_iframe(
        timeout=15
    ), "Wrong-password error did not appear within 15s"
    assert not file_download_page.is_password_verified_in_iframe(
        timeout=3
    ), "Password was verified despite using wrong password"

    file_download_page.switch_to_default_content()


def test_locked_download_correct_password_unlocks(file_download_page):
    """Entering the correct password into the lock iframe should show
    the 'Your Download Link is Ready' message and reveal the
    start-download link."""
    file_download_page.click_locked_download()
    assert file_download_page.is_lock_iframe_present(), "Lock iframe did not appear"

    file_download_page.switch_to_lock_iframe()
    file_download_page.enter_password_in_iframe(config.DOWNLOAD_PASSWORD)
    file_download_page.submit_password_in_iframe()

    assert file_download_page.is_password_verified_in_iframe(), (
        "Password verification success message did not appear"
    )

    link_visible = file_download_page.wait.until(
        lambda _: file_download_page.driver.find_element(
            *file_download_page.IFRAME_START_DOWNLOAD_LINK
        ).is_displayed()
    )
    assert link_visible, (
        "Start download link is not visible after password verification"
    )

    file_download_page.switch_to_default_content()


def test_full_unlock_flow(file_download_page):
    """End-to-end: perform the full unlock flow via the convenience
    helper method — should not raise."""
    file_download_page.unlock_password_protected_download(config.DOWNLOAD_PASSWORD)
