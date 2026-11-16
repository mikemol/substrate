# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Where substrate's postgres tenants live, asked of the owner rather than carried as a port.

⚑⚑⚑ THE OLD ADDRESS WAS A CONSTANT, AND THE THING IT NAMED WAS RETIRED UNDER IT. `store.py`
defaults to `127.0.0.1:30432` (live) and reaches the sandbox on libpq's default port. On
2026-09-22 both refused connections: luthen-observability had retired its loopback NodePorts on
an operator disclosure ruling, and nothing on the host listens on either port. A carried port
cannot notice its target moving; it only fails, and the failure reads as "store down".

⚑⚑ SO THE ADDRESS IS ASKED OF THE PARTY THAT OWNS IT, through `substrate.luthen_resolver` (W319:
the one caller of luthen's resolver; this module is a thin adapter over it for the `postgres`
service). It REFUSES on anything but an answer, never falling back to loopback, which is the
resolver's own rule and the one the old default broke.

⚑⚑ THE CREDENTIAL IS READ, NEVER RECORDED. Each tenant's credentials live in the k8s Secret
`pg-tenant-<tenant>` (namespace `buildbuddy`), which luthen provisions and may rotate. The
returned source is a CALLABLE read at connect time, the shape `store.py`'s keyring source and
`sandbox_target.target(source=...)` already take, so a rotation is followed rather than cached,
and no value ever sits in a module global, a message, or a file.

⚑ TENANTS, per the operator's ruling (2026-09-22): `substrate` and `substrate_sandbox`, matching
the live/sandbox split. The old store is gone; these start empty and are rebuilt from the cores.
"""

from __future__ import annotations

import base64
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import luthen_resolver as lr
from substrate import vmagent_address

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

#: The repository that owns the address, and the resolver inside it.
LUTHEN: Path = lr.DEFAULT_LUTHEN
RESOLVER: Path = LUTHEN / "checks" / "endpoints_query.py"
INTERPRETER: Path = LUTHEN / ".venv" / "bin" / "python"

#: The name luthen's resolver answers the store under.
SERVICE = "postgres"

#: The two tenants the operator ruled (2026-09-22).
LIVE = "substrate"
SANDBOX = "substrate_sandbox"

#: Where luthen provisions a tenant's credentials: the k8s object `<prefix><tenant>`.
NAMESPACE = "buildbuddy"
OBJECT_PREFIX = "pg-tenant-"
K3S = "/usr/bin/k3s"
#: The data key a connection needs from that object. Checked against the object, not assumed.
DATA_KEY = "password"

_TIMEOUT_S = 60


class EndpointError(RuntimeError):
    """The owner could not be asked, or did not answer. Never a reason to guess an address."""


class NoAnswerError(EndpointError, lr.NoAnswerError):
    """luthen's resolver exited non-zero or returned a state other than answered."""

    def __init__(self, code: int, state: object, reply: str = "") -> None:
        """Name the exit code and the state, and say the address will not be guessed."""
        lr.NoAnswerError.__init__(self, SERVICE, code, state, reply)


class UnusableAnswerError(EndpointError, lr.UnusableAnswerError):
    """The resolver answered, but without a usable host and port."""


class UnreadableObjectError(EndpointError):
    """The tenant's k8s object could not be read."""

    def __init__(self, tenant: str, code: int) -> None:
        """Name the object and the exit code."""
        super().__init__(f"could not read {object_name(tenant)} (exit {code})")


class MissingKeyError(EndpointError):
    """The tenant's k8s object has no such data key; the keys it does carry are named."""

    def __init__(self, tenant: str, key: str, keys: list[str]) -> None:
        """Name the missing key and list the present key NAMES (never a value)."""
        super().__init__(f"{object_name(tenant)} has no {key!r}; it carries {keys}")


@dataclass(frozen=True, slots=True)
class Endpoint:
    """The store's address as its owner declares it today."""

    host: str
    port: int
    as_of: str


def run(argv: list[str]) -> tuple[int, str]:
    """Run one command and return `(exit code, stdout)`; a launch failure is exit -1."""
    return vmagent_address.run(argv, _TIMEOUT_S)


def resolve_argv() -> list[str]:
    """Return the resolver invocation, by absolute path so no cwd is assumed."""
    return lr.argv(SERVICE, LUTHEN)


def record_of(text: str) -> dict[str, object]:
    """Return `text` as a JSON object, whole or as its first object LINE, or an empty record."""
    return lr.record_of(text)


def resolve(runner: Callable[[list[str]], tuple[int, str]] = run) -> Endpoint:
    """Ask luthen's resolver where the store is. Refuse on anything but an answer."""
    try:
        got = lr.resolve(SERVICE, runner, LUTHEN)
    except lr.NoAnswerError as exc:
        raise NoAnswerError(exc.code, exc.state, exc.reply) from exc
    except lr.UnusableAnswerError as exc:
        raise UnusableAnswerError(exc.record) from exc
    return Endpoint(host=got.host, port=got.port, as_of=got.as_of)


def object_name(tenant: str) -> str:
    """Return the k8s object name for a tenant: `_` becomes `-`, which k8s names cannot carry.

    ⚑ The ROLE and DATABASE keep the underscore (`substrate_sandbox`); only the object differs
    (`pg-tenant-substrate-sandbox`), per luthen's provisioning (2026-09-22). Spelling the object
    from the tenant verbatim asked for a name that cannot exist.
    """
    return f"{OBJECT_PREFIX}{tenant.replace('_', '-')}"


def object_argv(tenant: str) -> list[str]:
    """Return the k8s read for one tenant's object (needs the k3s group, hence `sg`)."""
    return [
        "sg",
        "k3s",
        "-c",
        f"{K3S} kubectl -n {NAMESPACE} get secret {object_name(tenant)} -o json",
    ]


def _data(tenant: str, runner: Callable[[list[str]], tuple[int, str]]) -> dict[str, object]:
    """Return the object's `data` mapping, or refuse naming the object."""
    code, out = runner(object_argv(tenant))
    data = record_of(out).get("data")
    if code != 0 or not isinstance(data, dict):
        raise UnreadableObjectError(tenant, code)
    return {str(k): v for k, v in data.items()}


def data_keys(tenant: str, runner: Callable[[list[str]], tuple[int, str]] = run) -> list[str]:
    """Return the KEY NAMES the tenant's object carries, never a value.

    ⚑ So the key a caller asks for is checked against the object rather than assumed; luthen
    names the keys, and a guessed key reads as "no credential".
    """
    return sorted(_data(tenant, runner))


def credential(
    tenant: str,
    key: str = DATA_KEY,
    runner: Callable[[list[str]], tuple[int, str]] = run,
) -> Callable[[], str | None]:
    """Return a source that reads `key` from the tenant's object each time it is CALLED.

    ⚑ Lazy on purpose: the object is read at connect time, so a rotation is followed and
    importing this module touches no cluster.
    """

    def read() -> str | None:
        data = _data(tenant, runner)
        raw = data.get(key)
        if not isinstance(raw, str):
            raise MissingKeyError(tenant, key, sorted(data))
        return base64.b64decode(raw).decode("utf-8")

    return read


def main(argv: list[str]) -> int:
    """Print the resolved endpoint and, per tenant named, its data key NAMES (never values)."""
    try:
        ep = resolve()
        sys.stdout.write(f"{SERVICE}: {ep.host}:{ep.port}  (as of {ep.as_of or '?'})\n")
        for tenant in argv[1:]:
            sys.stdout.write(f"  {tenant}: keys {data_keys(tenant)}\n")
    except EndpointError as exc:
        sys.stdout.write(f"store-endpoint: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
