Module knowledge.base.response
==============================

Classes
-------

`ErrorDetail(severity: str, reason: str, position_offset: int, timestamp: str)`
:   ErrorDetail
    ----------
    Represents an error detail.
    
    Parameters
    ----------
    severity: str
        The severity of the error.
    reason: str
        The reason for the error.
    position_offset: int
        The position offset of the error in the file.
    timestamp: str
        The timestamp of the error in ISO 8601 format.

    ### Instance variables

    `position_offset: int`
    :   The position offset of the error in the file.

    `reason: str`
    :   The reason for the error.

    `severity: str`
    :   The severity of the error.

    `timestamp: datetime.datetime`
    :   The timestamp of the error in ISO 8601 format.

`ErrorLogEntry(source_reference_id: str | None, errors: List[knowledge.base.response.ErrorDetail])`
:   ErrorLogEntry
    -------------
    Represents an entry in the error log.

    ### Instance variables

    `errors: List[knowledge.base.response.ErrorDetail]`
    :   The list of errors.

    `source_reference_id: str | None`
    :   The source reference ID.

`ErrorLogResponse(next_page_id: str, error_log: List[knowledge.base.response.ErrorLogEntry])`
:   ErrorLogResponse
    ----------------
    Represents the response for error log.

    ### Static methods

    `from_dict(param: Dict[str, Any]) ‑> knowledge.base.response.ErrorLogResponse`
    :   Create an ErrorLogResponse instance from a dictionary.
        Parameters
        ----------
        param: Dict[str, Any]
            Response data from the API.
        
        Returns
        -------
        instance: ErrorLogResponse
            Instance of ErrorLogResponse.

    ### Instance variables

    `error_log: List[knowledge.base.response.ErrorLogEntry]`
    :   The list of error log entries.

    `next_page_id: str`
    :   The ID of the next page.

`JobStatus(user_id: str, tenant_id: str, internal_job_id: str, job_id: str, status: Literal['Pending', 'InProgress', 'Completed', 'Failed', 'Retrying'], processed_entities: int = 0, processed_relations: int = 0, processed_images: int = 0, started_at: datetime.datetime | None = None, finished_at: datetime.datetime | None = None, failures: int = 0)`
:   JobStatus
    ---------
    Represents the status of a job.
    
    Parameters
    ----------
    user_id: str
        Identifies the user who started the job.
    tenant_id: str
        Identifies the tenant where the entities are imported.
    internal_job_id: str
        Identifies the internal job ID.
    job_id: str
        Identifies the job ID.
    status: Literal["Pending", "InProgress", "Completed", "Failed", "Retrying"]
        The status of the job. Possible values are:
        - Pending - The job is pending.
        - InProgress - The job is in progress.
        - Completed - The job is completed.
        - Failed - The job has failed.
        - Retrying - The job is being retried.
    processed_entities: int
        The number of processed entities.
    processed_relations: int
        The number of processed relations.
    processed_images: int
        The number of processed images.
    started_at: Optional[datetime]
        The timestamp when the job started.
    finished_at: Optional[datetime]
        The timestamp when the job finished.

    ### Class variables

    `COMPLETED: str`
    :   The job is completed.

    `FAILED: str`
    :   The job has failed.

    `IN_PROGRESS: str`
    :   The job is in progress. It has started but not yet completed.

    `PENDING: str`
    :   The job is pending. It has not started yet, as another job is in progress.

    `RETRYING: str`
    :   The job is being retried.

    ### Static methods

    `from_dict(data: Dict[str, Any]) ‑> knowledge.base.response.JobStatus`
    :   Create a JobStatus instance from a dictionary.
        Parameters
        ----------
        data: Dict[str, Any]
            Response data from the API.
        
        Returns
        -------
        instance: JobStatus
            Instance of JobStatus.

    ### Instance variables

    `failures: int`
    :   The number of failures encountered during the job.

    `finished_at: datetime.datetime | None`
    :   The timestamp when the job finished.

    `internal_job_id: str`
    :   Identifies the internal job ID.

    `job_id: str`
    :   Identifies the job ID.

    `processed_entities: int`
    :   The number of processed entities.

    `processed_images: int`
    :   The number of processed images.

    `processed_relations: int`
    :   The number of processed relations.

    `started_at: datetime.datetime | None`
    :   The timestamp when the job started.

    `status: Literal['Pending', 'InProgress', 'Completed', 'Failed', 'Retrying']`
    :   The status of the job. Possible values are:
        - Pending - The job is pending.
        - InProgress - The job is in progress.
        - Completed - The job is completed.
        - Failed - The job has failed.
        - Retrying - The job is being retried.

    `tenant_id: str`
    :   Identifies the tenant where the entities are imported.

    `user_id: str`
    :   Identifies the user who started the job.

`NewEntityUrisResponse(new_entities_uris: List[Dict[str, str]], next_page_id: str | None)`
:   NewEntityUrisResponse
    -------------------
    Represents the response for new entities.
    
    Parameters
    ----------
    new_entities_uris: Dict[str, str]
        The mapping of entity IDs to URIs (ref_id -> uri).
    next_page_id: Optional[str]
        Next page ID for pagination.

    ### Static methods

    `from_dict(param: Dict[str, Any]) ‑> knowledge.base.response.NewEntityUrisResponse`
    :   Create a NewEntityUrisResponse instance from a dictionary.
        Parameters
        ----------
        param: Dict[str, Any]
            Response data from the API.
        
        Returns
        -------
        instance: NewEntityUrisResponse
            Instance of NewEntityUrisResponse.

    ### Instance variables

    `new_entities_uris: Dict[str, str]`
    :   The mapping of entity IDs to URIs.

    `next_page_id: str | None`
    :   The ID of the next page.