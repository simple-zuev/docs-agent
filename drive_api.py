from __future__ import annotations

from pathlib import Path
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


def get_readonly_services() -> dict[str, Any]:
    try:
        s = docs_agent.services()
        return _ok(
            "get-readonly-services",
            services_available=sorted(list(s.keys())),
            has_drive="drive" in s,
            has_docs="docs" in s,
            has_sheets="sheets" in s,
        ) | {"services": s}
    except Exception as exc:
        error_type, retryable, auth_related, network_related = docs_agent.classify_error(exc)
        return _error(
            "get-readonly-services",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
        )


def get_drive_service() -> dict[str, Any]:
    payload = get_readonly_services()
    if not payload.get("ok"):
        return payload
    return _ok("get-drive-service", service=payload["services"]["drive"])


def get_docs_service() -> dict[str, Any]:
    payload = get_readonly_services()
    if not payload.get("ok"):
        return payload
    return _ok("get-docs-service", service=payload["services"]["docs"])


def get_sheets_service() -> dict[str, Any]:
    payload = get_readonly_services()
    if not payload.get("ok"):
        return payload
    return _ok("get-sheets-service", service=payload["services"]["sheets"])


def get_file_meta_readonly(file_id: str) -> dict[str, Any]:
    drive_payload = get_drive_service()
    if not drive_payload.get("ok"):
        return drive_payload

    try:
        meta = docs_agent.get_file_meta(drive_payload["service"], file_id)
        return _ok("get-file-meta-readonly", file_id=file_id, meta=meta)
    except Exception as exc:
        error_type, retryable, auth_related, network_related = docs_agent.classify_error(exc)
        return _error(
            "get-file-meta-readonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={"file_id": file_id},
        )


def list_children_readonly(folder_id: str, page_size: int = 1000) -> dict[str, Any]:
    drive_payload = get_drive_service()
    if not drive_payload.get("ok"):
        return drive_payload

    try:
        items = docs_agent.list_children(drive_payload["service"], folder_id, page_size=page_size)
        return _ok(
            "list-children-readonly",
            folder_id=folder_id,
            page_size=page_size,
            items=items,
            count=len(items),
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = docs_agent.classify_error(exc)
        return _error(
            "list-children-readonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={"folder_id": folder_id, "page_size": page_size},
        )


def find_folder_readonly(name: str, parent_id: str | None = None) -> dict[str, Any]:
    drive_payload = get_drive_service()
    if not drive_payload.get("ok"):
        return drive_payload

    try:
        folder = docs_agent.find_folder(drive_payload["service"], name, parent_id=parent_id)
        return _ok(
            "find-folder-readonly",
            folder_name=name,
            parent_id=parent_id,
            folder=folder,
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = docs_agent.classify_error(exc)
        return _error(
            "find-folder-readonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={"folder_name": name, "parent_id": parent_id},
        )


def get_sheet_values_readonly(spreadsheet_id: str, range_a1: str) -> dict[str, Any]:
    sheets_payload = get_sheets_service()
    if not sheets_payload.get("ok"):
        return sheets_payload

    try:
        values = docs_agent.get_sheet_values(sheets_payload["service"], spreadsheet_id, range_a1)
        return _ok(
            "get-sheet-values-readonly",
            spreadsheet_id=spreadsheet_id,
            range_a1=range_a1,
            values=values,
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = docs_agent.classify_error(exc)
        return _error(
            "get-sheet-values-readonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={"spreadsheet_id": spreadsheet_id, "range_a1": range_a1},
        )


def get_sheet_rows_readonly(spreadsheet_id: str, sheet_name: str) -> dict[str, Any]:
    sheets_payload = get_sheets_service()
    if not sheets_payload.get("ok"):
        return sheets_payload

    try:
        rows = docs_agent.get_sheet_rows(sheets_payload["service"], spreadsheet_id, sheet_name)
        return _ok(
            "get-sheet-rows-readonly",
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            rows=rows,
            row_count=len(rows),
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = docs_agent.classify_error(exc)
        return _error(
            "get-sheet-rows-readonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={"spreadsheet_id": spreadsheet_id, "sheet_name": sheet_name},
        )


def get_sheet_header_map_readonly(
    spreadsheet_id: str,
    sheet_name: str,
    header_row: int = 1,
) -> dict[str, Any]:
    sheets_payload = get_sheets_service()
    if not sheets_payload.get("ok"):
        return sheets_payload

    try:
        header, mapping = docs_agent.get_sheet_header_map(
            sheets_payload["service"],
            spreadsheet_id,
            sheet_name,
            header_row=header_row,
        )
        return _ok(
            "get-sheet-header-map-readonly",
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            header_row=header_row,
            header=header,
            mapping=mapping,
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = docs_agent.classify_error(exc)
        return _error(
            "get-sheet-header-map-readonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={
                "spreadsheet_id": spreadsheet_id,
                "sheet_name": sheet_name,
                "header_row": header_row,
            },
        )
