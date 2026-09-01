# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the Wikipedia helpers in ``knowledge/utils/wikipedia.py``.

Wikimedia answers HTTP 403 to the default ``python-requests`` User-Agent, and the helpers
swallow the resulting ``ExtractionException`` into an empty string, so the failure reaches
callers as "this article has no summary" rather than as an error. These tests pin the
identifying header on every Wikimedia request, and the empty-summary fallback that keeps
``wikidata_to_thing`` from emitting blank descriptions.

No network — ``requests.Session.get`` is replaced by a recorder.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pytest
import requests

from knowledge import __version__
from knowledge.base.entity import Description, Label
from knowledge.base.language import DE_DE, EN_US, LocaleCode
from knowledge.ontomapping import MappingConfiguration
from knowledge.ontomapping.manager import wikidata_to_thing
from knowledge.public.wikidata import SiteLinks, WikidataThing
from knowledge.utils.wikipedia import (
    get_wikipedia_summary,
    get_wikipedia_summary_image,
    get_wikipedia_summary_url,
)

ARTICLE: str = "Vincent van Gogh"
ABSTRACT: str = "Vincent Willem van Gogh was a Dutch Post-Impressionist painter."
THUMBNAIL: str = "https://upload.wikimedia.org/wikipedia/commons/thumb/vg.jpg"
DEFAULT_REQUESTS_AGENT: str = "python-requests"


class _FakeResponse:
    """Minimal stand-in for ``requests.Response`` covering what the helpers read."""

    def __init__(self, payload: Dict[str, Any], ok: bool = True) -> None:
        self.ok: bool = ok
        self.__payload: Dict[str, Any] = payload

    def json(self) -> Dict[str, Any]:
        """Decoded body."""
        return self.__payload


def _payload() -> Dict[str, Any]:
    """A ``query`` response carrying both an extract and a thumbnail."""
    return {
        "query": {
            "pages": {
                "3021": {
                    "extract": ABSTRACT,
                    "thumbnail": {"source": THUMBNAIL},
                }
            }
        }
    }


def _record_requests(monkeypatch: pytest.MonkeyPatch, ok: bool = True) -> List[Dict[str, str]]:
    """Replace ``requests.Session.get`` with a recorder and return the captured headers.

    The recorded headers are the *effective* ones — the session defaults merged with any
    per-call override — so the test does not care which of the two the fix uses.
    """
    captured: List[Dict[str, str]] = []

    def _get(session: requests.Session, url: str, **kwargs: Any) -> _FakeResponse:
        effective: Dict[str, str] = {str(k): str(v) for k, v in dict(session.headers).items()}
        effective.update(kwargs.get("headers") or {})
        captured.append(effective)
        return _FakeResponse(_payload(), ok=ok)

    monkeypatch.setattr(requests.Session, "get", _get)
    return captured


def _user_agents(captured: List[Dict[str, str]]) -> List[str]:
    """The User-Agent of every recorded request, matched case-insensitively."""
    agents: List[str] = []
    for headers in captured:
        for name, value in headers.items():
            if name.lower() == "user-agent":
                agents.append(value)
                break
        else:
            agents.append("")
    return agents


# ------------------------------------------ User-Agent on every request -----------------------------------------------
def test_summary_request_identifies_the_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """``get_wikipedia_summary`` must not go out as the default ``python-requests`` agent.

    Wikimedia returns 403 for that agent, which the helper turns into an empty summary.
    """
    captured: List[Dict[str, str]] = _record_requests(monkeypatch)

    get_wikipedia_summary(ARTICLE, "en")

    assert len(captured) == 1
    agent: str = _user_agents(captured)[0]
    assert agent != ""
    assert not agent.startswith(DEFAULT_REQUESTS_AGENT)


def test_user_agent_carries_tool_version_and_contact(monkeypatch: pytest.MonkeyPatch) -> None:
    """Wikimedia's policy asks for a tool name, a version and a way to make contact."""
    captured: List[Dict[str, str]] = _record_requests(monkeypatch)

    get_wikipedia_summary(ARTICLE, "en")

    agent: str = _user_agents(captured)[0]
    assert "personal-knowledge-library" in agent
    assert __version__ in agent
    assert "https://github.com/Wacom-Developer/personal-knowledge-library" in agent


def test_summary_image_requests_identify_the_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Both requests behind ``get_wikipedia_summary_image`` carry the agent."""
    captured: List[Dict[str, str]] = _record_requests(monkeypatch)

    result: Dict[str, str] = get_wikipedia_summary_image(ARTICLE, "en")

    assert result == {"summary-image": THUMBNAIL, "summary-text": ABSTRACT}
    assert len(captured) == 2
    for agent in _user_agents(captured):
        assert not agent.startswith(DEFAULT_REQUESTS_AGENT)
        assert "personal-knowledge-library" in agent


def test_summary_url_requests_identify_the_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Both requests behind ``get_wikipedia_summary_url`` carry the agent."""
    captured: List[Dict[str, str]] = _record_requests(monkeypatch)

    result: Dict[str, str] = get_wikipedia_summary_url(f"https://en.wikipedia.org/wiki/{ARTICLE}", "en")

    assert result["summary-text"] == ABSTRACT
    assert len(captured) == 2
    for agent in _user_agents(captured):
        assert not agent.startswith(DEFAULT_REQUESTS_AGENT)
        assert "personal-knowledge-library" in agent


