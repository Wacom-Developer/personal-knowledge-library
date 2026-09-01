# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Live regression test for the Wikipedia helpers.

This one really calls Wikimedia. It exists because the failure it guards against is
invisible offline: Wikimedia rejects an unidentified client with HTTP 403, and
``get_wikipedia_summary`` turns that into an empty string, so a broken integration and an
article with no summary look identical to the caller.

The offline coverage lives in ``tests/test_wikipedia_unit.py``.
"""

import pytest

from knowledge.utils.wikipedia import get_wikipedia_summary, get_wikipedia_summary_image

ARTICLE: str = "Vincent van Gogh"


@pytest.mark.parametrize("language", ["en", "de"])
def test_wikipedia_summary_is_not_empty(language: str) -> None:
    """A well-known article must come back with prose, not an empty string."""
    summary: str = get_wikipedia_summary(ARTICLE, language)

    assert summary != "", (
        f"Empty summary for '{ARTICLE}' ({language}). Wikimedia most likely refused the request; "
        f"check that knowledge/utils/wikipedia.py still sends an identifying User-Agent."
    )
    assert len(summary) > 100


def test_wikipedia_summary_image_returns_both_parts() -> None:
    """The combined helper must fill in the thumbnail as well as the text."""
    result = get_wikipedia_summary_image(ARTICLE, "en")

    assert result["summary-text"] != ""
    assert result["summary-image"].startswith("https://")
