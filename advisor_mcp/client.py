"""httpx client for the upstream Solar Advisor agent API."""

from typing import Any

import httpx
from pydantic import BaseModel


class AdvisorConfigError(Exception):
    """SOLAR_ADVISOR_URL was not set."""


class AdvisorHttpError(Exception):
    """Upstream returned non-2xx."""

    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body[:200]}")
        self.status = status


class AdvisorNetworkError(Exception):
    """Upstream unreachable."""


class AdvisorResponse(BaseModel):
    answer: str
    intent: str | None = None
    citations: list[dict[str, Any]] = []
    payback_years: float | None = None
    governance_report: dict[str, Any] | None = None
    errors: list[dict[str, Any]] = []


async def query(*, base_url: str, question: str, timeout: float = 60.0) -> AdvisorResponse:
    if not base_url:
        raise AdvisorConfigError("SOLAR_ADVISOR_URL is not set in .env")

    url = f"{base_url.rstrip('/')}/api/v1/query"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url, json={"question": question})
    except httpx.HTTPError as e:
        raise AdvisorNetworkError(f"Request to {url} failed: {e}") from e

    if r.status_code != 200:
        raise AdvisorHttpError(r.status_code, r.text)

    return AdvisorResponse.model_validate(r.json())


async def health(*, base_url: str, timeout: float = 5.0) -> dict[str, Any]:
    if not base_url:
        raise AdvisorConfigError("SOLAR_ADVISOR_URL is not set in .env")
    url = f"{base_url.rstrip('/')}/healthz"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url)
    except httpx.HTTPError as e:
        raise AdvisorNetworkError(f"Request to {url} failed: {e}") from e
    if r.status_code != 200:
        raise AdvisorHttpError(r.status_code, r.text)
    return r.json()
