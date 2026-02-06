Module knowledge.services.helper
================================

Variables
---------

`RELATIONS_BULK_LIMIT: int`
:   In one request only 30 relations can be created, otherwise the database operations are too many.

Functions
---------

`entity_payload(entity: knowledge.base.ontology.ThingObject) ‑> Dict[str, Any]`
:   Create the payload for the entity.
    Parameters
    ----------
    entity: ThingObject
        The entity to create the payload for.
    
    Returns
    -------
    Dict[str, Any]
        The payload for the entity.

`split_updates(updates: Dict[knowledge.base.ontology.OntologyPropertyReference, List[str]], max_operations: int = 30) ‑> Iterator[List[Dict[str, str | List[str]]]]`
:   Parameters
    ----------
    updates: Dict[OntologyPropertyReference, List[str]]
        The updates to split into batches.
    max_operations: int (default: RELATIONS_BULK_LIMIT)
        The maximum number of operations
    
    Yields
    -------
    batch: List[Dict[str, Union[str, List[str]]]]
        The batch of updates to process.