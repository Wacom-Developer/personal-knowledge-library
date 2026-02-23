Module knowledge.services.asyncio.ink
=====================================

Classes
-------

`AsyncInkServices(application_name: str, service_url: str, service_endpoint: str = 'v1/exports', verify_calls: bool = True, timeout: int = 60)`
:   AsyncInkServices
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

    ### Ancestors (in MRO)

    * knowledge.services.asyncio.base.AsyncServiceAPIClient
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

    `convert_to(self, content: bytes, export: knowledge.base.ink.ExportFormat, auth_key: str | None = None, timeout: int = 60) ‑> bytes`
    :   Convert content to the specified export format.
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

    `convert_to_pdf(self, content: bytes, pdf_type: knowledge.base.ink.PDFType, auth_key: str | None = None, timeout: int = 60) ‑> bytes`
    :   Export service.
        
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

    `ink_to_x(self, content: bytes, settings: knowledge.base.ink.InkToXSettings = <knowledge.base.ink.InkToXSettings object>, priority: knowledge.base.ink.Priority = Priority.LOWEST, auth_key: str | None = None, timeout: int = 60) ‑> bytes`
    :   Running the ink to X service, which analyzes the UIM content for the different content modes and then
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

    `perform_ink_to_math(self, content: bytes, schema: knowledge.base.ink.Schema, provider: knowledge.base.ink.Provider = Provider.MYSCRIPT, priority: knowledge.base.ink.Priority = Priority.LOWEST, auth_key: str | None = None, timeout: int = 60) ‑> bytes`
    :   Run a math recognition process.
        
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

    `perform_ink_to_text(self, content: bytes, locale: knowledge.base.language.LocaleCode = 'en_US', hwr_mode: knowledge.base.ink.HWRMode = HWRMode.TEXT_MODE, priority: knowledge.base.ink.Priority = Priority.LOWEST, provider: knowledge.base.ink.Provider = Provider.MYSCRIPT, schema: knowledge.base.ink.Schema = Schema.SEGMENTATION_V03, text_direction: knowledge.base.ink.WritingOrientation | None = None, filter_brushes: List[str] | None = None, auth_key: str | None = None, timeout: int = 60) ‑> bytes`
    :   Run a handwriting recognition process.
        
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

    `perform_ink_to_text_plain(self, content: bytes, locale: knowledge.base.language.LocaleCode = 'en_US', hwr_mode: knowledge.base.ink.HWRMode = HWRMode.TEXT_MODE, priority: knowledge.base.ink.Priority = Priority.LOWEST, provider: knowledge.base.ink.Provider = Provider.MYSCRIPT, schema: knowledge.base.ink.Schema = Schema.SEGMENTATION_V03, text_direction: knowledge.base.ink.WritingOrientation | None = None, filter_brushes: List[str] | None = None, auth_key: str | None = None, timeout: int = 60) ‑> str`
    :   Run a handwriting recognition process.
        
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

    `perform_named_entity_linking(self, content: bytes, locale: knowledge.base.language.LocaleCode = 'en_US', auth_key: str | None = None, timeout: int = 60) ‑> bytes`
    :   NEL service for Universal Ink Model.
        
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