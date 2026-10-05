"""Environment settings with the same bounded defaults as the previous API."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
# Use the platform DNS resolver. The bundled c-ares resolver can stall gRPC
# on local networks even when Google's HTTPS endpoints are reachable.
os.environ.setdefault("GRPC_DNS_RESOLVER", "native")


def number(name: str, default: float, minimum: float, maximum: float) -> float:
    try:
        value = float(os.getenv(name, ""))
        return value if minimum <= value <= maximum else default
    except ValueError:
        return default


def integer(name: str, default: int, minimum: int, maximum: int) -> int:
    return int(number(name, default, minimum, maximum) + 0.5)


def enabled(name: str, default: bool = True) -> bool:
    value = os.getenv(name, "")
    return value.lower() in {"1", "true", "yes", "on"} if value else default


def names(name: str, default: list[str]) -> list[str]:
    return (
        list(dict.fromkeys(v.strip() for v in os.getenv(name, "").split(",") if v.strip()))
        or default
    )
