# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom Authors. All Rights Reserved.
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
"""
Content API sample
------------------
Demonstrates the full lifecycle of the Content API:

    1. Create a wacom:core#Page entity to own the content
    2. Upload a file linked to the entity URI
    3. Tag and annotate the content item
    4. Retrieve and inspect the content info
    5. Replace the stored file
    6. Upload a second file to show multi-content support
    7. List all content for the entity
    8. Delete individual items and bulk-delete everything
    9. Clean up the entity

Usage
-----
    python samples/content_handling.py \\
        --tenant <TENANT_API_KEY> \\
        --user   <EXTERNAL_USER_ID> \\
        --file   /path/to/file.png \\
        --instance https://private-knowledge.wacom.com
"""
import argparse
from pathlib import Path
from typing import Dict, List

from knowledge.base.content import ContentObject
from knowledge.base.language import EN_US
from knowledge.base.ontology import (
    DataProperty,
    OntologyClassReference,
    OntologyPropertyReference,
    ThingObject,
)
from knowledge.services.base import WacomServiceException
from knowledge.services.content import ContentClient
from knowledge.services.graph import WacomKnowledgeService

# ── Ontology references ────────────────────────────────────────────────────────
PAGE_TYPE: OntologyClassReference = OntologyClassReference.parse("wacom:core#Page")
CONTENT_PROP: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#content")


def create_page_entity(title: str) -> ThingObject:
    """
    Build a minimal wacom:core#Page entity.

    Parameters
    ----------
    title: str
        Label for the page entity.

    Returns
    -------
    page: ThingObject
        Configured page entity ready to be pushed to PKS.
    """
    page: ThingObject = ThingObject(concept_type=PAGE_TYPE)
    page.add_label(title, EN_US)
    page.add_description("Page entity created by the content_handling sample.", EN_US)
    page.add_data_property(
        DataProperty(
            content="Sample page content text.",
            property_ref=CONTENT_PROP,
            language_code=EN_US,
        )
    )
    # Disable all index types — this page is used only for content attachment
    page.use_full_text_index = False
    page.use_vector_index = False
    page.use_vector_index_document = False
    page.use_for_nel = False
    return page


