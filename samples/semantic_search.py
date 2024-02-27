# -*- coding: utf-8 -*-
# Copyright © 2024 Wacom Authors. All Rights Reserved.
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
import re
import time
from typing import List, Dict, Any

from knowledge.base.language import EN_US
from knowledge.base.search import LabelMatchingResponse, DocumentSearchResponse, VectorDBDocument
from knowledge.services.search import SemanticSearchClient


def clean_text(text: str, max_length: int = -1) -> str:
    """
    Clean text from new lines and multiple spaces.

    Parameters
    ----------
    text: str
        Text to clean.
    max_length: int [default=-1]
        Maximum length of the cleaned text. If length is - 1 then the text is not truncated.

    Returns
    -------
    str
        Cleaned text.
    """
    # First remove new lines
    text = text.strip().replace('\n', ' ')
    # Then remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    if 0 < max_length < len(text):
        return text[:max_length] + '...'
    return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    args = parser.parse_args()
    client: SemanticSearchClient = SemanticSearchClient(service_url=args.instance)
    session = client.login(args.tenant, args.user)
    max_results: int = 10
    labels_count: int = client.count_documents(locale=EN_US)
    print(f"Tenant ID: {client.current_session.tenant_id} | Labels count: {labels_count} for [locale:={EN_US}]")
    t0: float = time.time()
    results: LabelMatchingResponse = client.labels_search(query="Leonardo Da Vinci", locale=EN_US,
                                                          max_results=max_results)
    t1: float = time.time()
    if len(results.results) > 0:
        print("=" * 120)
        for idx, res in enumerate(results.results):
            print(f"{idx + 1}. {res.label} | Relevance: ({res.score:.2f}) | URI: {res.entity_uri}")
        all_labels: List[VectorDBDocument] = client.retrieve_labels(EN_US, results.results[0].entity_uri)
        print("=" * 120)
        print(f"Labels for best match: {results.results[0].entity_uri}")
        for idx, label in enumerate(all_labels):
            print(f"{idx + 1}. {label.content}")
    print("=" * 120)
    print(f"Time: {(t1 - t0) * 1000:.2f} ms")
    print("=" * 120)
    document_count: int = client.count_documents(locale=EN_US)
    print(f"Document count: {document_count} for [locale:={EN_US}]")
    t2: float = time.time()
    document_results: DocumentSearchResponse = client.document_search(query="Leonardo Da Vinci artwork", locale=EN_US,
                                                                      max_results=max_results)
    t3: float = time.time()
    print("=" * 120)
    if len(document_results.results) > 0:

        for idx, res in enumerate(document_results.results):
            print(f"{idx + 1}.  URI: {res.content_uri} | Relevance: {res.score:.2f} | Chunk:"
                  f"\n\t{clean_text(res.content_chunk, max_length=100)}")
        print(f"\n All document chunks for best match: {document_results.results[0].content_uri}")
        print("=" * 120)
        # If you need all document chunks, you can retrieve them using the content_uri.
        best_match_uri: str = document_results.results[0].content_uri
        chunks: List[VectorDBDocument] = client.retrieve_documents_chunks(locale=EN_US, uri=best_match_uri)
        metadata: Dict[str, Any] = document_results.results[0].metadata
        for idx, chunk in enumerate(chunks):
            print(f"{idx + 1}. {clean_text(chunk.content)}")
        print("\n\tMetadata:\n\t---------")
        for key, value in metadata.items():
            print(f"\t- {key}: {clean_text(value, max_length=100) if isinstance(value, str) else value }")
    print("=" * 120)
    print(f"Time: {(t3 - t2) * 1000:.2f} ms")
    print("=" * 120)
