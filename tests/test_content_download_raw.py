"""Unit test: AsyncSession._request_content must not JSON-decode file downloads.

Regression guard for content whose stored MIME type is ``application/json``:
``download_content`` requests ``raw_content=True`` so the exact uploaded bytes
are returned instead of a re-stringified ``dict``. Pure unit test — no server.
"""

import orjson

from knowledge.services.asyncio.base import AsyncSession


class _FakeResponse:
    """Minimal stand-in for aiohttp.ClientResponse for _request_content."""

    def __init__(self, body: bytes) -> None:
        self._body = body
        self.headers = {"Content-Type": "application/json"}

    async def read(self) -> bytes:
        return self._body

    async def json(self, encoding: str = "utf-8", loads=orjson.loads):  # type: ignore[no-untyped-def]
        return loads(self._body)


async def test_raw_download_preserves_bytes() -> None:
    body = orjson.dumps({"key": "value", "n": 1})
    # raw=True: exact bytes, no deserialization (the download path).
    assert await AsyncSession._request_content(_FakeResponse(body), raw=True) == body
    # Default path still deserializes JSON API responses into a dict.
    assert await AsyncSession._request_content(_FakeResponse(body)) == {"key": "value", "n": 1}
