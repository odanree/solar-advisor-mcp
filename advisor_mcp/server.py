"""FastMCP server exposing the Solar Advisor agent as MCP tools."""

import os
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic_settings import BaseSettings, SettingsConfigDict

from advisor_mcp.client import (
    AdvisorConfigError,
    AdvisorHttpError,
    AdvisorNetworkError,
    health,
    query,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    solar_advisor_url: str = ""


def _ok(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": data}


def _err(kind: str, message: str) -> dict[str, Any]:
    return {"ok": False, "error_kind": kind, "message": message}


mcp = FastMCP("solar-advisor")


@mcp.tool()
async def solar_advisor_query(question: str) -> dict[str, Any]:
    """Ask the Solar Advisor agent a natural-language question about solar economics.

    The agent classifies intent (cost_lookup or payback_estimate), pulls from
    Solar Cost Explorer GraphQL, NREL PVWatts, DSIRE, and EIA as needed, then
    returns a structured answer with citations and (when applicable) an
    estimated payback period in years.

    Returns {ok: True, data: {...}} on success, or {ok: False, error_kind, message}
    on failure. error_kind is one of: config, network, http.
    """
    settings = Settings()
    try:
        result = await query(base_url=settings.solar_advisor_url, question=question)
        return _ok(result.model_dump())
    except AdvisorConfigError as e:
        return _err("config", str(e))
    except AdvisorNetworkError as e:
        return _err("network", str(e))
    except AdvisorHttpError as e:
        return _err("http", str(e))


@mcp.tool()
async def solar_advisor_health() -> dict[str, Any]:
    """Quick reachability probe of the upstream agent."""
    settings = Settings()
    try:
        return _ok(await health(base_url=settings.solar_advisor_url))
    except AdvisorConfigError as e:
        return _err("config", str(e))
    except AdvisorNetworkError as e:
        return _err("network", str(e))
    except AdvisorHttpError as e:
        return _err("http", str(e))


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
