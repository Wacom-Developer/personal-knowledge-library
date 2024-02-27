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

from knowledge.base.language import LocaleCode, EN_US
from knowledge.base.search import DocumentSearchResponse, VectorDBDocument
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

def search_document(query: str, locale: LocaleCode, tenant_api_key: str, external_user_id: str, instance_url: str,
                    max_results: int):
    """
    Search for words in the knowledge graph.

    Parameters
    ----------
    query: str
        Word to search for.
    locale: str
        Locale of the word.
    tenant_api_key: str
        Tenant API key.
    external_user_id: str
        External user id.
    instance_url: str
        URL of the instance.
    max_results: int
        Maximum number of results.
    """
    client: SemanticSearchClient = SemanticSearchClient(service_url=instance_url)
    client.login(tenant_api_key, external_user_id)
    t0: float = time.time()
    document_results: DocumentSearchResponse = client.document_search(query=query, locale=locale,
                                                                      max_results=max_results)
    t1: float = time.time()
    print("=" * 120)
    if len(document_results.results) > 0:

        for idx, res in enumerate(document_results.results):
            print(f"{idx + 1}.  URI: {res.content_uri} | Relevance: {res.score:.2f} | Chunk:"
                  f"\n\t{clean_text(res.content_chunk, max_length=100)}")
        print(f"\n All document chunks for best match: {document_results.results[0].content_uri}")
        print("=" * 120)
        # If you need all document chunks, you can retrieve them using the content_uri.
        best_match_uri: str = document_results.results[0].content_uri
        chunks: List[VectorDBDocument] = client.retrieve_documents_chunks(locale=locale, uri=best_match_uri)
        metadata: Dict[str, Any] = document_results.results[0].metadata
        for idx, chunk in enumerate(chunks):
            print(f"{idx + 1}. {clean_text(chunk.content)}")
        print("\n\tMetadata:\n\t---------")
        for key, value in metadata.items():
            print(f"\t- {key}: {clean_text(value, max_length=100) if isinstance(value, str) else value}")
    print("=" * 120)
    print(f"Time: {(t1 - t0) * 1000:.2f} ms")
    print("=" * 120)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    parser.add_argument("-q", "--query", help="Query to search for.", required=True)
    parser.add_argument("-l", "--locale", help="Locale for the word index.", type=LocaleCode,
                        default=EN_US)
    parser.add_argument("-m", "--max_results", help="Maximum number of results.", type=int, required=True)
    args = parser.parse_args()
    search_document(args.query, args.locale, args.tenant, args.user, args.instance, max_results=args.max_results)
