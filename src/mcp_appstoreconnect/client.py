from typing import Any

import httpx

from .auth import ASCAuth

BASE = "https://api.appstoreconnect.apple.com/v1"


class ASCClient:
    def __init__(self, auth: ASCAuth) -> None:
        self.auth = auth

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.auth.get_token()}"}

    async def get(self, path: str, params: dict[str, str] | None = None) -> Any:
        async with httpx.AsyncClient() as http:
            r = await http.get(
                f"{BASE}{path}",
                params=params or {},
                headers=self._headers(),
                timeout=30,
            )
            r.raise_for_status()
            return r.json()

    async def patch(self, path: str, body: dict[str, Any]) -> Any:
        async with httpx.AsyncClient() as http:
            r = await http.patch(
                f"{BASE}{path}",
                json=body,
                headers={**self._headers(), "Content-Type": "application/json"},
                timeout=30,
            )
            r.raise_for_status()
            return r.json()

    async def post(self, path: str, body: dict[str, Any]) -> Any:
        async with httpx.AsyncClient() as http:
            r = await http.post(
                f"{BASE}{path}",
                json=body,
                headers={**self._headers(), "Content-Type": "application/json"},
                timeout=30,
            )
            r.raise_for_status()
            return r.json()
