Module knowledge.utils.graph
============================

Functions
---------

`async_count_things(async_client: knowledge.services.asyncio.graph.AsyncWacomKnowledgeService, user_token: str, concept_type: knowledge.base.ontology.OntologyClassReference, locale: knowledge.base.language.LocaleCode | None = None, visibility: knowledge.services.graph.Visibility | None = None, only_own: bool | None = None) ‑> int`
:   Async counting of things given a concept type.
    
    Parameters
    ----------
    async_client: AsyncWacomKnowledgeService
        The Wacom Knowledge Service
    user_token: str
        The user token
    concept_type: OntologyClassReference
        The concept type
    locale: Optional[LocaleCode] = [default:= None]
        The locale
    visibility: Optional[Visibility] = [default:= None]
        The visibility
    only_own: Optional[bool] = [default:= None]
        Only own things
    
    Returns
    -------
    int
        The number of things

`async_count_things_session(async_client: knowledge.services.asyncio.graph.AsyncWacomKnowledgeService, concept_type: knowledge.base.ontology.OntologyClassReference, locale: knowledge.base.language.LocaleCode | None = None, visibility: knowledge.services.graph.Visibility | None = None, only_own: bool | None = None) ‑> int`
:   Async counting of things given a concept type using session.
    
    Parameters
    ----------
    async_client: AsyncWacomKnowledgeService
        The Wacom Knowledge Service
    concept_type: OntologyClassReference
        The concept type
    locale: Optional[LocaleCode] = [default:= None]
        The locale
    visibility: Optional[Visibility] = [default:= None]
        The visibility
    only_own: Optional[bool] = [default:= None]
        Only own things
    
    Returns
    -------
    int
        The number of things

`async_things_iter(async_client: knowledge.services.asyncio.graph.AsyncWacomKnowledgeService, user_token: str, refresh_token: str, concept_type: knowledge.base.ontology.OntologyClassReference, visibility: knowledge.services.graph.Visibility | None = None, locale: knowledge.base.language.LocaleCode | None = None, only_own: bool | None = None, include_relations: bool | None = None, fetch_size: int = 100, force_refresh_timeout: int = 360, tenant_api_key: str | None = None, external_user_id: str | None = None) ‑> AsyncIterator[Tuple[knowledge.base.ontology.ThingObject, str, str]]`
:   Generates an asynchronous iterator that retrieves and yields objects along with user and refresh tokens.
    
    Parameters
    ----------
    async_client : AsyncWacomKnowledgeService
        The asynchronous client used to communicate with the Wacom knowledge service.
    user_token : str
        The current user's authentication token.
    refresh_token : str
        The token used to refresh the user’s session when expired.
    concept_type : OntologyClassReference
        The type of concept to filter the retrieved objects by.
    visibility : Optional[Visibility], optional
        The visibility level used to filter the retrieved objects.
    locale : Optional[LocaleCode], optional
        The locale used to localize object retrieval.
    only_own : Optional[bool], optional
        If True, restricts retrieval to objects owned by the current user.
    include_relations : Optional[bool], optional
        If True, includes relations in the retrieved objects.
    fetch_size : int, optional
        The number of objects to fetch per page. Default is 100.
    force_refresh_timeout : int, optional
        Forces a timeout duration for token refresh handling. Default is 360 seconds.
    tenant_api_key : Optional[str], optional
        The tenant-specific API key for the user’s organization.
    external_user_id : Optional[str], optional
        The external identifier for the user in the tenant's system.
    
    Returns
    -------
    AsyncIterator[Tuple[ThingObject, str, str]]
        An asynchronous iterator yielding retrieved objects, the updated user token, and the refresh token.

`async_things_session_iter(async_client: knowledge.services.asyncio.graph.AsyncWacomKnowledgeService, concept_type: knowledge.base.ontology.OntologyClassReference, visibility: knowledge.services.graph.Visibility | None = None, locale: knowledge.base.language.LocaleCode | None = None, only_own: bool | None = None, include_relations: bool | None = None, fetch_size: int = 100, force_refresh_timeout: int = 360) ‑> AsyncIterator[knowledge.base.ontology.ThingObject]`
:   Asynchronous iterator over all things of a given type using session.
    
    Parameters
    ----------
    async_client: AsyncWacomKnowledgeService
        The Wacom Knowledge Service
    concept_type: OntologyClassReference
        The class type
    visibility: Optional[Visibility] [default:= None]
        The visibility
    locale: Optional[LocaleCode] [default:= None]
        Only entities with this label having a given locale
    only_own: Optional[bool] = [default:= None]
        Only own things
    include_relations: Optional[bool] = [default:= None]
        Include relations
    fetch_size: int [default:= 100]
        Fetch size.
    force_refresh_timeout: int [default:= 360]
        Force refresh timeout
    
    Yields
    -------
    ThingObject
        Next thing object

