Module knowledge.base
=====================
Base structures.
----------------
This module provides the base structures for the knowledge graph.
Such as the ontology, entities and access.

The classes in this module are used by the knowledge graph service.
For instance, the ontology structure is used to create the structure knowledge graph.
The entities are used to store the knowledge graph.

The access is used to access the knowledge graph, there are different types of access:
    - Private access: the user can access only the entities that he/she created.
    - Public access: the user can access all the entities.
    - Group access: the user can access the entities that are in the same group.

Sub-modules
-----------
* knowledge.base.access
* knowledge.base.entity
* knowledge.base.language
* knowledge.base.ontology
* knowledge.base.search
* knowledge.base.tenant