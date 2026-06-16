"""Server-level tests: exercise the MCP tool functions directly and verify
the envelope shape (ok/error_kind/message)."""

import httpx
import pytest
import respx

from advisor_mcp.server import solar_advisor_health, solar_advisor_query


@respx.mock
async def test_query_returns_ok_envelope(monkeypatch):
    monkeypatch.setenv("SOLAR_ADVISOR_URL", "https://example.test")
    respx.post("https://example.test/api/v1/query").mock(
        return_value=httpx.Response(
            200,
            json={"answer": "ok", "intent": "cost_lookup", "citations": [], "errors": []},
        )
    )
    result = await solar_advisor_query(question="any")
    assert result["ok"] is True
    assert result["data"]["intent"] == "cost_lookup"


async def test_query_returns_config_error_when_url_missing(monkeypatch):
    monkeypatch.delenv("SOLAR_ADVISOR_URL", raising=False)
    result = await solar_advisor_query(question="any")
    assert result["ok"] is False
    assert result["error_kind"] == "config"


@respx.mock
async def test_query_returns_http_error_envelope(monkeypatch):
    monkeypatch.setenv("SOLAR_ADVISOR_URL", "https://example.test")
    respx.post("https://example.test/api/v1/query").mock(
        return_value=httpx.Response(500, text="bad")
    )
    result = await solar_advisor_query(question="any")
    assert result["ok"] is False
    assert result["error_kind"] == "http"


@respx.mock
async def test_health_returns_ok_envelope(monkeypatch):
    monkeypatch.setenv("SOLAR_ADVISOR_URL", "https://example.test")
    respx.get("https://example.test/healthz").mock(
        return_value=httpx.Response(200, json={"status": "ok"})
    )
    result = await solar_advisor_health()
    assert result["ok"] is True
    assert result["data"]["status"] == "ok"
