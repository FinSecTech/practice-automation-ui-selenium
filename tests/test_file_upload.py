"""
Tests for the File Upload page
(https://practice-automation.com/file-upload/).

Verifies that each supported file type (txt, docx, pdf, jpeg, png, jpg,
gif) can be uploaded successfully, and that unsupported file types are
rejected with a validation error.
"""

import os
import pytest
from pages.file_upload_page import FileUploadPage

# Absolute path to the test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "upload_test_data")
TEST_DATA_DIR = os.path.normpath(os.path.abspath(TEST_DATA_DIR))

# Every supported file type
SUPPORTED_FILES = [
    "test.txt",
    "test.docx",
    "test.pdf",
    "test.jpeg",
    "test.png",
    "test.jpg",
    "test.gif",
]


class TestFileUpload:
    """Test suite for the File Upload page."""

    @pytest.mark.parametrize("filename", SUPPORTED_FILES)
    def test_upload_supported_file(self, file_upload_page: FileUploadPage, filename: str):
        """Each supported file type uploads successfully and triggers a
        success response."""
        page = file_upload_page
        file_path = os.path.join(TEST_DATA_DIR, filename)

        assert os.path.exists(file_path), f"Test file not found: {file_path}"

        page.upload_file(file_path)

        assert page.wait_for_response(), "No response after upload"
        assert page.is_response_success(), (
            f"Upload of '{filename}' was not successful. "
            f"Response: '{page.response_text}'"
        )

    def test_upload_unsupported_file_rejected(self, file_upload_page: FileUploadPage):
        """An unsupported file type triggers a validation error and the
        form shows 'invalid' status."""
        page = file_upload_page

        # Create a temporary .exe file (not in the accepted list)
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=".exe", delete=False)
        tmp.write(b"fake executable content")
        tmp.close()

        try:
            page.select_file(tmp.name)
            page.click_upload()
            page.wait_for_response()

            assert page.is_response_error(), (
                "Form should be in 'invalid' state for unsupported file type"
            )
            error_text = page.get_validation_error_text()
            assert "not allowed" in error_text.lower(), (
                f"Expected validation error about file type, got: '{error_text}'"
            )
        finally:
            os.unlink(tmp.name)
