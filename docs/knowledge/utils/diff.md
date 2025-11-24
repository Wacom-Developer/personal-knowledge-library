Module knowledge.utils.diff
===========================

Functions
---------

`diff_entities(client: knowledge.services.graph.WacomKnowledgeService, file_thing: knowledge.base.ontology.ThingObject, kg_thing: knowledge.base.ontology.ThingObject, kg_things: Dict[str, knowledge.base.ontology.ThingObject] | None = None) ‑> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]`
:   Check the differences between the two entities.
    
    Parameters
    ----------
    client: WacomKnowledgeService
        The client to use.
    file_thing: ThingObject
        The thing to check.
    kg_thing: ThingObject
        The knowledge graph entity to check.
    kg_things: Optional[Dict[str, ThingObject]]
        The entities in the knowledge graph.
    
    Returns
    -------
    differences: List[Dict[str, Any]]
        The differences.
    difference_data_properties: List[Dict[str, Any]]
        The differences in the data properties.
    difference_object_properties: List[Dict[str, Any]]
        The differences in the object properties.

`diff_entities_async(client: knowledge.services.asyncio.graph.AsyncWacomKnowledgeService, file_thing: knowledge.base.ontology.ThingObject, kg_thing: knowledge.base.ontology.ThingObject, kg_things: Dict[str, knowledge.base.ontology.ThingObject] | None = None) ‑> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]`
:   Check the differences between the two entities.
    
    Parameters
    ----------
    client: WacomKnowledgeService
        The client to use.
    file_thing: ThingObject
        The thing to check.
    kg_thing: ThingObject
        The knowledge graph entity to check.
    kg_things: Optional[Dict[str, ThingObject]]
        The entities in the knowledge graph.
    
    Returns
    -------
    differences: List[Dict[str, Any]]
        The differences.
    difference_data_properties: List[Dict[str, Any]]
        The differences in the data properties.
    difference_object_properties: List[Dict[str, Any]]
        The differences in the object properties.

`is_different(client: knowledge.services.graph.WacomKnowledgeService, thing_file: knowledge.base.ontology.ThingObject, thing_kg: knowledge.base.ontology.ThingObject) ‑> bool`
:   Check if the two entities are different.
    
    Parameters
    ----------
    client: WacomKnowledgeService
        The client to use.
    thing_file: ThingObject
        The thing from the file.
    thing_kg: ThingObject
        The thing from the knowledge graph.
    
    Returns
    -------
    is_different: bool
        True if the entities are different, False otherwise.

`is_different_async(client: knowledge.services.asyncio.graph.AsyncWacomKnowledgeService, thing_file: knowledge.base.ontology.ThingObject, thing_kg: knowledge.base.ontology.ThingObject) ‑> bool`
:   Check if the two entities are different.
    
    Parameters
    ----------
    client: WacomKnowledgeService
        The client to use.
    thing_file: ThingObject
        The thing from the file.
    thing_kg: ThingObject
        The thing from the knowledge graph.
    
    Returns
    -------
    is_different: bool
        True if the entities are different, False otherwise.