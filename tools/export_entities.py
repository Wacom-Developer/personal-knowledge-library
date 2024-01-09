# -*- coding: utf-8 -*-
# Copyright © 2023-24 Wacom. All rights reserved.
import argparse
from pathlib import Path
from typing import Union, Dict, List

import ndjson
import requests
from tqdm import tqdm

from knowledge.base.ontology import OntologyClassReference, DataProperty, SYSTEM_SOURCE_REFERENCE_ID, \
    SYSTEM_SOURCE_SYSTEM, EN_US
from knowledge.base.ontology import ThingObject
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.session import PermanentSession
from knowledge.utils.graph import count_things, things_iter


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
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        img_offline: Path = user_images_path / f'{uri}.png'
        with img_offline.open('wb') as fp_img:
            for chunk in r.iter_content(chunk_size=8192):
                fp_img.write(chunk)
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
    parser.add_argument("-c", "--concept_type", default='wacom:core#Thing', help="Concept type to filter.")
    parser.add_argument("-i", "--instance", default='https://private-knowledge.wacom.com',
                        help="URL of instance. (default:=https://private-knowledge.wacom.com)")
    args = parser.parse_args()
    filter_type: OntologyClassReference = OntologyClassReference.parse(args.concept_type)
    # Wacom personal knowledge REST API Client
    wacom_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Wacom Knowledge Listing",
        service_url=args.instance)
    session: PermanentSession = wacom_client.login(args.tenant, args.user)
    next_page_id: Union[str, None] = None
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
    total_number: int = count_things(wacom_client, session.auth_token, filter_type)
    print(f'Found {total_number} entities.')
    delete_uri: List[str] = []
    pbar: tqdm = tqdm(things_iter(wacom_client, session.auth_token, session.refresh_token, filter_type),
                      f"Export entities. [tenant:={args.tenant}, user:={args.user}]")
    # Writing items to a ndjson file
    with open(dump_file, 'w', encoding='utf-8') as fp_dump:
        writer: ndjson.writer = ndjson.writer(fp_dump, ensure_ascii=False)
        for e, _, _ in pbar:
            if not args.all and not e.owner:
                continue
            if args.relations:
                if e.owner or args.all:
                    pbar.set_description(f"Relation for {e.uri} - {e.label[0].content} - ({e.concept_type.iri})")
                    relations = wacom_client.relations( uri=e.uri)
                    e.object_properties = relations

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
                    pbar.set_description(f'Export entity: {e.label_lang(EN_US)}')
                # Write entity to cache file
                writer.writerow(e.__import_format_dict__())
            page_number += 1
    print_summary(total_number, types_count, languages_count)

