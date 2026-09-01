# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom. All rights reserved.
from typing import Any, Dict

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from knowledge import __version__

__all__ = [
    "ExtractionException",
    "USER_AGENT",
    "get_wikipedia_summary",
    "get_wikipedia_summary_image",
    "get_wikipedia_summary_url",
]

# Wikimedia's User-Agent policy asks every client to identify itself with a tool name, a
# version and a way to make contact, and answers HTTP 403 to the default
# ``python-requests/x.y`` agent. Because the helpers below turn a failed request into an
# empty summary, an unidentified client fails silently — every article simply looks like
# it has no abstract. See https://meta.wikimedia.org/wiki/User-Agent_policy.
USER_AGENT: str = (
    f"personal-knowledge-library/{__version__} (https://github.com/Wacom-Developer/personal-knowledge-library)"
)


class ExtractionException(Exception):
    """
    Exception for extraction errors.
    """


def __wikimedia_session__(max_retries: int = 5, backoff_factor: float = 0.5) -> requests.Session:
    """A session that identifies this client to Wikimedia and retries transient failures.

    Every Wikimedia request goes through here so that no call site can forget the
    ``User-Agent`` — omitting it is answered with HTTP 403, which the callers below turn
    into an empty result rather than an error.

    Parameters
    ----------
    max_retries: int
        Maximum number of retries.
    backoff_factor: float
        A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
        second try without a delay)

    Returns
    -------
    session: requests.Session
        Configured session.
    """
    session: requests.Session = requests.Session()
    retries: Retry = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def __extract_abstract__(title: str, language: str = "en", max_retries: int = 5, backoff_factor: float = 0.5) -> str:
    """Extracting an abstract.

    Parameters
    ----------
    title: str -
        Title of wikipedia article
    language: str -
        language_code of Wikipedia

    Returns
    -------
    abstract: str
        Abstract of the wikipedia article

    Raises
    ------
    ExtractionException -
        Failed to extract abstract
    """
    params: Dict[str, str] = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",
        "exintro": "1",
        "explaintext": "1",
        "redirects": "1",
    }

    url: str = f"https://{language}.wikipedia.org/w/api.php"
    with __wikimedia_session__(max_retries, backoff_factor) as session:
        response: Response = session.get(url, params=params)
        if response.ok:
            result: Dict[str, Any] = response.json()
            if "query" in result:
                pages = result["query"]["pages"]
                if len(pages) == 1:
                    for v in pages.values():
                        return str(v.get("extract", ""))
    raise ExtractionException(f"Abstract for article with {title} in language_code {language} cannot be extracted.")


def __extract_thumb__(title: str, language: str = "en", max_retries: int = 5, backoff_factor: float = 0.5) -> str:
    """
    Extracting thumbnail from Wikipedia.

    Parameters
    ----------
    title: str
        Title of wikipedia article
    language: str
        Language code of Wikipedia
    max_retries: int
        Maximum number of retries
    backoff_factor: float
        A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
        second try without a delay)

    Returns
    -------
    url: str
        thumb URL
    """
    params: Dict[str, str] = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "pageimages",
        "pithumbsize": "400",
    }

    url: str = f"https://{language}.wikipedia.org/w/api.php"
    with __wikimedia_session__(max_retries, backoff_factor) as session:
        response: Response = session.get(url, params=params)
        if response.ok:
            result: Dict[str, Any] = response.json()
            if "query" in result:
                pages: Dict[str, Any] = result["query"]["pages"]
                if len(pages) == 1:
                    for v in pages.values():
                        if "thumbnail" in v:
                            return str(v["thumbnail"]["source"])

    raise ExtractionException(f"Thumbnail for article with {title} in language_code {language} cannot be extracted.")


def get_wikipedia_summary(title: str, lang: str = "en") -> str:
    """
    Extracting summary wikipedia URL.

    Parameters
    ----------
    title: str
        Title of the Wikipedia article
    lang: str
        Language code

    Returns
    -------
    result: Dict[str, str]
        Summary dict with image and summary text
    """
    try:
        summary: str = __extract_abstract__(title, lang)
    except ExtractionException:
        summary = ""
    return summary


def get_wikipedia_summary_image(title: str, lang: str = "en") -> Dict[str, str]:
    """
    Extracting summary image and abstract for wikipedia URL.

    Parameters
    ----------
    title: str
        Title of the Wikipedia article
    lang: str
        Language code

    Returns
    -------
    result: Dict[str, str]
        Summary dict with image and summary text
    """
    try:
        thumbnail: str = __extract_thumb__(title, lang)
    except ExtractionException:
        thumbnail = ""
    try:
        summary: str = __extract_abstract__(title, lang)
    except ExtractionException:
        summary = ""
    return {"summary-image": thumbnail, "summary-text": summary}


def get_wikipedia_summary_url(wiki_url: str, lang: str = "en") -> Dict[str, str]:
    """
    Extracting summary image and abstract for wikipedia URL.
    Parameters
    ----------
    wiki_url: str
        Wikipedia URL
    lang: str
        Language code

    Returns
    -------
    result: Dict[str, str]
        Result dictionary.
    """
    title: str = wiki_url.split("/")[-1]
    return {
        "url": wiki_url,
        "summary-image": __extract_thumb__(title, lang),
        "summary-text": __extract_abstract__(title, lang),
    }
