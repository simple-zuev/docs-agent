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


def create_staging_copy_writeonly(
    *,
    file_id: str,
    target_folder: str = "13_Черновики_и_review",
) -> dict[str, Any]:
    services_payload = get_write_services()
    if not services_payload.get("ok"):
        return services_payload

    try:
        drive = services_payload["services"]["drive"]

        cass = docs_agent.find_folder(drive, "Cass")
        target = docs_agent.find_folder(drive, target_folder, cass["id"])
        source = docs_agent.get_file_meta(drive, file_id)

        copy_name = f"STAGING_COPY__{source['name']}__{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        copied = (
            drive.files()
            .copy(
                fileId=file_id,
                body={
                    "name": copy_name,
                    "parents": [target["id"]],
                },
                fields="id,name,webViewLink,parents",
                supportsAllDrives=True,
            )
            .execute()
        )

        log_payload = append_change_log_entry(
            action="Copy",
            obj=copy_name,
            from_=source.get("webViewLink", file_id),
            to=f"Cass / {target_folder}",
            reason="Создание staging-копии для безопасного редактирования без изменения canonical-документа",
            impact="Low",
            status="Done",
            notes=f"Source: {source['name']} | Copy URL: {copied.get('webViewLink')}",
        )
        if not log_payload.get("ok"):
            return log_payload

        return _ok(
            "create-staging-copy-writeonly",
            file_id=file_id,
            target_folder=target_folder,
            source=source,
            copied=copied,
            copy_name=copy_name,
            change_log=log_payload,
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = (
            docs_agent.classify_error(exc)
        )
        return _error(
            "create-staging-copy-writeonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={
                "file_id": file_id,
                "target_folder": target_folder,
            },
        )


def create_doc_in_folder_writeonly(
    *,
    target_folder: str,
    title_prefix: str = "ASTCV_DOCS_AGENT_OFFICE_TEST",
) -> dict[str, Any]:
    services_payload = get_write_services()
    if not services_payload.get("ok"):
        return services_payload

    try:
        drive = services_payload["services"]["drive"]
        docs = services_payload["services"]["docs"]

        cass = docs_agent.find_folder(drive, "Cass")
        target = docs_agent.find_folder(drive, target_folder, cass["id"])
        title = f"{title_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        created = (
            drive.files()
            .create(
                body={
                    "name": title,
                    "mimeType": "application/vnd.google-apps.document",
                    "parents": [target["id"]],
                },
                fields="id,name,webViewLink,parents",
                supportsAllDrives=True,
            )
            .execute()
        )

        docs.documents().batchUpdate(
            documentId=created["id"],
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": (
                                "Тестовый документ ASTCV Docs Agent.\n"
                                f"Папка: Cass / {target_folder}.\n"
                                "Назначение: проверка создания файлов в выбранной папке Cass.\n"
                                "Canonical-документы не изменялись.\n"
                            ),
                        }
                    }
                ]
            },
        ).execute()

        log_payload = append_change_log_entry(
            action="Create",
            obj=title,
            from_="Local docs-agent",
            to=f"Cass / {target_folder}",
            reason="Проверка создания документа в выбранной папке Cass через controlled write helper",
            impact="Low",
            status="Done",
            notes=f"URL: {created.get('webViewLink')}",
        )
        if not log_payload.get("ok"):
            return log_payload

        return _ok(
            "create-doc-in-folder-writeonly",
            target_folder=target_folder,
            title_prefix=title_prefix,
            created=created,
            title=title,
            change_log=log_payload,
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = (
            docs_agent.classify_error(exc)
        )
        return _error(
            "create-doc-in-folder-writeonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={
                "target_folder": target_folder,
                "title_prefix": title_prefix,
            },
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
