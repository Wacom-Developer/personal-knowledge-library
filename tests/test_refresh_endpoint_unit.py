"""Unit tests for the refresh endpoint derivation. No network access."""

import pytest

from knowledge.services.asyncio.graph import AsyncWacomKnowledgeService
from knowledge.services.asyncio.search import AsyncSemanticSearchClient
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ink import InkServices
from knowledge.services.ontology import OntologyService
from knowledge.services.search import SemanticSearchClient

INSTANCE = "https://stage-private-knowledge.wacom.com"
EXPECTED = f"{INSTANCE}/graph/v1/user/refresh"

FACTORIES = [
    pytest.param(lambda: WacomKnowledgeService(service_url=INSTANCE), id="sync-graph"),
    pytest.param(lambda: SemanticSearchClient(service_url=INSTANCE), id="sync-search"),
    pytest.param(lambda: OntologyService(service_url=INSTANCE), id="sync-ontology"),
    pytest.param(lambda: InkServices(service_url=INSTANCE), id="sync-ink"),
    pytest.param(lambda: AsyncWacomKnowledgeService(service_url=INSTANCE, application_name="test"), id="async-graph"),
    pytest.param(lambda: AsyncSemanticSearchClient(service_url=INSTANCE), id="async-search"),
]


@pytest.mark.parametrize("factory", FACTORIES)
def test_refresh_endpoint_is_graph_scoped_for_every_client(factory):
    assert factory().refresh_endpoint == EXPECTED


def test_refresh_endpoint_honours_base_auth_url():
    client = WacomKnowledgeService(service_url=INSTANCE, base_auth_url="https://auth.example.com")
    assert client.refresh_endpoint == "https://auth.example.com/graph/v1/user/refresh"


def test_refresh_endpoint_does_not_repeat_the_service_endpoint():
    assert "graph/v1/graph/v1" not in SemanticSearchClient(service_url=INSTANCE).refresh_endpoint