def test_rejected_request_still_yields_an_empty_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    """A refused request keeps the documented contract: an empty string, never a raise."""
    _record_requests(monkeypatch, ok=False)

    assert get_wikipedia_summary(ARTICLE, "en") == ""


# --------------------------------------- Blank summaries must not win -------------------------------------------------
def _van_gogh() -> WikidataThing:
    """A Wikidata entity with descriptions and an English/German Wikipedia sitelink."""
    thing: WikidataThing = WikidataThing(
        revision="1",
        qid="Q5582",
        modified=datetime(2026, 1, 1),
        label={
            "en_US": Label("Vincent van Gogh", EN_US, main=True),
            "de_DE": Label("Vincent van Gogh", DE_DE, main=True),
        },
        description={
            "en_US": Description("Dutch painter (1853-1890)", EN_US),
            "de_DE": Description("niederländischer Maler (1853-1890)", DE_DE),
        },
    )
    thing.sitelinks["wiki"] = SiteLinks(
        source="wiki",
        titles={"en": ARTICLE, "de": ARTICLE},
        urls={"en": f"https://en.wikipedia.org/wiki/{ARTICLE}"},
    )
    return thing


def test_blank_wikipedia_summary_falls_back_to_the_wikidata_descriptions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An empty summary is 'nothing pulled', not 'a description that happens to be empty'.

    ``wikidata_to_thing`` only consults the Wikidata descriptions when its Wikipedia list
    is empty. Blank summaries filled that list, so entities came back holding nothing but
    empty strings — strictly worse than never asking for Wikipedia at all.
    """
    monkeypatch.setattr("knowledge.ontomapping.mapping_configuration", MappingConfiguration())
    monkeypatch.setattr("knowledge.ontomapping.manager.get_wikipedia_summary", lambda title, lang: "")
    entity: WikidataThing = _van_gogh()

    thing, _ = wikidata_to_thing(
        entity,
        all_relations={},
        supported_locales=[EN_US, DE_DE],
        all_wikidata_objects={entity.qid: entity},
        pull_wikipedia=True,
        guess_concept_type=False,
    )

    contents: Dict[str, Optional[str]] = {str(d.language_code): d.content for d in thing.description}
    assert contents == {
        str(EN_US): "Dutch painter (1853-1890)",
        str(DE_DE): "niederländischer Maler (1853-1890)",
    }


def test_real_wikipedia_summary_is_preferred_over_the_wikidata_description(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The fallback must not fire when Wikipedia actually answered."""
    monkeypatch.setattr("knowledge.ontomapping.mapping_configuration", MappingConfiguration())
    monkeypatch.setattr("knowledge.ontomapping.manager.get_wikipedia_summary", lambda title, lang: ABSTRACT)
    entity: WikidataThing = _van_gogh()

    thing, _ = wikidata_to_thing(
        entity,
        all_relations={},
        supported_locales=[EN_US, DE_DE],
        all_wikidata_objects={entity.qid: entity},
        pull_wikipedia=True,
        guess_concept_type=False,
    )

    assert [d.content for d in thing.description] == [ABSTRACT, ABSTRACT]
    assert {str(d.language_code) for d in thing.description} == {str(EN_US), str(DE_DE)}


def test_whitespace_only_summary_counts_as_blank(monkeypatch: pytest.MonkeyPatch) -> None:
    """A summary of nothing but whitespace is no more useful than an empty one.

    It would otherwise satisfy the "did Wikipedia answer?" check and suppress the
    Wikidata fallback just as the empty string did.
    """
    monkeypatch.setattr("knowledge.ontomapping.mapping_configuration", MappingConfiguration())
    monkeypatch.setattr("knowledge.ontomapping.manager.get_wikipedia_summary", lambda title, lang: "   \n ")
    entity: WikidataThing = _van_gogh()

    thing, _ = wikidata_to_thing(
        entity,
        all_relations={},
        supported_locales=[EN_US, DE_DE],
        all_wikidata_objects={entity.qid: entity},
        pull_wikipedia=True,
        guess_concept_type=False,
    )

    contents: Dict[str, Optional[str]] = {str(d.language_code): d.content for d in thing.description}
    assert contents == {
        str(EN_US): "Dutch painter (1853-1890)",
        str(DE_DE): "niederländischer Maler (1853-1890)",
    }


def test_locale_codes_are_preserved_on_the_fallback_descriptions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The fallback must keep locale codes, not the bare language codes of the sitelinks."""
    monkeypatch.setattr("knowledge.ontomapping.mapping_configuration", MappingConfiguration())
    monkeypatch.setattr("knowledge.ontomapping.manager.get_wikipedia_summary", lambda title, lang: "")
    entity: WikidataThing = _van_gogh()

    thing, _ = wikidata_to_thing(
        entity,
        all_relations={},
        supported_locales=[EN_US, DE_DE],
        all_wikidata_objects={entity.qid: entity},
        pull_wikipedia=True,
        guess_concept_type=False,
    )

    locales: List[LocaleCode] = [d.language_code for d in thing.description]
    assert sorted(str(locale) for locale in locales) == sorted([str(DE_DE), str(EN_US)])
