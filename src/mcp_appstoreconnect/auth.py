import time
from pathlib import Path

import jwt


class ASCAuth:
    """Manages App Store Connect API JWT tokens with automatic refresh."""

    def __init__(self, key_id: str, issuer_id: str, key_path: str) -> None:
        self.key_id = key_id
        self.issuer_id = issuer_id
        self.key_path = Path(key_path).expanduser()
        self._token: str | None = None
        self._token_exp: float = 0

    def get_token(self) -> str:
        now = time.time()
        if self._token and self._token_exp - now > 60:
            return self._token

        private_key = self.key_path.read_text()
        exp = int(now) + 1200  # ASC max is 20 minutes

        self._token = jwt.encode(
            {
                "iss": self.issuer_id,
                "iat": int(now),
                "exp": exp,
                "aud": "appstoreconnect-v1",
            },
            private_key,
            algorithm="ES256",
            headers={"kid": self.key_id},
        )
        self._token_exp = exp
        return self._token
