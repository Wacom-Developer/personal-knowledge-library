# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""
Integration tests for AsyncInkServices.

These tests verify the ink export functionality using the async client.
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
import pytest_asyncio

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
from knowledge.services.asyncio.ink import AsyncInkServices
from knowledge.services.asyncio.users import AsyncUserManagementService
from knowledge.services.base import WacomServiceException, format_exception
from knowledge.services.users import UserRole, User

# ================================================================================================
# Format Validation Helpers
# ================================================================================================

# Magic bytes for file format detection
PNG_MAGIC: bytes = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC: bytes = b"\xff\xd8\xff"
PDF_MAGIC: bytes = b"%PDF"


def is_valid_png(data: bytes) -> Tuple[bool, str]:
    """
    Validate PNG format by checking magic bytes.

    Parameters
    ----------
    data: bytes
        The byte data to validate.

    Returns
    -------
    Tuple[bool, str]
        (is_valid, error_message)
    """
    if len(data) < 8:
        return False, f"Data too short for PNG: {len(data)} bytes"
    if data[:8] != PNG_MAGIC:
        return False, f"Invalid PNG magic bytes: {data[:8].hex()}"
    return True, ""


def is_valid_jpeg(data: bytes) -> Tuple[bool, str]:
    """
    Validate JPEG format by checking magic bytes.

    Parameters
    ----------
    data: bytes
        The byte data to validate.

    Returns
    -------
    Tuple[bool, str]
        (is_valid, error_message)
    """
    if len(data) < 3:
        return False, f"Data too short for JPEG: {len(data)} bytes"
    if data[:3] != JPEG_MAGIC:
        return False, f"Invalid JPEG magic bytes: {data[:3].hex()}"
    return True, ""


def is_valid_svg(data: bytes) -> Tuple[bool, str]:
    """
    Validate SVG format by checking for XML/SVG content.

    Parameters
    ----------
    data: bytes
        The byte data to validate.

    Returns
    -------
    Tuple[bool, str]
        (is_valid, error_message)
    """
    if len(data) < 10:
        return False, f"Data too short for SVG: {len(data)} bytes"

    try:
        # SVG is XML-based, decode as UTF-8
        text = data[:1000].decode("utf-8", errors="ignore").lower()
        # Check for XML declaration or SVG element
        if "<?xml" in text or "<svg" in text:
            return True, ""
        return False, "SVG content not found (no <?xml or <svg tag)"
    except Exception as e:
        return False, f"Failed to parse SVG: {e}"


def is_valid_pdf(data: bytes) -> Tuple[bool, str]:
    """
    Validate PDF format by checking magic bytes.

    Parameters
    ----------
    data: bytes
        The byte data to validate.

    Returns
    -------
    Tuple[bool, str]
        (is_valid, error_message)
    """
    if len(data) < 4:
        return False, f"Data too short for PDF: {len(data)} bytes"
    if data[:4] != PDF_MAGIC:
        return False, f"Invalid PDF magic bytes: {data[:4].hex()}"
    return True, ""


# ================================================================================================

# Root directory of the project
root_dir: Path = Path(__file__).parent.parent
logger = loguru.logger

