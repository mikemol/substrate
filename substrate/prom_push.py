# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""POST Prometheus text exposition to luthen's vmagent (W49, 2026-09-23).

⚑ A TRANSPORT 200 IS NOT A VERIFICATION. vmagent accepts a name no alert entails and drops it
silently (luthen's docs), so returning normally means only that the POST was accepted.
"""

from __future__ import annotations

import http.client
from typing import TYPE_CHECKING

from substrate import vmagent_address

if TYPE_CHECKING:
    from pathlib import Path

IMPORT_PATH = "/api/v1/import/prometheus"
TIMEOUT_S = 10
HTTP_OK_MIN, HTTP_OK_MAX = 200, 300


def push(text: str, luthen: Path) -> None:
    """POST `text`; raise OSError/UnresolvedError on failure or a non-2xx status."""
    host, port = vmagent_address.address(luthen)
    conn = http.client.HTTPConnection(host, port, timeout=TIMEOUT_S)
    try:
        conn.request(
            "POST", IMPORT_PATH, body=text.encode(), headers={"Content-Type": "text/plain"}
        )
        status = conn.getresponse().status
    finally:
        conn.close()
    if not HTTP_OK_MIN <= status < HTTP_OK_MAX:
        msg = f"vmagent answered HTTP {status}"
        raise OSError(msg)
