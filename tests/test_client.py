import httpx
import pytest
import respx

from advisor_mcp.client import (
    AdvisorConfigError,
    AdvisorHttpError,
    AdvisorNetworkError,
    health,
    query,
)


@respx.mock
async def test_query_success():
    respx.post("https://example.test/api/v1/query").mock(
        return_value=httpx.Response(
            200,
            json={
                "answer": "Sample answer.",
                "intent": "cost_lookup",
                "citations": [{"source": "solar_cost_explorer", "detail": "..."}],
                "errors": [],
            },
        )
    )
    r = await query(base_url="https://example.test", question="median ca $/W?")
    assert r.intent == "cost_lookup"
    assert r.answer == "Sample answer."


async def test_query_requires_url():
    with pytest.raises(AdvisorConfigError):
        await query(base_url="", question="x")


@respx.mock
async def test_query_http_error_maps():
    respx.post("https://example.test/api/v1/query").mock(
        return_value=httpx.Response(503, text="upstream down")
    )
    with pytest.raises(AdvisorHttpError) as exc:
        await query(base_url="https://example.test", question="x")
    assert exc.value.status == 503


@respx.mock
async def test_query_network_error_maps():
    respx.post("https://example.test/api/v1/query").mock(side_effect=httpx.ConnectError("boom"))
    with pytest.raises(AdvisorNetworkError):
        await query(base_url="https://example.test", question="x")


@respx.mock
async def test_health_success():
    respx.get("https://example.test/healthz").mock(
        return_value=httpx.Response(200, json={"status": "ok"})
    )
    h = await health(base_url="https://example.test")
    assert h["status"] == "ok"
