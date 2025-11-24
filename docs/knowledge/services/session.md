Module knowledge.services.session
=================================
This module contains the session management.
There are three types of sessions:
    - **TimedSession**: The session is only valid until the token expires.
        There is no refresh token, thus the session cannot be refreshed.
    - **RefreshableSession**: The session is valid until the token expires.
        There is a refresh token, thus the session can be refreshed.
    - **PermanentSession**: The session is valid until the token expires.
        There is a refresh token, thus the session can be refreshed.
        Moreover, the session is bound to then _tenant api key_ and the _external user id_, which can be used to
        re-login when the refresh token expires.

Classes
-------

`PermanentSession(tenant_api_key: str, external_user_id: str, auth_token: str, refresh_token: str)`
:   PermanentSession
    ----------------
    
    A session that retains a tenant API key and an external user ID for
    permanent identification and authorization.
    
    This class extends the RefreshableSession by encapsulating additional
    information such as a unique tenant API key and an external user ID, which
    are immutable properties. It is used to establish and maintain a session
    that requires these parameters alongside authentication and refresh tokens.
    
    Attributes
    ----------
    tenant_api_key : str
        The API key associated with the tenant for this session.
    external_user_id : str
        The external user identifier for the session.

    ### Ancestors (in MRO)

    * knowledge.services.session.RefreshableSession
    * knowledge.services.session.TimedSession
    * knowledge.services.session.Session
    * abc.ABC

    ### Instance variables

    `tenant_api_key: str`
    :   Tenant api key.

`RefreshableSession(auth_token: str, refresh_token: str)`
:   RefreshableSession
    ------------------
    
    Class that extends TimedSession to provide functionality for refreshable session management.
    
    Detailed description of the class, its purpose, and usage. Allows handling of authentication
    and refresh tokens while ensuring thread-safe updates to the session. This class provides
    property-based access and management for the refresh token state and validation of session
    tokens, ensuring compatibility with user, tenant, and instance details.
    
    Attributes
    ----------
    auth_token : str
        The authentication token required for session authentication.
    refresh_token : str
        The refresh token used to renew the session.

    ### Ancestors (in MRO)

    * knowledge.services.session.TimedSession
    * knowledge.services.session.Session
    * abc.ABC

    ### Descendants

    * knowledge.services.session.PermanentSession

    ### Instance variables

    `refresh_token: str`
    :   Refresh token for the session.

    `refreshable: bool`
    :   Is the session refreshable?

    ### Methods

    `update_session(self, auth_token: str, refresh_token: str)`
    :   Refresh the session.
        Parameters
        ----------
        auth_token: str
            The refreshed authentication token.
        refresh_token: str
            The refreshed refresh token.

`Session()`
:   Session
    -------
    
    Represents an abstract session for managing authentication tokens and tracking session state.
    
    This class provides an interface for managing sessions, including properties for authentication and
    refresh tokens, session expiration status, and time until expiration. It enforces implementation of
    essential methods for handling sessions in derived classes.
    
    Attributes
    ----------
    id : str
        Unique session id, which will be the same for the same external user id, tenant, and instance of the service.
    auth_token : str
        Authentication key used to identify an external user within private knowledge.
    tenant_id : str
        Tenant id.
    refresh_token : Optional[str]
        Refresh token used to refresh the session.
    refreshable : bool
        Indicator of whether the session is refreshable.
    expired : bool
        Indicator of whether the session is expired.
    expires_in : float
        Seconds remaining until the token expires.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * knowledge.services.session.TimedSession

    ### Instance variables

    `auth_token: str`
    :   Authentication key. The authentication key is used to identify an external user within private knowledge.

    `expired: bool`
    :   Is the session expired.

    `expires_in: float`
    :   Seconds until token is expired in seconds.

    `id: str`
    :   Unique session id, which will be the same for the same external user id, tenant,
        and instance of the service.

    `refresh_token: str | None`
    :   Refresh token. The refresh token is used to refresh the session.

    `refreshable: bool`
    :   Is the session refreshable.

    `tenant_id: str`
    :   Tenant id.

    ### Methods

    `update_session(self, auth_token: str, refresh_token: str)`
    :   Update the session.
        
        Parameters
        ----------
        auth_token: str
            The refreshed authentication token.
        refresh_token: str
            The refreshed refresh token.

