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


def read_doc_readonly(document_id: str, max_chars: int = 4000) -> dict[str, Any]:
    services_payload = get_readonly_services()
    if not services_payload.get("ok"):
        return services_payload

    try:
        docs = services_payload["services"]["docs"]
        drive = services_payload["services"]["drive"]

        meta = drive.files().get(
            fileId=document_id,
            fields="id,name,mimeType,webViewLink,modifiedTime",
            supportsAllDrives=True,
        ).execute()

        doc = docs.documents().get(documentId=document_id).execute()
        content = doc.get("body", {}).get("content", [])
        text_content = docs_agent.extract_text(content)

        truncated = False
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars] + "\n\n...[TRUNCATED]..."
            truncated = True

        return _ok(
            "read-doc-readonly",
            document_id=document_id,
            meta=meta,
            content=text_content,
            truncated=truncated,
            max_chars=max_chars,
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = docs_agent.classify_error(exc)
        return _error(
            "read-doc-readonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={"document_id": document_id, "max_chars": max_chars},
        )


def get_file_readonly(file_id: str) -> dict[str, Any]:
    drive_payload = get_drive_service()
    if not drive_payload.get("ok"):
        return drive_payload

    try:
        file_meta = docs_agent.get_file_meta(drive_payload["service"], file_id)
        return _ok(
            "get-file-readonly",
            file_id=file_id,
            file=file_meta,
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = docs_agent.classify_error(exc)
        return _error(
            "get-file-readonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={"file_id": file_id},
        )


def list_folder_by_id_readonly(folder_id: str) -> dict[str, Any]:
    drive_payload = get_drive_service()
    if not drive_payload.get("ok"):
        return drive_payload

    try:
        meta = drive_payload["service"].files().get(
            fileId=folder_id,
            fields="id,name,mimeType,webViewLink,modifiedTime,parents",
            supportsAllDrives=True,
        ).execute()

        items = docs_agent.list_children(drive_payload["service"], folder_id)

        return _ok(
            "list-folder-by-id-readonly",
            folder_id=folder_id,
            folder=meta,
            items=items,
            count=len(items),
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = docs_agent.classify_error(exc)
        return _error(
            "list-folder-by-id-readonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={"folder_id": folder_id},
        )


def read_sheet_header_readonly(
    spreadsheet_id: str,
    sheet_name: str,
    header_row: int = 1,
) -> dict[str, Any]:
    header_payload = get_sheet_header_map_readonly(
        spreadsheet_id=spreadsheet_id,
        sheet_name=sheet_name,
        header_row=header_row,
    )
    if not header_payload.get("ok"):
        return header_payload

    header = header_payload["header"]
    mapping = header_payload["mapping"]

    header_cells = []
    for i, value in enumerate(header, start=1):
        header_cells.append(
            {
                "index": i,
                "column_a1": docs_agent.col_to_a1(i),
                "value": value,
            }
        )

    return _ok(
        "read-sheet-header-readonly",
        spreadsheet_id=spreadsheet_id,
        sheet_name=sheet_name,
        header_row=header_row,
        header=header,
        mapping=mapping,
        header_cells=header_cells,
    )


def find_row_by_column_readonly(
    spreadsheet_id: str,
    sheet_name: str,
    column_name: str,
    match_value: str,
    header_row: int = 1,
) -> dict[str, Any]:
    sheets_payload = get_sheets_service()
    if not sheets_payload.get("ok"):
        return sheets_payload

    try:
        rows = docs_agent.get_sheet_rows(sheets_payload["service"], spreadsheet_id, sheet_name)
        _, mapping = docs_agent.get_sheet_header_map(
            sheets_payload["service"],
            spreadsheet_id,
            sheet_name,
            header_row=header_row,
        )

        matches = docs_agent.find_rows_by_column(
            rows=rows,
            header_map=mapping,
            column_name=column_name,
            match_value=match_value,
            header_row=header_row,
        )

        return _ok(
            "find-row-by-column-readonly",
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            column_name=column_name,
            match_value=match_value,
            header_row=header_row,
            matches_found=len(matches),
            matches=matches,
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = docs_agent.classify_error(exc)
        return _error(
            "find-row-by-column-readonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={
                "spreadsheet_id": spreadsheet_id,
                "sheet_name": sheet_name,
                "column_name": column_name,
                "match_value": match_value,
                "header_row": header_row,
            },
        )


def find_row_by_link_fragment_readonly(
    spreadsheet_id: str,
    sheet_name: str,
    fragment: str,
    link_column: str = "Link",
    header_row: int = 1,
) -> dict[str, Any]:
    sheets_payload = get_sheets_service()
    if not sheets_payload.get("ok"):
        return sheets_payload

    try:
        rows = docs_agent.get_sheet_rows(sheets_payload["service"], spreadsheet_id, sheet_name)
        _, mapping = docs_agent.get_sheet_header_map(
            sheets_payload["service"],
            spreadsheet_id,
            sheet_name,
            header_row=header_row,
        )

        matches = docs_agent.find_rows_by_link_fragment(
            rows=rows,
            header_map=mapping,
            fragment=fragment,
            link_column=link_column,
            header_row=header_row,
        )

        return _ok(
            "find-row-by-link-fragment-readonly",
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            fragment=fragment,
            link_column=link_column,
            header_row=header_row,
            matches_found=len(matches),
            matches=matches,
        )
    except Exception as exc:
        error_type, retryable, auth_related, network_related = docs_agent.classify_error(exc)
        return _error(
            "find-row-by-link-fragment-readonly",
            error_type,
            str(exc),
            retryable=retryable,
            auth_related=auth_related,
            network_related=network_related,
            details={
                "spreadsheet_id": spreadsheet_id,
                "sheet_name": sheet_name,
                "fragment": fragment,
                "link_column": link_column,
                "header_row": header_row,
            },
        )
