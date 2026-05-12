from __future__ import annotations

from typing import Any


def replace_all_text(
    *,
    docs: Any,
    document_id: str,
    old_text: str,
    new_text: str,
    match_case: bool = True,
) -> dict[str, Any]:
    response = (
        docs.documents()
        .batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "replaceAllText": {
                            "containsText": {
                                "text": old_text,
                                "matchCase": match_case,
                            },
                            "replaceText": new_text,
                        }
                    }
                ]
            },
        )
        .execute()
    )

    replies = response.get("replies", [])
    occurrences_changed = 0
    if replies and isinstance(replies[0], dict):
        occurrences_changed = int(
            replies[0].get("replaceAllText", {}).get("occurrencesChanged", 0) or 0
        )

    return {
        "ok": True,
        "command": "replace-all-text",
        "document_id": document_id,
        "old_text": old_text,
        "new_text": new_text,
        "match_case": match_case,
        "occurrences_changed": occurrences_changed,
        "raw_response": response,
    }
