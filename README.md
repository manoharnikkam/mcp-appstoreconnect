# mcp-appstoreconnect

A lightweight [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server for the [Apple App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi). Works with Claude Code, Claude Desktop, and any MCP-compatible client.

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

## Setup

### 1. Create an App Store Connect API key

1. Go to [App Store Connect → Users and Access → Integrations → App Store Connect API](https://appstoreconnect.apple.com/access/integrations/api)
2. Generate a key with **Developer** role (or higher)
3. Download the `.p8` private key file — you can only download it once
4. Note your **Key ID** and **Issuer ID**

### 2. Configure environment variables

```bash
export ASC_KEY_ID="XXXXXXXXXX"
export ASC_ISSUER_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export ASC_KEY_PATH="~/.appstoreconnect/AuthKey_XXXXXXXXXX.p8"
```

### 3. Add to Claude Code (global)

Add to `~/.claude/settings.json`:

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

### 4. Add to Claude Desktop

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

> **Note:** Use absolute paths (not `~`) in Claude Desktop config.

## Running locally (development)

```bash
git clone https://github.com/manoharnikkam/mcp-appstoreconnect
cd mcp-appstoreconnect
uv sync
uv run mcp-appstoreconnect
```

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) (recommended) or pip

## License

MIT
