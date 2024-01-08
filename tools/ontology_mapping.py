# -*- coding: utf-8 -*-
# Copyright © 2023-24 Wacom. All rights reserved.
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from ontospy import Ontospy, OntoProperty
from rdflib import URIRef

from knowledge.base.ontology import OntologyContext
from knowledge.ontomapping import CLASSES, DATA_PROPERTIES, OBJECT_PROPERTIES, DOMAIN_PROPERTIES, WIKIDATA_TYPES, \
    DBPEDIA_TYPES, CONTEXT_NAME
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tenant", help="Tenant id for managing the tenants.")
    parser.add_argument("-u", "--user", help="External user id.")
    parser.add_argument("-i", "--instance", help="URL of instance", default='https://private-knowledge.wacom.com')
    parser.add_argument("-m", "--mapping", help="Mapping files.", default='../pkl-cache/ontology_mapping.json')
    args = parser.parse_args()
    datatypes: Dict[str, int] = {}
    mapping_file: Path = Path(args.mapping)
    if mapping_file.exists():
        with mapping_file.open('r') as fp:
            mapping: Dict[str, Any] = json.loads(fp.read())
    else:
        mapping: Dict[str, Any] = {
            CLASSES: {},
            DATA_PROPERTIES: {},
            OBJECT_PROPERTIES: {}
        }

    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(service_url=args.instance,
                                                                    application_name="Ontology")

    ontology_client: OntologyService = OntologyService(service_url=args.instance)
    admin_token, refresh, expire = knowledge_client.request_user_token(args.tenant, args.user)
    context: OntologyContext = ontology_client.context(admin_token)
    if not context:
        # First, create a context for the ontology
        ontology_client.create_context(admin_token, name=CONTEXT_NAME, base_uri=f'wacom:{CONTEXT_NAME}')
        context_name: str = CONTEXT_NAME
    else:
        context_name: str = context.context
    model: Ontospy = Ontospy(data=ontology_client.rdf_export(admin_token, context_name), verbose=False)
    for c in model.all_classes:
        c_uri: str = str(c.uri)
        if c_uri in mapping[CLASSES]:
            mapping[CLASSES][c_uri][DOMAIN_PROPERTIES] = []
        else:
            mapping[CLASSES][c_uri] = {
                WIKIDATA_TYPES: [],
                DBPEDIA_TYPES: [],
                DOMAIN_PROPERTIES: []
            }
        for domain in c.domain_of_inferred:
            for dom_class, dom_props in domain.items():
                mapping[CLASSES][c_uri][DOMAIN_PROPERTIES].append({
                    "class": dom_class.uri,
                    "property": [str(d.uri) for d in dom_props]
                })

    for c in model.all_properties_datatype:
        if c.uri in mapping[DATA_PROPERTIES]:
            mapping[DATA_PROPERTIES][str(c.uri)] = {
                "property": c.uri,
                "type": c.rdftype_qname,
                "domains": [str(d.uri) for d in c.domains],
                "ranges": [str(r.uri) for r in c.ranges]
            }
        else:
            mapping[DATA_PROPERTIES][str(c.uri)] = {
                WIKIDATA_TYPES: [],
                "property": c.uri,
                "type": c.rdftype_qname,
                "domains": [str(d.uri) for d in c.domains],
                "ranges": [str(r.uri) for r in c.ranges]
            }
    for c in model.all_properties_object:
        props: List[URIRef] = c.getValuesForProperty('http://www.w3.org/2002/07/owl#inverseOf')
        inv: Optional[OntoProperty] = None
        if len(props) > 0:
            inv = model.get_property(uri=props[0])
        if c.uri in mapping[OBJECT_PROPERTIES]:
            mapping[OBJECT_PROPERTIES][str(c.uri)] = {
                "property": c.uri,
                "inverse": str(inv.uri) if inv is not None else None,
                "type": c.rdftype_qname,
                "domains": [str(d.uri) for d in c.domains],
                "ranges": [str(r.uri) for r in c.ranges]
            }
        else:
            mapping[OBJECT_PROPERTIES][str(c.uri)] = {
                WIKIDATA_TYPES: [],
                "property": c.uri,
                "inverse": str(inv.uri) if inv is not None else None,
                "type": c.rdftype_qname,
                "domains": [str(d.uri) for d in c.domains],
                "ranges": [str(r.uri) for r in c.ranges]
            }
    with Path(args.mapping).open("w") as fp:
        fp.write(json.dumps(mapping, indent=2))