`count_things(wacom_client: knowledge.services.graph.WacomKnowledgeService, user_token: str, concept_type: knowledge.base.ontology.OntologyClassReference, locale: knowledge.base.language.LocaleCode | None = None, visibility: knowledge.services.graph.Visibility | None = None, only_own: bool | None = None) ‑> int`
:   Counts the number of things.
    
    Parameters
    ----------
    wacom_client: WacomKnowledgeService
        The Wacom Knowledge Service
    user_token: str
        The user token
    concept_type: OntologyClassReference
        The concept type
    locale: Optional[LocaleCode]
        The locale
    visibility: Optional[Visibility]
        The visibility
    only_own: Optional[bool]
        Only own things
    Returns
    -------
    int
        The number of things

`count_things_session(wacom_client: knowledge.services.graph.WacomKnowledgeService, concept_type: knowledge.base.ontology.OntologyClassReference, locale: knowledge.base.language.LocaleCode | None = None, visibility: knowledge.services.graph.Visibility | None = None, only_own: bool | None = None) ‑> int`
:   Counts the number of things.
    
    Parameters
    ----------
    wacom_client: WacomKnowledgeService
        The Wacom Knowledge Service
    concept_type: OntologyClassReference
        The concept type
    locale: Optional[LocaleCode] = [default:= None]
        The locale
    visibility: Optional[Visibility] = [default:= None]
        The visibility
    only_own: Optional[bool] = [default:= None]
        Only own things
    Returns
    -------
    int
        The number of things

`things_iter(wacom_client: knowledge.services.graph.WacomKnowledgeService, user_token: str, refresh_token: str, concept_type: knowledge.base.ontology.OntologyClassReference, visibility: knowledge.services.graph.Visibility | None = None, locale: knowledge.base.language.LocaleCode | None = None, only_own: bool = False, include_relations: bool | None = None, fetch_size: int = 100, force_refresh_timeout: int = 360, tenant_api_key: str | None = None, external_user_id: str | None = None) ‑> Iterator[Tuple[knowledge.base.ontology.ThingObject, str, str]]`
:   Iterates over all things.
    
    Parameters
    ----------
    wacom_client: WacomKnowledgeService
        The Wacom Knowledge Service
    user_token: str
        The user token
    refresh_token: str
        The refresh token
    concept_type: OntologyClassReference
        The class type
    visibility: Optional[Visibility] [default:= None]
        The visibility
    locale: Optional[LocaleCode] [default:= None]
        Only entities with this labels having a given locale
    only_own: bool [default:= False]
        Only own things
    include_relations: Optional[bool] = [default:= None]
        Include relations in the response.
    fetch_size: int [default:= 100]
        Fetch size.
    force_refresh_timeout: int [default:= 360]
        Force refresh timeout
    tenant_api_key: Optional[str] [default:= None]
        The tenant API key
    external_user_id: Optional[str] [default:= None]
        The external user ID
    
    Yields
    -------
    obj: ThingObject
        Current thing
    user_token: str
        The user token
    refresh_token: str
        The refresh token

`things_session_iter(wacom_client: knowledge.services.graph.WacomKnowledgeService, concept_type: knowledge.base.ontology.OntologyClassReference, visibility: knowledge.services.graph.Visibility | None = None, locale: knowledge.base.language.LocaleCode | None = None, only_own: bool = False, include_relations: bool | None = None, fetch_size: int = 100, force_refresh_timeout: int = 360) ‑> Iterator[knowledge.base.ontology.ThingObject]`
:   Iterates over all things using the current session configured for a client.
    
    Parameters
    ----------
    wacom_client: WacomKnowledgeService
        The Wacom Knowledge Service
    concept_type: OntologyClassReference
        The class type
    visibility: Optional[Visibility] [default:= None]
        The visibility
    locale: Optional[LocaleCode] [default:= None]
        Only entities with this labels having a given locale
    only_own: bool [default:= False]
        Only own things
    include_relations: Optional[bool] = [default:= None]
        Include relations in the response.
    fetch_size: int [default:= 100]
        Fetch size.
    force_refresh_timeout: int [default:= 360]
        Force refresh timeout
    
    Yields
    -------
    ThingObject
        Next thing object
    
    Raises
    ------
    ValueError
        If no session is configured for a client