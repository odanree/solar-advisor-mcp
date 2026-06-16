# solar-advisor-mcp

MCP server wrapping the [solar-advisor-agent](https://github.com/odanree/solar-advisor-agent)
deployment at `solar-advisor.danhle.net`. Exposes two tools to any MCP client
(Claude Desktop, Claude Code, custom LangGraph clients):

- `solar_advisor_query(question)` — natural-language solar-economics query.
  Returns the agent's answer, classified intent, citations, optional payback
  years, and any governance flags / source-error envelope.
- `solar_advisor_health()` — quick reachability probe of the upstream agent.

## Why

The Solar Advisor is the operator's composite-data LangGraph agent (Solar Cost
Explorer GraphQL + NREL PVWatts + DSIRE + EIA). Without this MCP wrapper,
calling it from Claude Code or Desktop requires hand-crafted `curl`. With it,
the model drives the agent like any other tool.

Pairs with [oci-mcp](https://github.com/odanree/oci-mcp), [infra-mcp](https://github.com/odanree/infra-mcp),
[beacon-mcp](https://github.com/odanree/beacon-mcp), and
[clinical-mcp-server](https://github.com/odanree/clinical-mcp-server) in the
operator's MCP-server portfolio. This is the second of the "MCP wraps a
self-built agent" pattern (the first being oci-mcp).

## Setup

```bash
cp .env.example .env
# set SOLAR_ADVISOR_URL=https://solar-advisor.danhle.net
pip install -e ".[dev]"
pytest -q
```

Register with Claude Code:

```bash
claude mcp add solar-advisor python -m advisor_mcp.server
```

## Smoke test

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"solar_advisor_query","arguments":{"question":"Is solar worth it in California for a 6 kW system?"}}}' | python -m advisor_mcp.server
```

## License

MIT
