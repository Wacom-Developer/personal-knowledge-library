# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom. All rights reserved.
"""
Ink Services Client
-------------------
Synchronous client for Wacom Ink Services including:
- Named Entity Linking (NEL)
- Handwriting Recognition (HWR)
- Math Recognition
- Format Conversion (PNG, JPG, SVG, PDF)
"""

from http import HTTPStatus
from typing import Dict, Optional, List

from requests import Response

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
from knowledge.base.language import LocaleCode, EN_US
from knowledge.services import (
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_BACKOFF_FACTOR,
)
from knowledge.services.base import WacomServiceAPIClient, handle_error

__all__ = ["InkServices"]


class InkServices(WacomServiceAPIClient):
    """
    InkServices
    -----------
    Synchronous client for Wacom Ink Services.

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
    max_retries: int
        Maximum number of retries for failed requests
    backoff_factor: float
        Backoff factor for retries

    Examples
    --------
    >>> from knowledge.services.ink import InkServices
    >>> from knowledge.base.ink import ExportFormat
    >>>
    >>> client = InkServices(service_url="https://private-knowledge.wacom.com")
    >>> client.login(tenant_api_key="<key>", external_user_id="<user_id>")
    >>>
    >>> with open("input.uim", "rb") as f:
    ...     uim_content = f.read()
    >>> png_bytes = client.convert_to(uim_content, ExportFormat.PNG)
    """

    # Endpoint constants
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
        service_url: str,
        application_name: str = "Ink Services Client",
        service_endpoint: str = "v1/exports",
        verify_calls: bool = True,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        super().__init__(
            service_url=service_url,
            application_name=application_name,
            service_endpoint=service_endpoint,
            verify_calls=verify_calls,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )

    # ------------------------------------------ NEL Service -----------------------------------------------------------

    def perform_named_entity_linking(
        self,
        content: bytes,
        locale: LocaleCode = EN_US,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bytes:
        """
        Perform Named Entity Linking (NEL) on Universal Ink Model content.

        Links recognized text in ink content to entities in the knowledge graph.

        Parameters
        ----------
        content: bytes
            Universal Ink Model (UIM) binary content
        locale: LocaleCode
            Locale for language and country (default: en_US)
        auth_key: Optional[str]
            If set, uses this auth key instead of the logged-in user's token
        timeout: int
            Request timeout in seconds (default: 60)

        Returns
        -------
        bytes
            Enriched Universal Ink Model with entity links

        Raises
        ------
        WacomServiceException
            If the service returns an error
        """
        url: str = f"{self.service_base_url}{InkServices.NER_ENDPOINT}"
        params: Dict[str, str] = {LOCALE_TAG: str(locale)}
        response: Response = self.request_session.post(
            url,
            data=content,
            params=params,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.status_code == HTTPStatus.OK:
            return response.content
        raise handle_error(
            f"NEL service failed. Locale: {locale}",
            response,
            parameters=params,
        )

    # ------------------------------------------ Math Recognition ------------------------------------------------------

    def perform_ink_to_math(
        self,
        content: bytes,
        schema: Schema,
        provider: Provider = Provider.MYSCRIPT,
        priority: Priority = Priority.LOWEST,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bytes:
        """
        Perform math recognition on ink content.

        Parameters
        ----------
        content: bytes
            Universal Ink Model (UIM) binary content
        schema: Schema
            The schema for representing the recognition results
        provider: Provider
            Technology provider for recognition (default: MYSCRIPT)
        priority: Priority
            Request priority (default: LOWEST)
        auth_key: Optional[str]
            If set, uses this auth key instead of the logged-in user's token
        timeout: int
            Request timeout in seconds (default: 60)

        Returns
        -------
        bytes
            Enriched Universal Ink Model with math recognition results

        Raises
        ------
        WacomServiceException
            If the service returns an error
        """
        url: str = f"{self.service_base_url}{InkServices.MATH_MODEL_ENDPOINT}"
        params: Dict[str, str] = {
            "provider": provider.value,
            "schema": schema.value,
            "priority": priority.value,
        }

        response: Response = self.request_session.post(
            url,
            data=content,
            params=params,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return response.content
        raise handle_error(
            "Math recognition service failed",
            response,
            parameters=params,
        )

    # ------------------------------------------ Handwriting Recognition -----------------------------------------------

    def perform_ink_to_text(
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
        Perform handwriting recognition on ink content.

        Returns the enriched UIM with recognition results embedded.

        Parameters
        ----------
        content: bytes
            Universal Ink Model (UIM) binary content
        locale: LocaleCode
            Locale for language and country (default: en_US)
        hwr_mode: HWRMode
            Handwriting recognition mode (default: TEXT_MODE)
        priority: Priority
            Request priority (default: LOWEST)
        provider: Provider
            Recognition technology provider (default: MYSCRIPT)
        schema: Schema
            UIM schema for results (default: SEGMENTATION_V03)
        text_direction: Optional[WritingOrientation]
            Text direction. Only applicable to Japanese (ja_JP).
            Possible values: auto, horizontal, vertical.
        filter_brushes: Optional[List[str]]
            List of brush IDs to filter
        auth_key: Optional[str]
            If set, uses this auth key instead of the logged-in user's token
        timeout: int
            Request timeout in seconds (default: 60)

        Returns
        -------
        bytes
            Enriched Universal Ink Model with handwriting recognition results

        Raises
        ------
        WacomServiceException
            If the service returns an error
        ValueError
            If text_direction is set for a non-Japanese locale
        """
        url: str = f"{self.service_base_url}{InkServices.HWR_MODEL_ENDPOINT}"
        params: Dict[str, str] = {
            "textProvider": provider.value,
            LOCALE_TAG: str(locale),
            "mode": hwr_mode.value,
            "priority": priority.value,
            "schema": schema.value,
        }
        if filter_brushes:
            params["filterBrushes"] = ",".join(filter_brushes)

        if text_direction:
            if str(locale) != "ja_JP":
                raise ValueError(f"Text direction is only supported for ja_JP locale, not {locale}")
            params["textDirection"] = text_direction.value

        response: Response = self.request_session.post(
            url,
            data=content,
            params=params,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return response.content
        raise handle_error(
            f"Handwriting recognition failed. Status: {response.status_code}",
            response,
            parameters=params,
        )

    def perform_ink_to_text_plain(
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
        Perform handwriting recognition and return plain text.

        Unlike `perform_ink_to_text`, this returns only the recognized text string,
        not the enriched UIM.

        Parameters
        ----------
        content: bytes
            Universal Ink Model (UIM) binary content
        locale: LocaleCode
            Locale for language and country (default: en_US)
        hwr_mode: HWRMode
            Handwriting recognition mode (default: TEXT_MODE)
        priority: Priority
            Request priority (default: LOWEST)
        provider: Provider
            Recognition technology provider (default: MYSCRIPT)
        schema: Schema
            UIM schema for results (default: SEGMENTATION_V03)
        text_direction: Optional[WritingOrientation]
            Text direction. Only applicable to Japanese (ja_JP).
        filter_brushes: Optional[List[str]]
            List of brush IDs to filter
        auth_key: Optional[str]
            If set, uses this auth key instead of the logged-in user's token
        timeout: int
            Request timeout in seconds (default: 60)

        Returns
        -------
        str
            Recognized text as a string

        Raises
        ------
        WacomServiceException
            If the service returns an error
        """
        url: str = f"{self.service_base_url}{InkServices.HWR_MODEL_TEXT_ENDPOINT}"
        params: Dict[str, str] = {
            "textProvider": provider.value,
            LOCALE_TAG: str(locale),
            "mode": hwr_mode.value,
            "priority": priority.value,
            "schema": schema.value,
        }
        if filter_brushes:
            params["filterBrushes"] = ",".join(filter_brushes)

        if text_direction:
            if str(locale) == "ja_JP":
                params["textDirection"] = text_direction.value

        response: Response = self.request_session.post(
            url,
            data=content,
            params=params,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.status_code == HTTPStatus.OK:
            return response.text
        raise handle_error(
            f"Handwriting recognition (plain text) failed. Status: {response.status_code}",
            response,
            parameters=params,
        )

    # ------------------------------------------ Ink-to-X Pipeline -----------------------------------------------------

    def ink_to_x(
        self,
        content: bytes,
        settings: InkToXSettings = DEFAULT_INK_TO_X,
        priority: Priority = Priority.LOWEST,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bytes:
        """
        Run the Ink-to-X pipeline on UIM content.

        The Ink-to-X service analyzes UIM content for different content modes
        (text, math, diagrams, etc.) and uses the appropriate recognition services
        to enrich the content.

        Parameters
        ----------
        content: bytes
            Universal Ink Model (UIM) binary content
        settings: InkToXSettings
            Configuration settings for the Ink-to-X pipeline
        priority: Priority
            Request priority (default: LOWEST)
        auth_key: Optional[str]
            If set, uses this auth key instead of the logged-in user's token
        timeout: int
            Request timeout in seconds (default: 60)

        Returns
        -------
        bytes
            Enriched Universal Ink Model with recognition results

        Raises
        ------
        WacomServiceException
            If the service returns an error
        """
        url: str = f"{self.service_base_url}{InkServices.INK_TO_X_ENDPOINT}"
        params: Dict[str, str] = {}

        # Build provider parameters
        for idx, provider in enumerate(settings.provider_settings):
            params[f"providers[{idx}].locale"] = provider.locale
            params[f"providers[{idx}].mode"] = provider.mode.value
            params[f"providers[{idx}].provider"] = provider.provider.value
            params[f"providers[{idx}].schema"] = provider.schema.value
            params[f"providers[{idx}].textDirection"] = provider.text_direction.value
            if provider.filter_brushes:
                params[f"providers[{idx}].filterBrushes"] = ",".join(provider.filter_brushes)

        # Add optional settings
        if settings.segmentation_locale:
            params["segmentationLocale"] = settings.segmentation_locale
        if priority:
            params["priority"] = priority.value
        if settings.view_name:
            params["viewName"] = settings.view_name
        if settings.grouping_strategy:
            params["groupingStrategy"] = str(settings.grouping_strategy)
        if settings.optimized:
            params["optimized"] = str(settings.optimized)
        if settings.destination_segmentation_schema:
            params["destinationSegmentationSchema"] = str(settings.destination_segmentation_schema)
        if settings.reorder_strategy:
            params["reorderStrategy"] = str(settings.reorder_strategy)
        if settings.merge_rows_vertically:
            params["mergeRowsVertically"] = str(settings.merge_rows_vertically)
        if settings.other_separation_coef:
            params["otherSeparationCoef"] = str(settings.other_separation_coef)
        if settings.text_separation_coef:
            params["textSeparationCoef"] = str(settings.text_separation_coef)
        if settings.math_separation_coef:
            params["mathSeparationCoef"] = str(settings.math_separation_coef)
        if settings.batch_size:
            params["batchSize"] = str(settings.batch_size)

        response: Response = self.request_session.post(
            url,
            data=content,
            params=params,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return response.content
        raise handle_error(
            f"Ink-to-X pipeline failed. Status: {response.status_code}",
            response,
            parameters=params,
        )

    # ------------------------------------------ Format Conversion -----------------------------------------------------

    def convert_to(
        self,
        content: bytes,
        export_format: ExportFormat,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bytes:
        """
        Convert UIM content to the specified image format.

        Parameters
        ----------
        content: bytes
            Universal Ink Model (UIM) binary content
        export_format: ExportFormat
            Target format (PNG, JPG, SVG)
        auth_key: Optional[str]
            If set, uses this auth key instead of the logged-in user's token
        timeout: int
            Request timeout in seconds (default: 60)

        Returns
        -------
        bytes
            Converted image data in the requested format

        Raises
        ------
        WacomServiceException
            If the conversion service returns an error

        Examples
        --------
        >>> png_data = client.convert_to(uim_content, ExportFormat.PNG)
        >>> with open("output.png", "wb") as f:
        ...     f.write(png_data)
        """
        url: str = f"{self.service_base_url}{InkServices.EXPORT_ENDPOINT}"
        params: Dict[str, str] = {"format": export_format.value}

        response: Response = self.request_session.post(
            url,
            data=content,
            params=params,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return response.content
        raise handle_error(
            f"Export to {export_format.value} failed. Status: {response.status_code}",
            response,
            parameters=params,
        )

    def convert_to_pdf(
        self,
        content: bytes,
        pdf_type: PDFType,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bytes:
        """
        Convert UIM content to PDF format.

        Parameters
        ----------
        content: bytes
            Universal Ink Model (UIM) binary content
        pdf_type: PDFType
            PDF rendering type (VECTOR or RASTER)
        auth_key: Optional[str]
            If set, uses this auth key instead of the logged-in user's token
        timeout: int
            Request timeout in seconds (default: 60)

        Returns
        -------
        bytes
            PDF file content

        Raises
        ------
        WacomServiceException
            If the PDF conversion service returns an error

        Examples
        --------
        >>> pdf_data = client.convert_to_pdf(uim_content, PDFType.VECTOR)
        >>> with open("output.pdf", "wb") as f:
        ...     f.write(pdf_data)
        """
        url: str = f"{self.service_base_url}{InkServices.PDF_ENDPOINT}"
        params: Dict[str, str] = {"type": pdf_type.value}

        response: Response = self.request_session.post(
            url,
            data=content,
            params=params,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return response.content
        raise handle_error(
            f"PDF export ({pdf_type.value}) failed. Status: {response.status_code}",
            response,
            parameters=params,
        )