`TimedSession(auth_token: str)`
:   TimedSession
    ------------
    Manages a time-limited authentication session with a service.
    
    This class represents a session authenticated via a JWT token with an expiration timestamp.
    It provides utilities to decode and extract information such as roles, tenant id, service URL,
    and external user ID. Additionally, it generates and validates session IDs and keeps track of
    expiration and refreshability.
    
    Attributes
    ----------
    tenant_id : str
        ID of the tenant associated with the session.
    roles : str
        Roles assigned to the session.
    service_url : str
        URL of the service the session is authenticated with.
    external_user_id : str
        External user identifier for the session.
    expiration : datetime
        Timestamp indicating when the session token expires.
    auth_token : str
        JWT token used for authenticating the session.
    id : str
        Unique identifier for the session derived from the service URL, tenant ID, and external user ID.
    expires_in : float
        Number of seconds until the session token expires.
    expired : bool
        Indicates whether the session has expired.
    refreshable : bool
        Indicates whether the session token can be refreshed.

    ### Ancestors (in MRO)

    * knowledge.services.session.Session
    * abc.ABC

    ### Descendants

    * knowledge.services.session.RefreshableSession

    ### Static methods

    `extract_session_id(auth_key: str) ‑> str`
    :   Extract the session id from the authentication key.
        Parameters
        ----------
        auth_key: str
            Authentication key.
        
        Returns
        -------
        session_id: str
            Session id.

    ### Instance variables

    `auth_token: str`
    :   JWT token for the session encoding the user id.

    `expiration: datetime.datetime`
    :   Timestamp when the token expires.

    `external_user_id: str`
    :   External user id.

    `id: str`
    :   Session id.

    `roles: str`
    :   Roles.

    `service_url: str`
    :   Service url.

`TokenManager()`
:   TokenManager
    ------------
    
    Manages sessions for authentication and authorization.
    
    The `TokenManager` class provides functionality to handle different types of
    sessions including permanent, refreshable, and timed sessions. It ensures thread-safe
    operations for adding, retrieving, removing, and maintaining sessions. It also
    includes utilities for cleaning up expired sessions.
    
    Attributes
    ----------
    sessions : Dict[str, Union[TimedSession, RefreshableSession, PermanentSession]]
        A dictionary mapping session ids to their corresponding session objects.

    ### Instance variables

    `session_count: int`
    :   Number of active sessions.

    ### Methods

    `add_session(self, auth_token: str, refresh_token: str | None = None, tenant_api_key: str | None = None, external_user_id: str | None = None) ‑> knowledge.services.session.PermanentSession | knowledge.services.session.RefreshableSession | knowledge.services.session.TimedSession`
    :   Add a session.
        Parameters
        ----------
        auth_token: str
            The authentication token.
        refresh_token: Optional[str] [default := None]
            The refresh token.
        tenant_api_key: Optional[str] [default := None]
            The tenant api key.
        external_user_id: Optional[str] [default := None]
            The external user id.
        
        Returns
        -------
        session: Union[PermanentSession, RefreshableSession, TimedSession]
            The logged-in session.

    `cleanup_expired_sessions(self) ‑> int`
    :   Removes expired sessions from the session store.
        
        Returns
        -------
        int
            The number of expired sessions removed.

    `get_session(self, session_id: str) ‑> knowledge.services.session.RefreshableSession | knowledge.services.session.TimedSession | knowledge.services.session.PermanentSession | None`
    :   Get a session by its id.
        
        Parameters
        ----------
        session_id: str
            Session id.
        
        Returns
        -------
        session: Union[RefreshableSession, TimedSession, PermanentSession]
            Depending on the session type, the session is returned.

    `has_session(self, session_id: str) ‑> bool`
    :   Check if a session exists.
        
        Parameters
        ----------
        session_id: str
            Session id.
        
        Returns
        -------
        available: bool
            True if the session exists, otherwise False.

    `remove_session(self, session_id: str)`
    :   Remove a session by its id.
        
        Parameters
        ----------
        session_id: str
            Session id.