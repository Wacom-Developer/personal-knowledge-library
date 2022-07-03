# -*- coding: utf-8 -*-
# Copyright © 2021-2022 Wacom. All rights reserved.
import argparse
import os
from pathlib import Path
from typing import List, Dict, Optional

import ndjson
from tqdm import tqdm

from knowledge.base.ontology import OntologyClassReference
from knowledge.base.ontology import ThingObject
from knowledge.services.graph import WacomKnowledgeService

THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')


def print_summary(total: int, types: Dict[str, int], languages: Dict[str, int]):
    print('---------------------------------------------------------------------------------------------------')
    print(f' Total number: {total}')
    print('---------------------------------------------------------------------------------------------------')
    print('Concept Types:')
    print('---------------------------------------------------------------------------------------------------')
    for c_type, count in types.items():
        print(f' {c_type}: {count}')
    print('---------------------------------------------------------------------------------------------------')
    print('Label Languages:')
    print('---------------------------------------------------------------------------------------------------')
    for language_code, count in languages.items():
        print(f' {language_code}: {count}')
    print('---------------------------------------------------------------------------------------------------')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.")
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.")
    parser.add_argument("-r", "--relations", action="store_true", help="Include the relations in the dump.")
    parser.add_argument("-d", "--dump", default='dump.ndjson', help="Defines the location of an ndjson dump file.")
    parser.add_argument("-i", "--instance", default='https://stage-private-knowledge.wacom.com', help="URL of instance")
    args = parser.parse_args()

    # Wacom personal knowledge REST API Client
    wacom_client: WacomKnowledgeService = WacomKnowledgeService(application_name="Wacom Knowledge Listing",
                                                                service_url=args.instance)
    user_auth_key: str = wacom_client.request_user_token(args.tenant, args.user)
    page_id: Optional[str] = None
    page_number: int = 1
    entity_count: int = 0
    types_count: Dict[str, int] = {}
    languages_count: Dict[str, int] = {}
    dump_mode: bool = len(args.dump) > 0
    dump_entities: List[ThingObject] = []
    dump_file: Path = Path(args.dump)
    if not os.path.exists(dump_file.parent):
        dump_file.parent.mkdir(parents=True, exist_ok=True)
    # Writing items to a ndjson file
    with open(dump_file, 'w') as f:
        writer = ndjson.writer(f, ensure_ascii=False)

        while True:
            # pull
            entities, total_number, next_page_id = wacom_client.listing(user_auth_key,
                                                                        THING_OBJECT,
                                                                        page_id=page_id, limit=1000)
            if args.relations:
                for e in tqdm(entities, desc="Pulling relations"):
                    relations = wacom_client.relations(auth_key=user_auth_key, uri=e.uri)
                    e.object_properties = relations
            if dump_mode:
                dump_entities.extend(entities)
            pulled_entities: int = len(entities)
            entity_count += pulled_entities
            if pulled_entities == 0:
                print_summary(total_number, types_count, languages_count)
                break
            for e in entities:
                if e.concept_type.iri not in types_count:
                    types_count[e.concept_type.iri] = 0
                types_count[e.concept_type.iri] += 1
                for label in e.label:
                    if label.language_code not in languages_count:
                        languages_count[label.language_code] = 0
                    languages_count[label.language_code] += 1
                # Write entity to cache file
                writer.writerow(e.__dict__())
            page_number += 1
            page_id = next_page_id
