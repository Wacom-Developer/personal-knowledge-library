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
:   RefreshableSession
    ------------------
    The session class holds the information about the session.

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
    The session class holds the information about the session.
    As there is refresh token, the session can be refreshed.

    ### Ancestors (in MRO)

    * knowledge.services.session.TimedSession
    * knowledge.services.session.Session
    * abc.ABC

    ### Descendants

    * knowledge.services.session.PermanentSession

    ### Instance variables

    `refresh_token: str`
    :   Refresh token for the session.

`Session()`
:   Session
    -------
    Abstract session class.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * knowledge.services.session.TimedSession

    ### Instance variables

    `auth_token: str`
    :   Authentication key. The authentication key is used to identify an external user withing private knowledge.

    `expired: bool`
    :   Is the session expired.

    `expires_in: float`
    :   Seconds until token is expired in seconds.

    `id: str`
    :   Unique session id, which will be the same for the same external user id, tenant,
        and instance of the service.

    `refresh_token: Optional[str]`
    :   Refresh token. The refresh token is used to refresh the session.

    `refreshable: bool`
    :   Is the session refreshable.

    `tenant_id: str`
    :   Tenant id.

    ### Methods

    `refresh_session(self, auth_token: str, refresh_token: str)`
    :   Refresh the session.
        Parameters
        ----------
        auth_token: str
            The refreshed authentication token.
        refresh_token: str
            The refreshed refresh token.

`TimedSession(auth_token: str)`
:   TimedSession
    ----------------
    The timed session is only valid until the token expires. There is no refresh token, thus the session cannot be
    refreshed.

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
    The token manager is a singleton that holds all the sessions for the users.

    ### Methods

    `add_session(self, auth_token: str, refresh_token: Optional[str] = None, tenant_api_key: Optional[str] = None, external_user_id: Optional[str] = None) ‑> Union[knowledge.services.session.PermanentSession, knowledge.services.session.RefreshableSession, knowledge.services.session.TimedSession]`
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

    `get_session(self, session_id: str) ‑> Union[knowledge.services.session.RefreshableSession, knowledge.services.session.TimedSession, knowledge.services.session.PermanentSession, ForwardRef(None)]`
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