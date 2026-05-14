from __future__ import annotations


NETWORK_ERROR_TYPES = {
    "ConnectionResetError",
    "ServerNotFoundError",
    "SSLEOFError",
    "TimeoutError",
    "TransportError",
}

NETWORK_ERROR_TEXT_MARKERS = [
    "could not resolve host",
    "eof occurred in violation of protocol",
    "failed to establish a new connection",
    "name or service not known",
    "network is unreachable",
    "nodename nor servname provided",
    "ssl",
    "temporary failure in name resolution",
    "timeout",
    "unable to find the server",
]


def is_network_error_type(value: str | None) -> bool:
    return str(value or "") in NETWORK_ERROR_TYPES


def is_network_error_text(value: str | None) -> bool:
    text = str(value or "").lower()
    return any(marker in text for marker in NETWORK_ERROR_TEXT_MARKERS)
