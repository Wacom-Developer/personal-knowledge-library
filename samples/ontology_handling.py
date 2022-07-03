# -*- coding: utf-8 -*-
# Copyright © 2021-2022 Wacom Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language_code governing permissions and
#  limitations under the License.
import argparse
from typing import List, Tuple

from knowledge.base.entity import OntologyContext
from knowledge.base.ontology import OntologyClassReference, OntologyPropertyReference, OntologyClass, OntologyProperty,\
    Ontology
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService
from knowledge.utils.rdf import ontology_import

RESOURCE: str = "http://www.w3.org/2000/01/rdf-schema#Resource"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default="https://stage-private-knowledge.wacom.com", help="URL of instance")
    args = parser.parse_args()
    TENANT_KEY: str = args.tenant
    EXTERNAL_USER_ID: str = args.user
    # Wacom Ontology REST API Client
    ontology_client: OntologyService = OntologyService(service_url=args.instance)
    auth_key: str = ontology_client.request_user_token(TENANT_KEY, EXTERNAL_USER_ID)
    # Use special tenant for testing:  Unit-test tenant
    contexts: List[OntologyContext] = ontology_client.contexts(auth_key)
    if len(contexts) == 0:
        # No context available. So, let's create one
        ontology_client.create_context(auth_key, name="base")
        ontology_client.commit(auth_key, context_name="base")
        knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
            application_name="Wacom Knowledge Listing", service_url=args.instance)
        knowledge_client.ontology_update(auth_key)
        contexts: List[OntologyContext] = ontology_client.contexts(auth_key)

    # All context create for a tenant.
    for c in contexts:
        desc = ontology_client.context_metadata(auth_key, c.context)
        concepts: List[Tuple[OntologyClassReference, OntologyClassReference]] = ontology_client.concepts(auth_key,
                                                                                                         c.iri)
        # All context create for a tenant.
        print('-------------------------------------------------------------------------------------------------------')
        print(f' Concepts for: {c.iri}.')
        print('-------------------------------------------------------------------------------------------------------')
        for cpt, subclass_of_ref in sorted(concepts, key=lambda v: v[0].iri):
            if cpt.iri.startswith('wacom'):
                onto_class: OntologyClass = ontology_client.concept(auth_key, c.iri, cpt.iri)
                print(f'{onto_class.reference.context.upper()}_{onto_class.reference.name.upper()}: str = '
                      f'"{onto_class.iri}"')
        properties: List[Tuple[OntologyPropertyReference, OntologyPropertyReference]] = \
            ontology_client.properties(auth_key, c.iri)
        # All context create for a tenant.
        print('-------------------------------------------------------------------------------------------------------')
        print(f' Properties for: {c.iri}.')
        print('-------------------------------------------------------------------------------------------------------')
        for ontology_property_ref, sub_property_of_ref in properties:
            ontology_property: OntologyProperty = ontology_client.property(auth_key, c.iri, ontology_property_ref.iri)
            print(f'{ontology_property} -> {sub_property_of_ref}')

        print('-------------------------------------------------------------------------------------------------------')
        print(f' Properties for: {c.iri}.')
        print('-------------------------------------------------------------------------------------------------------')
        properties: List[Tuple[OntologyPropertyReference, OntologyPropertyReference]] = \
            ontology_client.properties(auth_key, c.iri)
        for ontology_property_ref, sub_property_ref in properties:
            ontology_property: OntologyProperty = ontology_client.property(auth_key, c.iri, ontology_property_ref.iri)
            print(ontology_property)
        print('-------------------------------------------------------------------------------------------------------')
        print('Export RDF ')
        print('-------------------------------------------------------------------------------------------------------')
        rdf_content: str = ontology_client.rdf_export(auth_key, c.iri)
        ontology: Ontology = ontology_import(rdf_content, TENANT_KEY, c.iri)
        print('Data properties for wacom:core#Person:')
        print(ontology.data_properties_for(OntologyClassReference.parse("wacom:core#Person")))
        print('Object properties for wacom:core#Person:')
        print(ontology.object_properties_for(OntologyClassReference.parse("wacom:core#Person")))

