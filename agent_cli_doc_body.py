from __future__ import annotations

from collections.abc import Callable

from agent_cli_output import build_error_payload


def assemble_context_payload(
    profile: str,
    *,
    capabilities_payload: Callable[[], dict],
    status_payload: Callable[[], dict],
    find_doc_any_payload_from_cache: Callable[[str], dict],
) -> dict:
    if profile != "exchange-docs":
        return build_error_payload(
            command="assemble-context",
            error_type="UnsupportedProfile",
            error_message=f"Unsupported context profile: {profile}",
            retryable=False,
            auth_related=False,
            network_related=False,
            profile=profile,
        )

    capabilities = capabilities_payload()
    status_payload_result = status_payload()

    source_groups = {
        "core_baseline_documents": [
            "КБ ТЗ v2",
            "КБ Архитектура v2",
        ],
        "stakeholder_flows": [
            "Клиент ФЛ JTBD и CJM",
            "Клиент ЮРЛ JTBD и CJM",
            "Партнер JTBD и CJM",
            "Админ JTBD и CJM",
            "Комплаенс JTBD и CJM",
            "Регулятор JTBD и CJM",
            "Поддержка JTBD и CJM",
        ],
        "repository_governance_and_operator_context": [
            "DOC-0001",
            "Change Log Lite",
            "status",
            "capabilities",
        ],
        "working_drafts_and_review_artifacts": [
            "13_Черновики_и_review",
        ],
    }

    resolved_sources = []
    unresolved_sources = []

    for group_name, items in source_groups.items():
        for item in items:
            if item == "DOC-0001":
                payload = find_doc_any_payload_from_cache("DOC-0001")
                if payload.get("ok"):
                    resolved_sources.append(
                        {
                            "group": group_name,
                            "query": item,
                            "matched_by": payload.get("matched_by"),
                            "summary": payload.get("summary"),
                        }
                    )
                else:
                    unresolved_sources.append(
                        {
                            "group": group_name,
                            "query": item,
                            "reason": "CacheMiss",
                            "error_message": "DOC-0001 was not available through current cache-only lookup.",
                        }
                    )
                continue

            if item in {"status", "capabilities"}:
                resolved_sources.append(
                    {
                        "group": group_name,
                        "query": item,
                        "matched_by": "built-in",
                        "summary": {"name": item},
                    }
                )
                continue

            if item == "Change Log Lite":
                resolved_sources.append(
                    {
                        "group": group_name,
                        "query": item,
                        "matched_by": "config",
                        "summary": {
                            "name": "Change Log Lite",
                            "spreadsheet_id": (
                                (status_payload_result.get("config") or {}).get(
                                    "change_log_spreadsheet_id"
                                )
                            ),
                            "sheet_name": (
                                (status_payload_result.get("config") or {}).get(
                                    "change_log_sheet_name"
                                )
                            ),
                        },
                    }
                )
                continue

            if item == "13_Черновики_и_review":
                resolved_sources.append(
                    {
                        "group": group_name,
                        "query": item,
                        "matched_by": "known-folder",
                        "summary": {"name": "13_Черновики_и_review"},
                    }
                )
                continue

            payload = find_doc_any_payload_from_cache(item)
            if payload.get("ok"):
                resolved_sources.append(
                    {
                        "group": group_name,
                        "query": item,
                        "matched_by": payload.get("matched_by"),
                        "summary": payload.get("summary"),
                    }
                )
            else:
                unresolved_sources.append(
                    {
                        "group": group_name,
                        "query": item,
                        "reason": "CacheMiss",
                        "error_message": "Source was not available through current cache-only lookup.",
                    }
                )

    recommended_generation_mode = (
        "draft-doc" if len(unresolved_sources) == 0 else "doc-body-only"
    )

    return {
        "ok": True,
        "command": "assemble-context",
        "profile": profile,
        "source_groups": source_groups,
        "resolved_sources": resolved_sources,
        "unresolved_sources": unresolved_sources,
        "capabilities_snapshot": capabilities,
        "safety_snapshot": status_payload_result,
        "context_summary": {
            "resolved_count": len(resolved_sources),
            "unresolved_count": len(unresolved_sources),
            "partial_context": len(unresolved_sources) > 0,
        },
        "recommended_generation_mode": recommended_generation_mode,
        "next_safe_step": (
            "Use draft-doc when all critical sources are resolved; otherwise prefer doc-body-only and avoid direct mutation."
        ),
    }


