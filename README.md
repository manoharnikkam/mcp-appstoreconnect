# mcp-appstoreconnect

A lightweight [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server for the [Apple App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi). Works with Claude Code, Claude Desktop, and any MCP-compatible client.

Two deployment modes — same codebase, same tools:

| Mode | Transport | Best for |
|------|-----------|----------|
| **Local** (`uvx`) | stdio | Solo developers, per-machine setup |
| **Shared** (Docker) | HTTP + bearer token | Teams sharing one server instance |

## Tools

| Tool | Description |
|------|-------------|
| `list_apps` | List all apps in your App Store Connect account |
| `list_builds` | List recent builds for an app |
| `get_build` | Get details for a specific build |
| `expire_build` | Expire a build so it can no longer be installed by testers |
| `list_crash_signatures` | List grouped crash signatures for a build |
| `get_crash_logs` | Get download URLs for individual crash logs |
| `list_app_store_versions` | List App Store submission versions for an app |
| `list_beta_groups` | List TestFlight beta groups for an app |
| `list_customer_reviews` | List customer reviews by territory |

## Prerequisites

1. Go to [App Store Connect → Users and Access → Integrations → App Store Connect API](https://appstoreconnect.apple.com/access/integrations/api)
2. Generate a key with **Developer** role (or higher)
3. Download the `.p8` private key — you can only download it once
4. Note your **Key ID** and **Issuer ID**

---

## Mode 1 — Local via uvx (solo developer)

No installation required. `uvx` runs the server as a subprocess, one per machine.

### Claude Code (per-project)

Add a `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "appstoreconnect": {
      "command": "uvx",
      "args": ["mcp-appstoreconnect"],
      "env": {
        "ASC_KEY_ID": "XXXXXXXXXX",
        "ASC_ISSUER_ID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        "ASC_KEY_PATH": "~/.appstoreconnect/AuthKey_XXXXXXXXXX.p8"
      }
    }
  }
}
```

> Add `.mcp.json` to `.gitignore` — it contains your personal key path.

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "appstoreconnect": {
      "command": "uvx",
      "args": ["mcp-appstoreconnect"],
      "env": {
        "ASC_KEY_ID": "XXXXXXXXXX",
        "ASC_ISSUER_ID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        "ASC_KEY_PATH": "/Users/you/.appstoreconnect/AuthKey_XXXXXXXXXX.p8"
      }
    }
  }
}
```

> Use absolute paths (not `~`) in Claude Desktop config.

---

## Mode 2 — Shared via Docker (team)

One server instance, shared by the whole team. The `.p8` key lives on the server — developers only need the URL and a bearer token.

### Start the server

```bash
# Copy and fill in your values
cp .env.example .env

# Start
docker compose up -d
```

`.env` file:

```env
ASC_KEY_ID=XXXXXXXXXX
ASC_ISSUER_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
ASC_KEY_FILE=/path/to/AuthKey_XXXXXXXXXX.p8
MCP_AUTH_TOKEN=your-secret-team-token
```

### Team member config

Each developer adds this to their `~/.claude/settings.json` (or `.mcp.json`):

```json
{
  "mcpServers": {
    "appstoreconnect": {
      "type": "http",
      "url": "http://your-server:8000/mcp",
      "headers": {
        "Authorization": "Bearer your-secret-team-token"
      }
    }
  }
}
```

No key file, no Python, no `uvx` needed on developer machines.

### Environment variables reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ASC_KEY_ID` | Yes | — | App Store Connect API Key ID |
| `ASC_ISSUER_ID` | Yes | — | Issuer ID from App Store Connect |
| `ASC_KEY_PATH` | Yes | — | Path to the `.p8` private key file |
| `MCP_TRANSPORT` | No | `stdio` | `stdio` for local, `http` for Docker/shared |
| `MCP_AUTH_TOKEN` | No | — | Bearer token required in HTTP mode (recommended) |
| `MCP_HOST` | No | `0.0.0.0` | Bind address (HTTP mode only) |
| `MCP_PORT` | No | `8000` | Port (HTTP mode only) |

---

## Development

```bash
git clone https://github.com/manoharnikkam/mcp-appstoreconnect
cd mcp-appstoreconnect
uv sync
uv run mcp-appstoreconnect           # stdio mode
MCP_TRANSPORT=http uv run mcp-appstoreconnect  # HTTP mode on :8000
```

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) for local mode, or Docker for shared mode

## License

MIT
