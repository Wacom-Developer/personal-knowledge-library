Module knowledge.utils.rdf
==========================

Functions
---------

    
`ontology_import(rdf_content: str, tenant_id: str = '', context: str = '') ‑> knowledge.base.ontology.Ontology`
:   Import Ontology from RDF ontology file.
    
    Parameters
    ----------
    rdf_content: str
        Content of the RDF content file.
    tenant_id: str (default:= '')
        Tenant ID.
    context: str (default:= '')
        Context file.
    
    Returns
    -------
    ontology: Ontology
        Instance of ontology.