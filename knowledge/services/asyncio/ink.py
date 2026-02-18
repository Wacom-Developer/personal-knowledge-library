# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
from http import HTTPStatus
from typing import Dict, Optional, List

__all__ = ["AsyncInkServices"]

from knowledge.base.entity import LOCALE_TAG
from knowledge.base.ink import (
    Schema,
    Provider,
    Priority,
    PDFType,
    HWRMode,
    WritingOrientation,
    InkToXSettings,
    DEFAULT_INK_TO_X,
    ExportFormat,
)
from knowledge.base.language import LocaleCode, EN_US, JA_JP
from knowledge.services import DEFAULT_TIMEOUT
from knowledge.services.asyncio.base import (
    AsyncServiceAPIClient,
    AsyncSession,
    handle_error,
    ResponseData,
)


class AsyncInkServices(AsyncServiceAPIClient):
    """
    AsyncInkServices
    ----------------
    Async client for Wacom Ink Services.

    Provides operations for:
        - Named Entity Linking (NEL) on ink content
        - Handwriting recognition (HWR)
        - Math recognition
        - Ink-to-X pipeline processing
        - Format conversion (PNG, JPG, SVG, PDF)

    Parameters
    ----------
    service_url: str
        URL of the service
    application_name: str
        Name of the application using the service
    service_endpoint: str
        Base endpoint (default: "v1/exports")
    verify_calls: bool
        Flag if API calls should be verified (default: True)
    timeout: int
        Default timeout for requests in seconds

    Examples
    --------
    >>> import asyncio
    >>> from knowledge.services.asyncio.ink import AsyncInkServices
    >>> from knowledge.base.ink import ExportFormat
    >>>
    >>> async def main():
    ...     client = AsyncInkServices(
    ...         service_url="https://private-knowledge.wacom.com",
    ...         application_name="My App"
    ...     )
    ...     await client.login(tenant_api_key="<key>", external_user_id="<user_id>")
    ...
    ...     with open("input.uim", "rb") as f:
    ...         uim_content = f.read()
    ...     png_bytes = await client.convert_to(uim_content, ExportFormat.PNG)
    >>>
    >>> asyncio.run(main())
    """

    INK_TO_X_ENDPOINT: str = "ink-to-x/enrich-uim/"
    NER_ENDPOINT: str = "ner/enrich-uim/"
    HWR_MODEL_ENDPOINT: str = "ink-to-text/enrich-uim/"
    HWR_MODEL_TEXT_ENDPOINT: str = "ink-to-text/uim-to-text/"
    MATH_MODEL_ENDPOINT: str = "ink-to-math/enrich-uim/"
    EXPORT_ENDPOINT: str = "conversion/export-uim/"
    PDF_ENDPOINT: str = "conversion/uim-to-pdf/"
    WDF_ENDPOINT: str = "conversion/uim-to-wdf/"

    def __init__(
        self,
        application_name: str,
        service_url: str,
        service_endpoint: str = "v1/exports",
        verify_calls: bool = True,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        super().__init__(
            service_url=service_url,
            application_name=application_name,
            service_endpoint=service_endpoint,
            verify_calls=verify_calls,
            timeout=timeout,
        )

    async def perform_named_entity_linking(
        self,
        content: bytes,
        locale: LocaleCode = EN_US,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bytes:
        """NEL service for Universal Ink Model.

        Parameter
        ---------
        content: bytes
            UIM bytes.
        locale: str
            Locale for language and country.

        auth_key: Optional[str] [default:=None]
            Use a different auth key than the one from the client.

        Returns
        -------
        enriched_model: InkModel
            Enriched Universal Ink Model.
        """
        url: str = f"{self.service_base_url}{AsyncInkServices.NER_ENDPOINT}"
        session: AsyncSession = await self.asyncio_session()

        response: ResponseData = await session.post(
            url,
            data=content,
            params={LOCALE_TAG: locale},
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.status == HTTPStatus.OK:
            return response.content
        raise await handle_error("Service returns failure.", response, parameters={LOCALE_TAG: locale})

    async def perform_ink_to_math(
        self,
        content: bytes,
        schema: Schema,
        provider: Provider = Provider.MYSCRIPT,
        priority: Priority = Priority.LOWEST,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bytes:
        """
        Run a math recognition process.

        Parameters
        ----------
        content: bytes
            UIM content
        schema: Schema
            The schema for representing the results
        provider: Provider
            Technology provider
        priority: Priority (default:= LOWEST)
            Priority of request
        timeout: int
            Timeout for the request
        auth_key: Optional[str]
            Authorization key for the request, if not set the token will be requested from the service.
        Returns
        -------
        content: bytes
            Content of an enriched model.
        """

        url: str = f"{self.service_base_url}{AsyncInkServices.MATH_MODEL_ENDPOINT}"
        parameters: Dict[str, str] = {
            "provider": provider.value,
            "schema": schema.value,
            "priority": priority.value,
        }
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.post(
            url,
            data=content,
            params=parameters,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return response.content
        raise await handle_error("Ink to Math service failed", response, parameters=parameters)

    async def perform_ink_to_text(
        self,
        content: bytes,
        locale: LocaleCode = EN_US,
        hwr_mode: HWRMode = HWRMode.TEXT_MODE,
        priority: Priority = Priority.LOWEST,
        provider: Provider = Provider.MYSCRIPT,
        schema: Schema = Schema.SEGMENTATION_V03,
        text_direction: Optional[WritingOrientation] = None,
        filter_brushes: Optional[List[str]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bytes:
        """
        Run a handwriting recognition process.

        Parameters
        ----------
        content: bytes
            UIM content
        locale: str
            Locale for language and country
        hwr_mode: HWRMode (default:= TEXT_MODE)
            Handwriting recognition mode.
        priority: Priority (default:= LOWEST)
            Priority of request
        provider: str
            Provider of handwriting recognition.
        schema: Schema
            The UIM schema for representing the results
        text_direction: WritingOrientation
            Text direction. Only applicable to Japanese (ja_JP)! Possible values: auto, horizontal, vertical.
        filter_brushes: List[str]
            Filter brushes
        timeout: int
            Timeout for the request
        auth_key: Optional[str]
            Authorization key for the request, if not set, the token will be requested from the service.

        Returns
        -------
        content: bytes
            Content of an enriched model.
        """
        url: str = f"{self.service_base_url}{AsyncInkServices.HWR_MODEL_ENDPOINT}"
        parameters: Dict[str, str] = {
            "textProvider": provider.value,
            LOCALE_TAG: locale,
            "mode": hwr_mode.value,
            "priority": priority.value,
            "schema": schema.value,
            "filterBrushes": [] if filter_brushes is None else filter_brushes,
        }
        if text_direction:
            if locale != "ja_JP":
                parameters["textDirection"] = text_direction.value
            raise ValueError(f"Text direction is not supported for locale: {locale}. Only for ja_JP.")
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {auth_key}",
            "Content-Type": "application/octet-stream",
        }
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.post(
            url,
            headers=headers,
            data=content,
            params=parameters,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return await response.content
        raise await handle_error(
            f"Ink to text fails with status code:= {response.status}.",
            response,
            headers=headers,
            parameters=parameters,
        )

    async def perform_ink_to_text_plain(
        self,
        content: bytes,
        locale: LocaleCode = EN_US,
        hwr_mode: HWRMode = HWRMode.TEXT_MODE,
        priority: Priority = Priority.LOWEST,
        provider: Provider = Provider.MYSCRIPT,
        schema: Schema = Schema.SEGMENTATION_V03,
        text_direction: Optional[WritingOrientation] = None,
        filter_brushes: Optional[List[str]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> str:
        """
        Run a handwriting recognition process.

        Parameters
        ----------
        content: bytes
            UIM content
        locale: str
            Locale for language and country
        hwr_mode: HWRMode (default:= TEXT_MODE)
            Handwriting recognition mode.
        priority: Priority (default:= LOWEST)
            Priority of request
        provider: str
            Provider of handwriting recognition.
        schema: Schema
            The UIM schema for representing the results
        text_direction: WritingOrientation
            Text direction. Only applicable to Japanese (ja_JP)! Possible values: auto, horizontal, vertical.
        filter_brushes: List[str]
            Filter brushes
        timeout: int
            Timeout for the request
        auth_key: Optional[str]
            Authorization key for the request, if not set the token will be requested from the service.
        Returns
        -------
        content: str
            Recognized text.
        """
        url: str = f"{self.service_base_url}{AsyncInkServices.HWR_MODEL_TEXT_ENDPOINT}"
        parameters: Dict[str, str] = {
            "textProvider": provider.value,
            LOCALE_TAG: locale,
            "mode": hwr_mode.value,
            "priority": priority.value,
            "schema": schema.value,
            "filterBrushes": [] if filter_brushes is None else filter_brushes,
        }
        if text_direction and locale == JA_JP:
            parameters["textDirection"] = text_direction.value

        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.post(
            url,
            data=content,
            params=parameters,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.status == HTTPStatus.OK:
            return response.content
        raise await handle_error(
            f"Ink to Text (plain) returns failure [status:={response.status}]",
            response,
            parameters=parameters,
        )

    async def ink_to_x(
        self,
        content: bytes,
        settings: InkToXSettings = DEFAULT_INK_TO_X,
        priority: Priority = Priority.LOWEST,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bytes:
        """
        Running the ink to X service, which analyzes the UIM content for the different content modes and then
        uses the different recognition services to enrich the UIM content.

        Parameters
        ----------
        content: bytes
            UIM content
        settings: InkToXSettings
            Settings for the ink to X service
        priority: Priority
            The priority of the request
        timeout: int
            Timeout for the request
        auth_key: Optional[str]
            Authorization key for the request, if not set the token will be requested from the service.

        Returns
        -------
        content: bytes
            Content of an enriched model.
        """
        url: str = f"{self.service_base_url}{AsyncInkServices.INK_TO_X_ENDPOINT}"
        parameters: Dict[str, str] = {}
        for provider_idx, provider in enumerate(settings.provider_settings):
            parameters[f"providers[{provider_idx}].locale"] = provider.locale
            parameters[f"providers[{provider_idx}].mode"] = provider.mode.value
            parameters[f"providers[{provider_idx}].provider"] = provider.provider.value
            parameters[f"providers[{provider_idx}].schema"] = provider.schema.value
            parameters[f"providers[{provider_idx}].textDirection"] = provider.text_direction.value
            if len(provider.filter_brushes) > 0:
                parameters[f"providers[{provider_idx}].filterBrushes"] = ",".join(provider.filter_brushes)
        if settings.segmentation_locale:
            parameters["segmentationLocale"] = settings.segmentation_locale
        if priority:
            parameters["priority"] = priority.value
        if settings.view_name:
            parameters["viewName"] = settings.view_name
        if settings.grouping_strategy:
            parameters["groupingStrategy"] = str(settings.grouping_strategy)
        if settings.optimized:
            parameters["optimized"] = str(settings.optimized)
        if settings.destination_segmentation_schema:
            parameters["destinationSegmentationSchema"] = str(settings.destination_segmentation_schema)
        if settings.reorder_strategy:
            parameters["reorderStrategy"] = str(settings.reorder_strategy)
        if settings.merge_rows_vertically:
            parameters["mergeRowsVertically"] = str(settings.merge_rows_vertically)
        if settings.other_separation_coef:
            parameters["otherSeparationCoef"] = str(settings.other_separation_coef)
        if settings.text_separation_coef:
            parameters["textSeparationCoef"] = str(settings.text_separation_coef)
        if settings.math_separation_coef:
            parameters["mathSeparationCoef"] = str(settings.math_separation_coef)
        if settings.batch_size:
            parameters["batchSize"] = str(settings.batch_size)
        session: AsyncSession = await self.asyncio_session()

        response: ResponseData = await session.post(
            url,
            params=parameters,
            data=content,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return response.content
        content: str = response.content
        raise await handle_error(
            f"Ink to X request fails with " f"status code:={response.status}, message: {content}",
            response,
            parameters=parameters,
        )

    async def convert_to(
        self,
        content: bytes,
        export: ExportFormat,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bytes:
        """
        Convert content to the specified export format.
        The available formats depend on the export service.

        Parameters
        ----------
        content : bytes
            Binary content to be converted.
        export : ExportFormat
            Desired output format.
        auth_key : Optional[str], optional
            Bearer token for authentication. If not provided, a new token is fetched.
        timeout : int, optional
            Request timeout in seconds. Defaults to DEFAULT_TIMEOUT.

        Returns
        -------
        bytes
            Converted binary data.

        Raises
        ------
        RuntimeError
            If the export service returns a non-successful status code.
        """
        url: str = f"{self.service_base_url}{AsyncInkServices.EXPORT_ENDPOINT}"
        parameters: Dict[str, str] = {"format": export.value}
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.post(
            url,
            data=content,
            params=parameters,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return response.content
        raise await handle_error(
            f"Export service fails with " f"status code:={response.status}, message: {str(response.content)}",
            response,
            parameters=parameters,
        )

    async def convert_to_pdf(
        self,
        content: bytes,
        pdf_type: PDFType,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bytes:
        """Export service.

        Parameters
        ----------
        content: bytes
            Universal Ink Model
        pdf_type: PDFType
            Raster or Vector mode
        timeout: int
            Timeout for the request
        auth_key: Optional[str]
            Authorization key for the request, if not set the token will be requested from the service.

        Returns
        -------
        pdf_content: bytes
            File content of the result PDF
        """
        url: str = f"{self.service_base_url}{AsyncInkServices.PDF_ENDPOINT}"
        parameters: Dict[str, str] = {"type": pdf_type.value}
        session: AsyncSession = await self.asyncio_session()

        response: ResponseData = await session.post(
            url,
            data=content,
            params=parameters,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return response.content
        raise await handle_error(
            f"PDF export service fails with " f"status code:={response.status}, message: {str(response.content)}",
            response,
            parameters=parameters,
        )
