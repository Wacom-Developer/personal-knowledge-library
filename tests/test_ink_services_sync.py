# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom. All rights reserved.
"""
Integration tests for InkServices (synchronous client).

These tests verify the ink export functionality using the synchronous client.
Requires environment variables:
    - INSTANCE: URL of the service instance
    - TENANT_API_KEY: Tenant API key for authentication
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import loguru
import pytest

from knowledge.base.ink import ExportFormat, PDFType, Schema, Provider
from knowledge.base.language import JA_JP

# UIM imports - may fail on Python 3.13+ due to removed 'chunk' module
try:
    from uim.codec.parser.uim import UIMParser
    from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
    from uim.model.ink import InkModel

    HAS_UIM = True
except ImportError:
    HAS_UIM = False
    UIMParser = None
    UIMEncoder310 = None
    InkModel = None
from knowledge.services.ink import InkServices
from knowledge.services.base import WacomServiceException, format_exception
from knowledge.services.users import UserRole, UserManagementServiceAPI, User

# Root directory of the project
root_dir: Path = Path(__file__).parent.parent
logger = loguru.logger

# Paths for test files
UIM_PATH: Path = Path(root_dir / "uims" / "text" / "en_US")
OUTPUT_PATH: Path = Path(root_dir / "test-runs" / "output-sync" / datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
LIMIT: int = 100


# ================================================================================================
# Format Validation Helpers
# ================================================================================================

PNG_MAGIC: bytes = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC: bytes = b"\xff\xd8\xff"
PDF_MAGIC: bytes = b"%PDF"


def is_valid_png(data: bytes) -> Tuple[bool, str]:
    """Validate PNG format by checking magic bytes."""
    if len(data) < 8:
        return False, f"Data too short for PNG: {len(data)} bytes"
    if data[:8] != PNG_MAGIC:
        return False, f"Invalid PNG magic bytes: {data[:8].hex()}"
    return True, ""


def is_valid_jpeg(data: bytes) -> Tuple[bool, str]:
    """Validate JPEG format by checking magic bytes."""
    if len(data) < 3:
        return False, f"Data too short for JPEG: {len(data)} bytes"
    if data[:3] != JPEG_MAGIC:
        return False, f"Invalid JPEG magic bytes: {data[:3].hex()}"
    return True, ""


def is_valid_svg(data: bytes) -> Tuple[bool, str]:
    """Validate SVG format by checking for XML/SVG content."""
    if len(data) < 10:
        return False, f"Data too short for SVG: {len(data)} bytes"
    try:
        text = data[:1000].decode("utf-8", errors="ignore").lower()
        if "<?xml" in text or "<svg" in text:
            return True, ""
        return False, "SVG content not found (no <?xml or <svg tag)"
    except Exception as e:
        return False, f"Failed to parse SVG: {e}"


def is_valid_pdf(data: bytes) -> Tuple[bool, str]:
    """Validate PDF format by checking magic bytes."""
    if len(data) < 4:
        return False, f"Data too short for PDF: {len(data)} bytes"
    if data[:4] != PDF_MAGIC:
        return False, f"Invalid PDF magic bytes: {data[:4].hex()}"
    return True, ""


# ================================================================================================
# Fixtures
# ================================================================================================


def get_tenant_api_key() -> str:
    """Get tenant API key from environment."""
    key = os.environ.get("TENANT_API_KEY")
    if not key:
        pytest.skip("TENANT_API_KEY environment variable not set")
    return key


def get_instance_url() -> str:
    """Get instance URL from environment."""
    url = os.environ.get("INSTANCE")
    if not url:
        pytest.skip("INSTANCE environment variable not set")
    return url


def get_uim_files() -> List[Path]:
    """Get list of UIM test files."""
    if not UIM_PATH.exists():
        pytest.skip(f"UIM test files not found at {UIM_PATH}")
    files = list(UIM_PATH.glob("*.uim"))
    if not files:
        pytest.skip(f"No .uim files found in {UIM_PATH}")
    return files


@pytest.fixture(scope="module")
def ink_service():
    """
    Create and setup the synchronous ink services client with user authentication.

    This fixture:
    1. Creates a UserManagementServiceAPI and InkServices client
    2. Creates a test user
    3. Logs in the ink service with the test user
    4. Yields the logged-in ink service
    5. Cleans up: deletes the test user
    """
    instance_url = get_instance_url()
    tenant_api_key = get_tenant_api_key()

    # Create output directory
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Create services
    user_management = UserManagementServiceAPI(service_url=instance_url)

    ink_svc = InkServices(
        service_url=instance_url,
        service_endpoint="v1/exports",
        application_name="ink-services-sync-test",
    )

    # Create test user
    external_id = str(uuid.uuid4())
    user, token, refresh_token, expire = user_management.create_user(
        tenant_api_key,
        external_id=external_id,
        meta_data={"account-type": "qa-test-sync"},
        roles=[UserRole.USER],
    )
    logger.info(f"Created test user: {external_id}")

    # Login the ink service with the test user credentials
    ink_svc.register_token(auth_key=token, refresh_token=refresh_token)
    logger.info(f"Ink service logged in with user: {external_id}")

    # Yield the logged-in service for tests
    yield ink_svc

    # Cleanup: delete test users
    logger.info("Starting cleanup...")

    try:
        list_user_all: List[User] = user_management.listing_users(tenant_api_key, limit=LIMIT)
        for u_i in list_user_all:
            if "account-type" in u_i.meta_data and u_i.meta_data.get("account-type") == "qa-test-sync":
                logger.info(f"Deleting test user: {u_i.external_user_id}")
                try:
                    user_management.delete_user(
                        tenant_api_key,
                        external_id=u_i.external_user_id,
                        internal_id=u_i.id,
                        force=True,
                    )
                except WacomServiceException as we:
                    logger.error(f"Error deleting user {u_i.external_user_id}: {we}")
    except Exception as e:
        logger.error(f"Error during user cleanup: {e}")


@pytest.fixture(scope="module")
def output_path() -> Path:
    """Return output path for test results."""
    return OUTPUT_PATH


@pytest.fixture(scope="module")
def uim_files() -> List[Path]:
    """Get list of UIM test files."""
    return get_uim_files()


# ================================================================================================
# Test Class
# ================================================================================================


class TestInkServicesSync:
    """
    Test class for synchronous ink export functionality.

    Tests various export formats: PNG, JPG, SVG, PDF (vector and raster).
    The ink_service fixture handles user creation, login, and cleanup.
    """

    def test_export_png(
        self,
        ink_service: InkServices,
        output_path: Path,
        uim_files: List[Path],
    ):
        """Test exporting UIM files to PNG format."""
        test_output_path = output_path / "png"
        test_output_path.mkdir(parents=True, exist_ok=True)

        for file in uim_files:
            with file.open("rb") as f:
                content: bytes = f.read()
                results: bytes = ink_service.convert_to(content, ExportFormat.PNG)
                output_file = test_output_path / f"{file.name}.png"
                with output_file.open("wb") as fp:
                    fp.write(results)

                assert output_file.exists(), f"Output file not created: {output_file}"
                assert output_file.stat().st_size > 0, f"Output file is empty: {output_file}"

                # Validate PNG format
                is_valid, error_msg = is_valid_png(results)
                assert is_valid, f"Invalid PNG format for {file.name}: {error_msg}"

    def test_export_jpg(
        self,
        ink_service: InkServices,
        output_path: Path,
        uim_files: List[Path],
    ):
        """Test exporting UIM files to JPG format."""
        test_output_path = output_path / "jpg"
        test_output_path.mkdir(parents=True, exist_ok=True)

        for file in uim_files:
            with file.open("rb") as f:
                content: bytes = f.read()
                try:
                    results: bytes = ink_service.convert_to(content, ExportFormat.JPG)
                    output_file = test_output_path / f"{file.name}.jpg"
                    with output_file.open("wb") as fp:
                        fp.write(results)

                    assert output_file.exists(), f"Output file not created: {output_file}"
                    assert output_file.stat().st_size > 0, f"Output file is empty: {output_file}"

                    # Validate JPEG format
                    is_valid, error_msg = is_valid_jpeg(results)
                    assert is_valid, f"Invalid JPEG format for {file.name}: {error_msg}"
                except WacomServiceException as e:
                    pytest.fail(format_exception(e))

    def test_export_svg(
        self,
        ink_service: InkServices,
        output_path: Path,
        uim_files: List[Path],
    ):
        """Test exporting UIM files to SVG format."""
        test_output_path = output_path / "svg"
        test_output_path.mkdir(parents=True, exist_ok=True)

        for file in uim_files:
            with file.open("rb") as f:
                content: bytes = f.read()
                try:
                    results: bytes = ink_service.convert_to(content, ExportFormat.SVG)
                    output_file = test_output_path / f"{file.name}.svg"
                    with output_file.open("wb") as fp:
                        fp.write(results)

                    assert output_file.exists(), f"Output file not created: {output_file}"
                    assert output_file.stat().st_size > 0, f"Output file is empty: {output_file}"

                    # Validate SVG format
                    is_valid, error_msg = is_valid_svg(results)
                    assert is_valid, f"Invalid SVG format for {file.name}: {error_msg}"
                except WacomServiceException as e:
                    pytest.fail(format_exception(e))

    def test_export_pdf_vector(
        self,
        ink_service: InkServices,
        output_path: Path,
        uim_files: List[Path],
    ):
        """Test exporting UIM files to PDF (vector) format."""
        test_output_path = output_path / "pdf-vector"
        test_output_path.mkdir(parents=True, exist_ok=True)

        for file in uim_files:
            with file.open("rb") as f:
                content: bytes = f.read()
                try:
                    results: bytes = ink_service.convert_to_pdf(content, PDFType.VECTOR)
                    output_file = test_output_path / f"{file.name}.pdf"
                    with output_file.open("wb") as fp:
                        fp.write(results)

                    assert output_file.exists(), f"Output file not created: {output_file}"
                    assert output_file.stat().st_size > 0, f"Output file is empty: {output_file}"

                    # Validate PDF format
                    is_valid, error_msg = is_valid_pdf(results)
                    assert is_valid, f"Invalid PDF format for {file.name}: {error_msg}"
                except WacomServiceException as e:
                    pytest.fail(format_exception(e))

    def test_export_pdf_raster(
        self,
        ink_service: InkServices,
        output_path: Path,
        uim_files: List[Path],
    ):
        """Test exporting UIM files to PDF (raster) format."""
        test_output_path = output_path / "pdf-raster"
        test_output_path.mkdir(parents=True, exist_ok=True)

        for file in uim_files:
            with file.open("rb") as f:
                content: bytes = f.read()
                try:
                    results: bytes = ink_service.convert_to_pdf(content, PDFType.RASTER)
                    output_file = test_output_path / f"{file.name}.pdf"
                    with output_file.open("wb") as fp:
                        fp.write(results)

                    assert output_file.exists(), f"Output file not created: {output_file}"
                    assert output_file.stat().st_size > 0, f"Output file is empty: {output_file}"

                    # Validate PDF format
                    is_valid, error_msg = is_valid_pdf(results)
                    assert is_valid, f"Invalid PDF format for {file.name}: {error_msg}"
                except WacomServiceException as e:
                    pytest.fail(format_exception(e))

    @pytest.mark.skipif(not HAS_UIM, reason="UIM package not available (Python 3.13+ compatibility)")
    def test_hwr_text_en_US_myscript(
        self,
        ink_service: InkServices,
    ):
        """Test handwriting recognition for English text using MyScript provider."""
        text_en_path = root_dir / "uims" / "text" / "en_US"
        uim_files = [
            "1) Value of Ink.uim",
            "2) Digital Ink is processable.uim",
            "3) Digital Ink.uim",
        ]

        for uim in uim_files:
            uim_path = text_en_path / uim
            if not uim_path.exists():
                pytest.skip(f"Test file not found: {uim_path}")

            with uim_path.open("rb") as f:
                content: bytes = f.read()
                before: InkModel = UIMParser().parse(content)
                before.clear_knowledge_graph()
                if before.has_tree("hwr"):
                    before.remove_tree("hwr")

                assert len(before.strokes) > 1, f"Expected strokes in {uim}"
                assert not before.has_tree("hwr"), f"HWR tree should not exist in {uim}"
                assert len(before.knowledge_graph.statements) == 0, f"Knowledge graph should be empty in {uim}"

                try:
                    hwr_result: bytes = ink_service.perform_ink_to_text(
                        UIMEncoder310().encode(before),
                        schema=Schema.SEGMENTATION_V03,
                        provider=Provider.MYSCRIPT,
                    )
                    after: InkModel = UIMParser().parse(hwr_result)
                    assert after.has_tree("hwr"), f"HWR tree should exist after recognition in {uim}"
                    assert len(after.knowledge_graph.statements) > 1, f"Knowledge graph should have statements in {uim}"
                    logger.info(f"HWR en_US MyScript passed for {uim}")
                except WacomServiceException as e:
                    pytest.fail(format_exception(e))

    @pytest.mark.skipif(not HAS_UIM, reason="UIM package not available (Python 3.13+ compatibility)")
    def test_hwr_text_ja_JP_ilabo(
        self,
        ink_service: InkServices,
    ):
        """Test handwriting recognition for Japanese text using iLabo provider."""
        text_ja_path = root_dir / "uims" / "text" / "ja_JP"
        uim_path = text_ja_path / "1.uim"

        if not uim_path.exists():
            pytest.skip(f"Test file not found: {uim_path}")

        with uim_path.open("rb") as f:
            content: bytes = f.read()
            before: InkModel = UIMParser().parse(content)
            before.clear_knowledge_graph()
            encoded_content = UIMEncoder310().encode(before)

            assert len(before.strokes) > 1, "Expected strokes in Japanese UIM"
            assert not before.has_tree("hwr"), "HWR tree should not exist"

            try:
                hwr_result: bytes = ink_service.perform_ink_to_text(
                    encoded_content,
                    locale=JA_JP,
                    schema=Schema.SIMPLE_SEGMENTATION_V01,
                    provider=Provider.ILABO,
                )
                after: InkModel = UIMParser().parse(hwr_result)
                assert after.has_tree("hwr"), "HWR tree should exist after recognition"
                assert len(after.knowledge_graph.statements) > 1, "Knowledge graph should have statements"
                logger.info("HWR ja_JP iLabo passed")
            except WacomServiceException as e:
                pytest.fail(format_exception(e))

    @pytest.mark.skipif(not HAS_UIM, reason="UIM package not available (Python 3.13+ compatibility)")
    def test_math_recognition_myscript(
        self,
        ink_service: InkServices,
    ):
        """Test math recognition using MyScript provider."""
        math_en_path = root_dir / "uims" / "math" / "en_US"
        uim_files = ["math.uim", "numbers.uim"]

        for uim in uim_files:
            uim_path = math_en_path / uim
            if not uim_path.exists():
                pytest.skip(f"Test file not found: {uim_path}")

            with uim_path.open("rb") as f:
                content: bytes = f.read()
                before: InkModel = UIMParser().parse(content)
                before.clear_knowledge_graph()
                logger.info(f"Number of strokes in {uim}: {len(before.strokes)}")

                assert len(before.strokes) > 1, f"Expected strokes in {uim}"
                assert not before.has_tree("hwr"), f"HWR tree should not exist in {uim}"
                assert len(before.knowledge_graph.statements) == 0, f"Knowledge graph should be empty in {uim}"

                try:
                    math_result: bytes = ink_service.perform_ink_to_math(
                        UIMEncoder310().encode(before),
                        schema=Schema.MATH_STRUCTURES_V01,
                        provider=Provider.MYSCRIPT,
                    )
                    after: InkModel = UIMParser().parse(math_result)
                    assert after.has_tree("hwr"), f"HWR tree should exist after math recognition in {uim}"
                    assert len(after.knowledge_graph.statements) > 1, f"Knowledge graph should have statements in {uim}"
                    logger.info(f"Math recognition MyScript passed for {uim}")
                except WacomServiceException as e:
                    pytest.fail(format_exception(e))

    @pytest.mark.skipif(not HAS_UIM, reason="UIM package not available (Python 3.13+ compatibility)")
    def test_math_recognition_ilabo(
        self,
        ink_service: InkServices,
    ):
        """Test math recognition using iLabo provider."""
        math_en_path = root_dir / "uims" / "math" / "en_US"
        uim_files = ["math.uim", "numbers.uim"]

        for uim in uim_files:
            uim_path = math_en_path / uim
            if not uim_path.exists():
                pytest.skip(f"Test file not found: {uim_path}")

            with uim_path.open("rb") as f:
                content: bytes = f.read()
                before: InkModel = UIMParser().parse(content)
                before.clear_knowledge_graph()
                logger.info(f"Number of strokes in {uim}: {len(before.strokes)}")

                assert len(before.strokes) > 1, f"Expected strokes in {uim}"
                assert not before.has_tree("hwr"), f"HWR tree should not exist in {uim}"
                assert len(before.knowledge_graph.statements) == 0, f"Knowledge graph should be empty in {uim}"

                try:
                    math_result: bytes = ink_service.perform_ink_to_math(
                        UIMEncoder310().encode(before),
                        schema=Schema.SEGMENTATION_V03,
                        provider=Provider.ILABO,
                        timeout=120,
                    )
                    after: InkModel = UIMParser().parse(math_result)
                    assert after.has_tree("hwr"), f"HWR tree should exist after math recognition in {uim}"
                    assert len(after.knowledge_graph.statements) > 1, f"Knowledge graph should have statements in {uim}"
                    logger.info(f"Math recognition iLabo passed for {uim}")
                except WacomServiceException as e:
                    pytest.fail(format_exception(e))