def doc_body_only_outline(document_type: str) -> list[str]:
    outlines = {
        "operating-model": [
            "Назначение",
            "Область применения",
            "Роли и ответственность",
            "Основные процессы",
            "Контрольные точки",
            "Ограничения и риски",
            "Следующие шаги",
        ],
        "instruction": [
            "Назначение инструкции",
            "Область применения",
            "Предварительные условия",
            "Порядок действий",
            "Контрольные проверки",
            "Ограничения",
            "Следующие шаги",
        ],
        "policy": [
            "Цель policy",
            "Область действия",
            "Обязательные правила",
            "Запрещённые действия",
            "Контроль соблюдения",
            "Исключения",
            "Следующие шаги",
        ],
        "architecture-note": [
            "Контекст",
            "Проблема",
            "Принятое решение",
            "Альтернативы",
            "Ограничения",
            "Риски",
            "Следующие шаги",
        ],
        "draft-spec": [
            "Назначение",
            "Контекст",
            "Функциональные требования",
            "Нефункциональные требования",
            "Ограничения",
            "Риски и допущения",
            "Следующие шаги",
        ],
    }
    return outlines.get(
        document_type,
        [
            "Назначение",
            "Контекст",
            "Основное содержание",
            "Ограничения",
            "Риски и допущения",
            "Следующие шаги",
        ],
    )


def build_doc_body_only_body(
    *,
    profile: str,
    document_type: str,
    title: str,
    context_payload: dict,
) -> str:
    outline = doc_body_only_outline(document_type)
    summary = context_payload.get("context_summary") or {}
    partial = bool(summary.get("partial_context"))
    resolved_count = int(summary.get("resolved_count") or 0)
    unresolved_count = int(summary.get("unresolved_count") or 0)

    lines = [
        f"# {title}",
        "",
        f"Профиль контекста: {profile}",
        f"Тип документа: {document_type}",
        "",
        "## Контекст подготовки",
        f"- resolved sources: {resolved_count}",
        f"- unresolved sources: {unresolved_count}",
        f"- partial context: {'yes' if partial else 'no'}",
        "",
        "## Важно",
        "Документ подготовлен в режиме doc-body-only.",
        "Это означает, что сформировано безопасное структурированное содержимое без автоматической записи в целевой артефакт.",
        "",
    ]

    if partial:
        lines.extend(
            [
                "## Ограничения текущего контекста",
                "- Не все источники были разрешены через текущий read-only lookup path.",
                "- Содержимое ниже является безопасным черновым телом документа и требует последующей валидации.",
                "",
            ]
        )

    for section in outline:
        lines.extend(
            [
                f"## {section}",
                f"[Черновое содержимое для раздела '{section}'. Заполнить и уточнить по материалам профиля {profile}.]",
                "",
            ]
        )

    lines.extend(
        [
            "## Допущения",
            "- Использован только подтверждённый и частично разрешённый контекст текущего agent workflow.",
            "- При появлении дополнительных canonical sources документ должен быть уточнён.",
            "",
            "## Следующий безопасный шаг",
            "Создать или выбрать draft document в review-контуре и перенести это тело документа в controlled write workflow.",
            "",
        ]
    )

    return "\n".join(lines)


def doc_body_only_payload(
    profile: str,
    document_type: str,
    title: str,
    *,
    assemble_context_payload: Callable[[str], dict],
) -> dict:
    context_payload = assemble_context_payload(profile)
    if not context_payload.get("ok"):
        return context_payload

    outline = doc_body_only_outline(document_type)
    body = build_doc_body_only_body(
        profile=profile,
        document_type=document_type,
        title=title,
        context_payload=context_payload,
    )

    unresolved_dependencies = [
        item.get("query")
        for item in (context_payload.get("unresolved_sources") or [])
        if item.get("query")
    ]

    assumptions = [
        "Body is generated without direct mutation.",
        "Body may be based on partial context when unresolved sources exist.",
        "Further review is required before canonical or review-draft update.",
    ]

    return {
        "ok": True,
        "command": "doc-body-only",
        "profile": profile,
        "document_type": document_type,
        "title": title,
        "context_snapshot": {
            "resolved_count": (context_payload.get("context_summary") or {}).get(
                "resolved_count"
            ),
            "unresolved_count": (context_payload.get("context_summary") or {}).get(
                "unresolved_count"
            ),
            "partial_context": (context_payload.get("context_summary") or {}).get(
                "partial_context"
            ),
        },
        "outline": outline,
        "body": body,
        "assumptions": assumptions,
        "unresolved_dependencies": unresolved_dependencies,
        "next_safe_step": "Create or select a draft document in review scope and use controlled write workflow to place this body.",
    }