# Paths for test files
UIM_PATH: Path = Path(root_dir / "uims" / "text" / "en_US")
OUTPUT_PATH: Path = Path(root_dir / "test-runs" / "output" / datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
LIMIT: int = 100


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


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def export_service():
    """
    Create and setup the async ink services client with user authentication.

    This fixture:
    1. Creates an AsyncUserManagementService and AsyncInkServices client
    2. Creates a test user
    3. Logs in the export service with the test user
    4. Yields the logged-in export service
    5. Cleans up: logs out and deletes the test user
    """
    instance_url = get_instance_url()
    tenant_api_key = get_tenant_api_key()

    # Create output directory
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Create services
    user_management = AsyncUserManagementService(
        service_url=instance_url, application_name="ink-services-test-user-mgmt"
    )

    export_svc = AsyncInkServices(
        service_url=instance_url,
        service_endpoint="v1/exports",
        application_name="ink-services-test",
    )

    # Create test user
    external_id = str(uuid.uuid4())
    user, token, refresh_token, expire = await user_management.create_user(
        tenant_api_key,
        external_id=external_id,
        meta_data={"account-type": "qa-test"},
        roles=[UserRole.USER],
    )
    logger.info(f"Created test user: {external_id}")

    # Login the export service with the test user credentials
    await export_svc.register_token(auth_key=token, refresh_token=refresh_token)
    logger.info(f"Export service logged in with user: {external_id}")

    # Yield the logged-in service for tests
    yield export_svc

    # Cleanup: logout and delete test users
    logger.info("Starting cleanup...")

    try:
        await export_svc.logout()
        logger.info("Export service logged out")
    except Exception as e:
        logger.error(f"Error during logout: {e}")

    # Delete all qa-test users
    try:
        list_user_all: List[User] = await user_management.listing_users(tenant_api_key, limit=LIMIT)
        for u_i in list_user_all:
            if "account-type" in u_i.meta_data and u_i.meta_data.get("account-type") == "qa-test":
                logger.info(f"Deleting test user: {u_i.external_user_id}")
                try:
                    await user_management.delete_user(
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


class TestExportFlow:
    """
    Test class for ink export functionality.

    Tests various export formats: PNG, JPG, SVG, PDF (vector and raster).
    The export_service fixture handles user creation, login, and cleanup.
    """

    @pytest.mark.asyncio
    async def test_export_png(
        self,
        export_service: AsyncInkServices,
        output_path: Path,
        uim_files: List[Path],
    ):
        """Test exporting UIM files to PNG format."""
        test_output_path = output_path / "png"
        test_output_path.mkdir(parents=True, exist_ok=True)

        for file in uim_files:
            with file.open("rb") as f:
                content: bytes = f.read()
                # No auth_key needed - service uses its session
                results: bytes = await export_service.convert_to(content, ExportFormat.PNG)
                output_file = test_output_path / f"{file.name}.png"
                with output_file.open("wb") as fp:
                    fp.write(results)
                assert output_file.exists(), f"Output file not created: {output_file}"
                assert output_file.stat().st_size > 0, f"Output file is empty: {output_file}"
                # Validate PNG format
                is_valid, error_msg = is_valid_png(results)
                assert is_valid, f"Invalid PNG format for {file.name}: {error_msg}"

    @pytest.mark.asyncio
    async def test_export_jpg(
        self,
        export_service: AsyncInkServices,
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
                    results: bytes = await export_service.convert_to(content, ExportFormat.JPG)
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

    @pytest.mark.asyncio
    async def test_export_svg(
        self,
        export_service: AsyncInkServices,
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
                    results: bytes = await export_service.convert_to(content, ExportFormat.SVG)
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

    @pytest.mark.asyncio
    async def test_export_pdf_vector(
        self,
        export_service: AsyncInkServices,
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
                    results: bytes = await export_service.convert_to_pdf(content, PDFType.VECTOR)
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

    @pytest.mark.asyncio
    async def test_export_pdf_raster(
        self,
        export_service: AsyncInkServices,
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
                    results: bytes = await export_service.convert_to_pdf(content, PDFType.RASTER)
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

    @pytest.mark.asyncio
    @pytest.mark.skipif(not HAS_UIM, reason="UIM package not available (Python 3.13+ compatibility)")
    async def test_hwr_text_en_us_myscript(
        self,
        export_service: AsyncInkServices,
    ):
        """Test handwriting recognition for English text using MyScript provider."""
        text_en_path: Path = root_dir / "uims" / "text" / "en_US"
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
                    hwr_result: bytes = await export_service.perform_ink_to_text(
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

    @pytest.mark.asyncio
    @pytest.mark.skipif(not HAS_UIM, reason="UIM package not available (Python 3.13+ compatibility)")
    async def test_hwr_text_ja_JP_ilabo(
        self,
        export_service: AsyncInkServices,
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
                hwr_result: bytes = await export_service.perform_ink_to_text(
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

    @pytest.mark.asyncio
    @pytest.mark.skipif(not HAS_UIM, reason="UIM package not available (Python 3.13+ compatibility)")
    async def test_math_recognition_myscript(
        self,
        export_service: AsyncInkServices,
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
                    math_result: bytes = await export_service.perform_ink_to_math(
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

    @pytest.mark.asyncio
    @pytest.mark.skipif(not HAS_UIM, reason="UIM package not available (Python 3.13+ compatibility)")
    async def test_math_recognition_ilabo(
        self,
        export_service: AsyncInkServices,
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
                    math_result: bytes = await export_service.perform_ink_to_math(
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
