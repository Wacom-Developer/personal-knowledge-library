Module knowledge.services.ink
=============================
Ink Services Client
-------------------
Synchronous client for Wacom Ink Services including
- Named Entity Linking (NEL)
- Handwriting Recognition (HWR)
- Math Recognition
- Format Conversion (PNG, JPG, SVG, PDF)

Classes
-------

`InkServices(service_url: str, application_name: str = 'Ink Services Client', service_endpoint: str = 'v1/exports', verify_calls: bool = True, max_retries: int = 3, backoff_factor: float = 0.1)`
:   InkServices
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

    ### Ancestors (in MRO)

    * knowledge.services.base.WacomServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Class variables

    `EXPORT_ENDPOINT: str`
    :   The type of the None singleton.

    `HWR_MODEL_ENDPOINT: str`
    :   The type of the None singleton.

    `HWR_MODEL_TEXT_ENDPOINT: str`
    :   The type of the None singleton.

    `INK_TO_X_ENDPOINT: str`
    :   The type of the None singleton.

    `MATH_MODEL_ENDPOINT: str`
    :   The type of the None singleton.

    `NER_ENDPOINT: str`
    :   The type of the None singleton.

    `PDF_ENDPOINT: str`
    :   The type of the None singleton.

    `WDF_ENDPOINT: str`
    :   The type of the None singleton.

    ### Methods

    `convert_to(self, content: bytes, export_format: knowledge.base.ink.ExportFormat, auth_key: str | None = None, timeout: int = 60) ‑> bytes`
    :   Convert UIM content to the specified image format.
        
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

    `convert_to_pdf(self, content: bytes, pdf_type: knowledge.base.ink.PDFType, auth_key: str | None = None, timeout: int = 60) ‑> bytes`
    :   Convert UIM content to PDF format.
        
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

    `ink_to_x(self, content: bytes, settings: knowledge.base.ink.InkToXSettings = <knowledge.base.ink.InkToXSettings object>, priority: knowledge.base.ink.Priority = Priority.LOWEST, auth_key: str | None = None, timeout: int = 60) ‑> bytes`
    :   Run the Ink-to-X pipeline on UIM content.
        
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

    `perform_ink_to_math(self, content: bytes, schema: knowledge.base.ink.Schema, provider: knowledge.base.ink.Provider = Provider.MYSCRIPT, priority: knowledge.base.ink.Priority = Priority.LOWEST, auth_key: str | None = None, timeout: int = 60) ‑> bytes`
    :   Perform math recognition on ink content.
        
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

    `perform_ink_to_text(self, content: bytes, locale: knowledge.base.language.LocaleCode = 'en_US', hwr_mode: knowledge.base.ink.HWRMode = HWRMode.TEXT_MODE, priority: knowledge.base.ink.Priority = Priority.LOWEST, provider: knowledge.base.ink.Provider = Provider.MYSCRIPT, schema: knowledge.base.ink.Schema = Schema.SEGMENTATION_V03, text_direction: knowledge.base.ink.WritingOrientation | None = None, filter_brushes: List[str] | None = None, auth_key: str | None = None, timeout: int = 60) ‑> bytes`
    :   Perform handwriting recognition on ink content.
        
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

    `perform_ink_to_text_plain(self, content: bytes, locale: knowledge.base.language.LocaleCode = 'en_US', hwr_mode: knowledge.base.ink.HWRMode = HWRMode.TEXT_MODE, priority: knowledge.base.ink.Priority = Priority.LOWEST, provider: knowledge.base.ink.Provider = Provider.MYSCRIPT, schema: knowledge.base.ink.Schema = Schema.SEGMENTATION_V03, text_direction: knowledge.base.ink.WritingOrientation | None = None, filter_brushes: List[str] | None = None, auth_key: str | None = None, timeout: int = 60) ‑> str`
    :   Perform handwriting recognition and return plain text.
        
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

    `perform_named_entity_linking(self, content: bytes, locale: knowledge.base.language.LocaleCode = 'en_US', auth_key: str | None = None, timeout: int = 60) ‑> bytes`
    :   Perform Named Entity Linking (NEL) on Universal Ink Model content.
        
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