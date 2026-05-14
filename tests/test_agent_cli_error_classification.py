from __future__ import annotations

import agent_cli
import docs_agent
from agent_cli_error_classification import is_network_error_text, is_network_error_type


class TransportError(Exception):
    pass


def test_network_error_classification_matches_transport_dns_failure() -> None:
    assert is_network_error_type("TransportError") is True
    assert (
        is_network_error_text("Unable to find the server at oauth2.googleapis.com")
        is True
    )


def test_docs_agent_classify_error_marks_transport_dns_failure_retryable() -> None:
    payload = docs_agent.classify_error(
        TransportError("Unable to find the server at oauth2.googleapis.com")
    )

    assert payload["error_type"] == "TransportError"
    assert payload["retryable"] is True
    assert payload["network_related"] is True
    assert payload["auth_related"] is False


def test_agent_cli_retry_classifier_marks_transport_dns_failure_retryable() -> None:
    assert (
        agent_cli.is_retryable_network_error(
            {
                "ok": False,
                "error_type": "TransportError",
                "error_message": "Unable to find the server at oauth2.googleapis.com",
            }
        )
        is True
    )
