# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
import argparse
from pathlib import Path
from typing import List, Dict, Optional

import ndjson
import requests
from tqdm import tqdm

from knowledge.base.entity import LanguageCode
from knowledge.base.ontology import OntologyClassReference, DataProperty, SYSTEM_SOURCE_REFERENCE_ID, \
    SYSTEM_SOURCE_SYSTEM
from knowledge.base.ontology import ThingObject
from knowledge.services.graph import WacomKnowledgeService

THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')
EN_US: LanguageCode = LanguageCode('en_US')


def download_file(url: str, user_images_path: Path, uri: str) -> str:
    """
    Download file from the given url and save it to the user_images_path.

    Parameters
    ----------
    url: str
        Url of the image.
    user_images_path: Path
        Path to the user images folder.
    uri: str
        Uri of the entity.

    Returns
    -------
    file_uri: str
        Uri of the downloaded file.
    """
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        img_offline: Path = user_images_path / f'{uri}.png'
        with img_offline.open('wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
            return img_offline.absolute().as_uri()


def print_summary(total: int, types: Dict[str, int], languages: Dict[str, int]):
    """
    Print summary of the listing.

    Parameters
    ----------
    total: int
        Total number of entities.
    types: Dict[str, int]
        Dictionary of types and their counts.
    languages: Dict[str, int]
        Dictionary of languages and their counts.

    """
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
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-r", "--relations", action="store_true", help="Include the relations in the dump.")
    parser.add_argument("-a", "--all", action="store_true",
                        help="All entities the user as access to, otherwise only his own entities are dumped.")
    parser.add_argument("-p", "--images", action="store_true", help="Include the images in the dump.")
    parser.add_argument("-d", "--dump", default='dump.ndjson', help="Defines the location of the dump path.")
    parser.add_argument("-i", "--instance", default='https://private-knowledge.wacom.com',
                        help="URL of instance. (default:=https://private-knowledge.wacom.com)")
    args = parser.parse_args()

    # Wacom personal knowledge REST API Client
    wacom_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Wacom Knowledge Listing",
        service_url=args.instance)
    user_auth_key, _, _ = wacom_client.request_user_token(args.tenant, args.user)
    page_id: Optional[str] = None
    page_number: int = 1
    entity_count: int = 0
    types_count: Dict[str, int] = {}
    languages_count: Dict[str, int] = {}
    dump_mode: bool = len(args.dump) > 0
    dump_entities: List[ThingObject] = []
    dump_path: Path = Path(args.dump)
    dump_file: Path = dump_path / 'entities.ndjson'
    images_path: Path = dump_path / 'images'
    dump_path.mkdir(parents=True, exist_ok=True)
    images_path.mkdir(parents=True, exist_ok=True)
    # Writing items to a ndjson file
    with open(dump_file, 'w') as f:
        writer = ndjson.writer(f, ensure_ascii=False)
        while True:
            # pull
            entities, total_number, next_page_id = wacom_client.listing(user_auth_key,
                                                                        THING_OBJECT,
                                                                        page_id=page_id, limit=1000,
                                                                        estimate_count=True)
            if args.relations:
                pbar: tqdm = tqdm([e for e in entities if not args.all and not e.owner], desc="Extract relations.")
                for e in pbar:
                    pbar.set_description(f"Relation for {e.uri} - {e.label[0].content} - ({e.concept_type.iri})")
                    relations = wacom_client.relations(auth_key=user_auth_key, uri=e.uri)
                    e.object_properties = relations

            pulled_entities: int = len(entities)
            entity_count += pulled_entities
            if pulled_entities == 0:
                print_summary(total_number, types_count, languages_count)
                break
            pbar = tqdm(entities)
            for e in pbar:
                if not args.all and not e.owner:
                    continue
                if args.images and e.image:
                    e.image = download_file(e.image, images_path, e.uri)
                if e.concept_type.iri not in types_count:
                    types_count[e.concept_type.iri] = 0
                types_count[e.concept_type.iri] += 1
                e.add_source_system(DataProperty(content='wacom-knowledge', property_ref=SYSTEM_SOURCE_SYSTEM,
                                                 language_code=EN_US))
                e.add_source_reference_id(
                    DataProperty(content=e.uri, property_ref=SYSTEM_SOURCE_REFERENCE_ID,
                                 language_code=EN_US))
                for label in e.label:
                    if label.language_code not in languages_count:
                        languages_count[label.language_code] = 0
                    languages_count[label.language_code] += 1
                if isinstance(e, ThingObject):
                    pbar.set_description(f'Export entity: {e.label_lang(LanguageCode("en_US"))}')
                # Write entity to cache file
                writer.writerow(e.__dict__())
            page_number += 1
            page_id = next_page_id
