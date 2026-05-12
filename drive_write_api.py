from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import docs_agent


def _ok(command: str, **extra) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": True, "command": command}
    payload.update(extra)
    return payload


def _error(
    command: str,
    error_type: str,
    error_message: str,
    *,
    retryable: bool = False,
    auth_related: bool = False,
    network_related: bool = False,
    details: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": False,
        "command": command,
        "error_type": error_type,
        "error_message": error_message,
        "retryable": retryable,
        "auth_related": auth_related,
        "network_related": network_related,
    }
    if details:
        payload["details"] = details
    return payload


def get_write_services() -> dict[str, Any]:
    try:
        services = docs_agent.services()
        return _ok(
            "get-write-services",
            services_available=sorted(list(services.keys())),
            has_drive="drive" in services,
            has_docs="docs" in services,
            has_sheets="sheets" in services,
        ) | {"services": services}
    except Exception as exc:
        error_type, retryable, auth_related, network_related = (
            docs_agent.classify_error(exc)
        )
        return _error(
            "get-write-services",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
        )


def append_change_log_entry(
    *,
    action: str,
    obj: str,
    from_: str,
    to: str,
    reason: str,
    impact: str = "Low",
    status: str = "Done",
    notes: str = "",
) -> dict[str, Any]:
    services_payload = get_write_services()
    if not services_payload.get("ok"):
        return services_payload

    try:
        sheets = services_payload["services"]["sheets"]
        now = datetime.now()
        change_id = f"CHG-{now.strftime('%Y-%m-%d-%H%M%S')}-LOCAL"
        row = [
            change_id,
            now.strftime("%Y-%m-%d"),
            action,
            obj,
            from_,
            to,
            reason,
            impact,
            status,
            notes,
        ]
        result = (
            sheets.spreadsheets()
            .values()
            .append(
                spreadsheetId=docs_agent.CHANGE_LOG_ID,
                range="'Change Log Lite'!A:J",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [row]},
            )
            .execute()
        )
        updated_range = result.get("updates", {}).get("updatedRange")
        return _ok(
            "append-change-log-entry",
            action=action,
            object_name=obj,
            from_=from_,
            to=to,
            reason=reason,
            impact=impact,
            status=status,
            notes=notes,
            change_id=change_id,
            updated_range=updated_range,
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = (
            docs_agent.classify_error(exc)
        )
        return _error(
            "append-change-log-entry",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={
                "action": action,
                "object_name": obj,
                "from_": from_,
                "to": to,
                "reason": reason,
                "impact": impact,
                "status": status,
            },
        )
