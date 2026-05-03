"""App Store Connect MCP Server."""

import os
from typing import Any

import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .auth import ASCAuth
from .client import ASCClient

mcp = FastMCP("App Store Connect")

_client: ASCClient | None = None


def _get_client() -> ASCClient:
    global _client
    if _client is None:
        key_id = os.environ["ASC_KEY_ID"]
        issuer_id = os.environ["ASC_ISSUER_ID"]
        key_path = os.environ["ASC_KEY_PATH"]
        _client = ASCClient(ASCAuth(key_id, issuer_id, key_path))
    return _client


def _pluck(data: list[dict[str, Any]], *fields: str) -> list[dict[str, Any]]:
    """Return only the requested top-level attribute keys from each record."""
    out = []
    for item in data:
        row: dict[str, Any] = {"id": item.get("id")}
        attrs = item.get("attributes", {})
        for f in fields:
            if f in attrs:
                row[f] = attrs[f]
        out.append(row)
    return out


# ---------------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_apps(limit: int = 25) -> list[dict[str, Any]]:
    """List all apps in App Store Connect."""
    data = await _get_client().get("/apps", {"limit": str(limit)})
    return _pluck(data["data"], "name", "bundleId", "primaryLocale", "isOrEverWasMadeForKids")


# ---------------------------------------------------------------------------
# Builds
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_builds(app_id: str, limit: int = 25) -> list[dict[str, Any]]:
    """List recent builds for an app."""
    data = await _get_client().get(
        "/builds",
        {"filter[app]": app_id, "limit": str(limit), "sort": "-uploadedDate"},
    )
    return _pluck(data["data"], "version", "uploadedDate", "processingState", "usesNonExemptEncryption")


@mcp.tool()
async def get_builds_by_number(app_id: str, build_number: str, limit: int = 200) -> list[dict[str, Any]]:
    """Get builds for an app by build number/version."""
    data = await _get_client().get(
        "/builds",
        {
            "filter[app]": app_id,
            "filter[version]": str(build_number),
            "limit": str(limit),
            "sort": "-uploadedDate",
        },
    )
    return _pluck(data["data"], "version", "uploadedDate", "processingState", "usesNonExemptEncryption")


@mcp.tool()
async def get_build(build_id: str) -> dict[str, Any]:
    """Get details for a specific build."""
    data = await _get_client().get(f"/builds/{build_id}")
    item = data["data"]
    return {"id": item["id"], **item.get("attributes", {})}


@mcp.tool()
async def expire_build(build_id: str) -> dict[str, Any]:
    """Expire a build so it can no longer be installed by testers."""
    body = {
        "data": {
            "type": "builds",
            "id": build_id,
            "attributes": {"expired": True},
        }
    }
    data = await _get_client().patch(f"/builds/{build_id}", body)
    item = data["data"]
    return {"id": item["id"], **item.get("attributes", {})}


# ---------------------------------------------------------------------------
# Crash logs / diagnostics
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_crash_signatures(build_id: str, limit: int = 20) -> list[dict[str, Any]]:
    """List crash signatures (grouped crash reports) for a build."""
    data = await _get_client().get(
        f"/builds/{build_id}/diagnosticSignatures",
        {"limit": str(limit)},
    )
    return _pluck(data["data"], "crashType", "signature", "weight")


@mcp.tool()
async def get_crash_logs(signature_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """Get individual crash log URLs for a diagnostic signature."""
    data = await _get_client().get(
        f"/diagnosticSignatures/{signature_id}/logs",
        {"limit": str(limit)},
    )
    return _pluck(data["data"], "downloadUrl", "timestamp")


# ---------------------------------------------------------------------------
# App Store Versions
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_app_store_versions(app_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """List App Store versions (submissions) for an app."""
    data = await _get_client().get(
        f"/apps/{app_id}/appStoreVersions",
        {"limit": str(limit)},
    )
    return _pluck(
        data["data"],
        "versionString",
        "appStoreState",
        "releaseType",
        "createdDate",
    )


# ---------------------------------------------------------------------------
# Beta testing
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_beta_groups(app_id: str) -> list[dict[str, Any]]:
    """List TestFlight beta groups for an app."""
    data = await _get_client().get(f"/apps/{app_id}/betaGroups")
    return _pluck(data["data"], "name", "isInternalGroup", "hasAccessToAllBuilds", "publicLinkEnabled")


# ---------------------------------------------------------------------------
# Customer reviews
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_customer_reviews(
    app_id: str,
    territory: str = "USA",
    limit: int = 25,
) -> list[dict[str, Any]]:
    """List customer reviews for an app in a given App Store territory."""
    data = await _get_client().get(
        f"/apps/{app_id}/customerReviews",
        {
            "limit": str(limit),
            "filter[territory]": territory,
            "sort": "-createdDate",
        },
    )
    return _pluck(data["data"], "title", "body", "rating", "createdDate", "reviewerNickname")


class _BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Response:
        token = os.environ.get("MCP_AUTH_TOKEN")
        if token:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {token}":
                return Response("Unauthorized", status_code=401)
        return await call_next(request)


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")

    if transport == "http":
        host = os.environ.get("MCP_HOST", "0.0.0.0")
        port = int(os.environ.get("MCP_PORT", "8000"))
        app = mcp.streamable_http_app()
        app.add_middleware(_BearerAuthMiddleware)
        uvicorn.run(app, host=host, port=port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