def print_content_item(item: ContentObject, indent: str = "    ") -> None:
    """Print a ContentObject in a human-readable format."""
    print(f"{indent}ID          : {item.id}")
    print(f"{indent}MIME type   : {item.mime_type}")
    print(f"{indent}Tags        : {item.tags}")
    print(f"{indent}Metadata    : {item.metadata}")
    print(f"{indent}Added       : {item.date_added.isoformat()}")
    print(f"{indent}Modified    : {item.date_modified.isoformat()}")
    print(f"{indent}Deleted     : {item.is_deleted}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Content API sample for the Wacom Personal Knowledge Service.")
    parser.add_argument("-u", "--user", required=True, help="External user ID within the knowledge service.")
    parser.add_argument("-t", "--tenant", required=True, help="Tenant API key.")
    parser.add_argument("-f", "--file", required=True, help="Path to a file to upload as content.")
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="Service instance URL.")
    args = parser.parse_args()

    file_path: Path = Path(args.file)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # ── Clients ────────────────────────────────────────────────────────────────
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Content Handling Sample",
        service_url=args.instance,
    )
    content_client: ContentClient = ContentClient(
        service_url=args.instance,
        application_name="Content Handling Sample",
    )

    knowledge_client.login(args.tenant, args.user)
    content_client.login(args.tenant, args.user)

    # ── Step 1: Create a page entity ───────────────────────────────────────────
    print("Step 1 — Create entity")
    print("=" * 80)
    page: ThingObject = create_page_entity("Content Sample Page")
    entity_uri: str = knowledge_client.create_entity(page)
    print(f"    Entity URI  : {entity_uri}")
    print("=" * 80)

    try:
        # ── Step 2: Upload a file ──────────────────────────────────────────────
        print("\nStep 2 — Upload content file")
        print("=" * 80)
        file_bytes: bytes = file_path.read_bytes()
        # Derive a basic MIME type from the file extension
        mime_map: Dict[str, str] = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".pdf": "application/pdf",
            ".svg": "image/svg+xml",
        }
        mime_type: str = mime_map.get(file_path.suffix.lower(), "application/octet-stream")
        content_id: str = content_client.upload_content(
            uri=entity_uri,
            file_content=file_bytes,
            filename=file_path.name,
            mimetype=mime_type,
        )
        print(f"    Content ID  : {content_id}")
        print(f"    File        : {file_path.name}  ({len(file_bytes):,} bytes)  [{mime_type}]")
        print("=" * 80)

        # ── Step 3: Add tags ───────────────────────────────────────────────────
        print("\nStep 3 — Add tags")
        print("=" * 80)
        content_client.update_content_tags(
            content_id=content_id,
            tags=["sample", "content-api", "wacom"],
        )
        print("    Tags set    : ['sample', 'content-api', 'wacom']")
        print("=" * 80)

        # ── Step 4: Add metadata ───────────────────────────────────────────────
        print("\nStep 4 — Add metadata")
        print("=" * 80)
        content_client.update_content_metadata(
            content_id=content_id,
            metadata={"source": "content_handling_sample", "version": "1"},
        )
        print("    Metadata set: {'source': 'content_handling_sample', 'version': '1'}")
        print("=" * 80)

        # ── Step 5: Retrieve content info ──────────────────────────────────────
        print("\nStep 5 — Retrieve content info")
        print("=" * 80)
        info: ContentObject = content_client.get_content_info(content_id)
        print_content_item(info)
        print("=" * 80)

        # ── Step 6: Update tags and metadata in a single PATCH ─────────────────
        print("\nStep 6 — Combined update (tags + metadata)")
        print("=" * 80)
        updated: ContentObject = content_client.update_content(
            content_id=content_id,
            tags=["sample", "content-api", "wacom", "updated"],
            metadata={"source": "content_handling_sample", "version": "2", "status": "reviewed"},
        )
        print("    Updated item:")
        print_content_item(updated)
        print("=" * 80)

        # ── Step 7: Download and verify the file ───────────────────────────────
        print("\nStep 7 — Download and verify file")
        print("=" * 80)
        downloaded: bytes = content_client.download_content(content_id)
        match: bool = downloaded == file_bytes
        print(f"    Downloaded  : {len(downloaded):,} bytes")
        print(f"    Matches original: {match}")
        print("=" * 80)

        # ── Step 8: Replace the stored file ───────────────────────────────────
        print("\nStep 8 — Replace stored file (PUT)")
        print("=" * 80)
        replacement_bytes: bytes = b"This is replacement content for the sample."
        content_client.update_content_file(
            content_id=content_id,
            file_content=replacement_bytes,
            filename="replacement.txt",
        )
        replaced: bytes = content_client.download_content(content_id)
        print(f"    Replacement : {len(replacement_bytes):,} bytes")
        print(f"    Verified    : {replaced == replacement_bytes}")
        print("=" * 80)

        # ── Step 9: Upload a second file (multi-content) ───────────────────────
        print("\nStep 9 — Upload a second file (multi-content)")
        print("=" * 80)
        second_bytes: bytes = b"Second content item attached to the same entity."
        second_id: str = content_client.upload_content(
            uri=entity_uri,
            file_content=second_bytes,
            filename="second.txt",
            mimetype="text/plain",
        )
        print(f"    Second content ID : {second_id}")
        print("=" * 80)

        # ── Step 10: List all content for the entity ───────────────────────────
        print("\nStep 10 — List all content for entity")
        print("=" * 80)
        items: List[ContentObject] = content_client.list_content(entity_uri)
        print(f"    Total items : {len(items)}")
        for idx, item in enumerate(items, start=1):
            print(f"\n    [{idx}]")
            print_content_item(item, indent="        ")
        print("=" * 80)

        # ── Step 11: Delete the second item individually ───────────────────────
        print("\nStep 11 — Delete second content item")
        print("=" * 80)
        content_client.delete_content(second_id)
        after_single_delete: List[ContentObject] = content_client.list_content(entity_uri)
        remaining_ids = [i.id for i in after_single_delete if not i.is_deleted]
        print(f"    Deleted     : {second_id}")
        print(f"    Remaining   : {remaining_ids}")
        print("=" * 80)

        # ── Step 12: Bulk-delete all remaining content ─────────────────────────
        print("\nStep 12 — Bulk delete all content for entity")
        print("=" * 80)
        content_client.delete_all_content(entity_uri)
        after_bulk_delete: List[ContentObject] = content_client.list_content(entity_uri)
        active_after: List[ContentObject] = [i for i in after_bulk_delete if not i.is_deleted]
        print(f"    Active items after bulk delete: {len(active_after)}")
        print("=" * 80)

    except WacomServiceException as exc:
        print(f"\nError: {exc}")
    finally:
        # ── Step 13: Clean up the entity ──────────────────────────────────────
        print("\nStep 13 — Delete entity")
        print("=" * 80)
        knowledge_client.delete_entity(entity_uri, force=True)
        print(f"    Deleted entity : {entity_uri}")
        print("=" * 80)
