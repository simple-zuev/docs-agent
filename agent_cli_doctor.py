from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

from agent_cli_lookup import payload_contains_quota_or_rate_limit
from agent_cli_output import build_error_payload
from agent_cli_subprocess import (
    BASE,
    DOCS_AGENT,
    DOCS_AGENT_TIMEOUT_SEC,
    PYTHON_BIN,
    PYTHON_BIN_SOURCE,
)


def summarize_payload_ok(payload: dict | None) -> bool:
    return isinstance(payload, dict) and bool(payload.get("ok"))


def safe_error_type(payload: dict | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    return payload.get("error_type")


def safe_error_message(payload: dict | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    return payload.get("error_message")


def build_doctor_summary(
    *, env_ok: bool, status_ok: bool, master_index_ok: bool, smoke_ok: bool
) -> str:
    if env_ok and status_ok and master_index_ok and smoke_ok:
        return "CLI выглядит работоспособным: окружение, status, доступ к MASTER_INDEX и smoke-проверка прошли успешно."
    failed = []
    if not env_ok:
        failed.append("окружение")
    if not status_ok:
        failed.append("status")
    if not master_index_ok:
        failed.append("MASTER_INDEX")
    if not smoke_ok:
        failed.append("smoke")
    failed_text = ", ".join(failed)
    return f"Обнаружены проблемы в следующих зонах: {failed_text}."


def diagnose_payload_failure(payload: dict | None) -> tuple[str, str, str]:
    if not isinstance(payload, dict):
        return (
            "unknown",
            "Не удалось интерпретировать результат проверки.",
            "Повтори команду и проверь целостность CLI-вывода.",
        )

    if payload_contains_quota_or_rate_limit(payload):
        return (
            "network",
            "Похоже на временную внешнюю проблему или превышение квоты Google API.",
            "Подожди 60-90 секунд, сократи quota-sensitive запросы и повтори doctor/smoke.",
        )

    error_type = str(payload.get("error_type") or "")
    error_message = str(payload.get("error_message") or "")
    auth_related = bool(payload.get("auth_related"))
    network_related = bool(payload.get("network_related"))
    retryable = bool(payload.get("retryable"))

    attempts = payload.get("attempts") or []
    nested_messages = []
    nested_types = []
    if isinstance(attempts, list):
        for item in attempts:
            if isinstance(item, dict):
                et = str(item.get("error_type") or "")
                em = str(item.get("error_message") or "")
                if et:
                    nested_types.append(et)
                if em:
                    nested_messages.append(em)

    joined_text = " | ".join(
        [error_type, error_message] + nested_types + nested_messages
    ).lower()

    if auth_related:
        return (
            "auth",
            "Похоже на проблему авторизации или доступа к Google/API.",
            "Проверь учетные данные, токены, scopes и доступ к целевым объектам.",
        )

    if (
        network_related
        or retryable
        or "ssl" in joined_text
        or "eof occurred in violation of protocol" in joined_text
    ):
        return (
            "network",
            "Похоже на временную сетевую проблему или нестабильность внешнего API.",
            "Подожди и повтори проверку; если повторяется, проверь сеть и лимиты API.",
        )

    if error_type in {"NotFound", "LinkParseError"}:
        return (
            "not_found",
            "Похоже, CLI не смог найти документ или корректно извлечь идентификатор из ссылки.",
            "Проверь точный query/Document ID/ссылку и сначала выполни find-doc-any.",
        )

    if error_type in {
        "EmptyOutput",
        "JSONDecodeError",
        "TimeoutExpired",
        "SmokeCheckFailed",
    }:
        return (
            "internal",
            "Похоже на внутренний сбой CLI или дочернего docs_agent.py.",
            "Проверь debug-вывод, timeout, stdout/stderr и отдельно запусти status/doctor --json.",
        )

    return (
        "internal",
        "Похоже на внутренний сбой без точной классификации.",
        "Проверь debug-вывод и повтори диагностику через doctor --json.",
    )


def build_doctor_next_step(
    *, env_ok: bool, status_ok: bool, master_index_ok: bool, smoke_ok: bool
) -> str:
    if not env_ok:
        return "Проверь активацию venv и доступность python/agent_cli.py."
    if not status_ok:
        return "Сначала выполни python agent_cli.py status --json и проверь блоки safety/config."
    if not master_index_ok:
        return (
            "Проверь доступность MASTER_INDEX и повтори python agent_cli.py f DOC-0001."
        )
    if not smoke_ok:
        return "Запусти bash scripts/regression_smoke_quiet.sh отдельно и проверь, какой шаг падает."
    return "Можно начинать штатную работу."


def _environment_payload() -> dict:
    return {
        "ok": bool(Path(PYTHON_BIN).exists() and DOCS_AGENT.exists() and BASE.exists()),
        "details": {
            "python_bin": str(PYTHON_BIN),
            "python_bin_source": PYTHON_BIN_SOURCE,
            "docs_agent_path": str(DOCS_AGENT),
            "base_path": str(BASE),
            "python_exists": Path(PYTHON_BIN).exists(),
            "docs_agent_exists": DOCS_AGENT.exists(),
            "base_exists": BASE.exists(),
        },
    }


def doctor_payload(
    *,
    status_payload: Callable[[], dict],
    find_doc_any_payload: Callable[[str], dict],
) -> dict:
    env = _environment_payload()

    status = status_payload()
    master_index_lookup = find_doc_any_payload("DOC-0001")
    smoke_probe = run_smoke_explain_payload()

    checks = {
        "environment": env,
        "status": status,
        "master_index_lookup": master_index_lookup,
        "smoke_probe": smoke_probe,
    }

    failed = [k for k, v in checks.items() if not v.get("ok")]

    if not failed:
        return {
            "ok": True,
            "command": "doctor",
            "checks": checks,
            "summary": "CLI выглядит работоспособным: окружение, status, доступ к MASTER_INDEX и smoke-проверка прошли успешно.",
            "next_step": "Можно начинать штатную работу.",
            "diagnosis": "healthy",
            "likely_cause": "Проблем не обнаружено.",
            "recommended_action": "Можно начинать штатную работу.",
        }

    sample = checks[failed[0]]

    diagnosis = str(sample.get("diagnosis") or "internal")
    likely_cause = str(
        sample.get("likely_cause")
        or "Похоже на внутренний сбой CLI или дочернего docs_agent.py."
    )
    recommended_action = str(
        sample.get("recommended_action")
        or "Проверь debug-вывод и отдельно запусти doctor --json."
    )
    error_type = str(sample.get("error_type") or "DoctorCheckFailed")
    error_message = str(sample.get("error_message") or "doctor check failed")

    return {
        "ok": False,
        "command": "doctor",
        "checks": checks,
        "summary": f"Обнаружены проблемы в следующих зонах: {', '.join(failed)}.",
        "next_step": "Проверь diagnosis / likely_cause / recommended_action или запусти bash scripts/regression_smoke_explain.sh.",
        "diagnosis": diagnosis,
        "likely_cause": likely_cause,
        "recommended_action": recommended_action,
        "error_type": error_type,
        "error_message": error_message,
        "retryable": bool(sample.get("retryable")),
        "auth_related": bool(sample.get("auth_related")),
        "network_related": bool(sample.get("network_related")),
    }


def doctor_lite_payload(
    *,
    status_payload: Callable[[], dict],
    find_doc_any_payload: Callable[[str], dict],
) -> dict:
    env = _environment_payload()

    status = status_payload()
    master_index_lookup = find_doc_any_payload("DOC-0001")

    checks = {
        "environment": env,
        "status": status,
        "master_index_lookup": master_index_lookup,
    }

    failed = [k for k, v in checks.items() if not v.get("ok")]

    if not failed:
        return {
            "ok": True,
            "command": "doctor-lite",
            "checks": checks,
            "summary": "CLI выглядит работоспособным для рутинного старта: окружение, status и доступ к MASTER_INDEX проверены.",
            "next_step": "Можно начинать штатную работу. Для углубленной проверки при необходимости запусти doctor.",
            "diagnosis": "healthy",
            "likely_cause": "Проблем не обнаружено.",
            "recommended_action": "Можно начинать штатную работу.",
        }

    sample = checks[failed[0]]
    diagnosis = "internal"
    likely_cause = "Похоже на внутренний сбой CLI или дочернего docs_agent.py."
    recommended_action = "Проверь debug-вывод и отдельно запусти doctor --json."

    if sample.get("auth_related"):
        diagnosis = "auth"
        likely_cause = (
            "Похоже на проблему доступа, авторизации или прав к внешним сервисам."
        )
        recommended_action = "Проверь credentials, доступы и авторизацию."
    elif sample.get("network_related") or sample.get("retryable"):
        diagnosis = "network"
        likely_cause = "Похоже на временную сетевую проблему или квоту внешнего API."
        recommended_action = "Подожди 60-90 секунд и повтори doctor-lite/doctor."
    elif str(sample.get("error_type") or "") in {"NotFound", "LinkParseError"}:
        diagnosis = "not_found"
        likely_cause = "Похоже, обязательный объект не найден."
        recommended_action = "Проверь MASTER_INDEX и доступность ожидаемых объектов."

    return {
        "ok": False,
        "command": "doctor-lite",
        "checks": checks,
        "summary": f"Обнаружены проблемы в следующих зонах: {', '.join(failed)}.",
        "next_step": "Запусти doctor --json для расширенной диагностики.",
        "diagnosis": diagnosis,
        "likely_cause": likely_cause,
        "recommended_action": recommended_action,
        "error_type": str(sample.get("error_type") or "DoctorLiteCheckFailed"),
        "error_message": str(sample.get("error_message") or "doctor-lite check failed"),
        "retryable": bool(sample.get("retryable")),
        "auth_related": bool(sample.get("auth_related")),
        "network_related": bool(sample.get("network_related")),
    }


def run_smoke_explain_payload() -> dict:
    script = BASE / "scripts" / "regression_smoke_explain.sh"
    if not script.exists():
        return build_error_payload(
            command="smoke-explain",
            error_type="ScriptNotFound",
            error_message="scripts/regression_smoke_explain.sh not found.",
            retryable=False,
            auth_related=False,
            network_related=False,
        )

    cmd = ["bash", str(script)]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=DOCS_AGENT_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return build_error_payload(
            command="smoke-explain",
            error_type="TimeoutExpired",
            error_message=f"regression_smoke_explain.sh timed out after {DOCS_AGENT_TIMEOUT_SEC} seconds.",
            retryable=True,
            auth_related=False,
            network_related=True,
        )
    except Exception as exc:
        return build_error_payload(
            command="smoke-explain",
            error_type=exc.__class__.__name__,
            error_message=f"Failed to run regression_smoke_explain.sh: {exc}",
            retryable=False,
            auth_related=False,
            network_related=False,
        )

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    blob = f"{stdout}\n{stderr}".lower()

    diagnosis = "healthy"
    likely_cause = "Проблем не обнаружено."
    recommended_action = "Можно продолжать работу."

    if proc.returncode != 0:
        diagnosis = "internal"
        likely_cause = "Похоже на внутренний сбой smoke-проверки."
        recommended_action = "Запусти bash scripts/regression_smoke_explain.sh отдельно и проверь первый failing step."

        if (
            "quota" in blob
            or "429" in blob
            or "rate limit" in blob
            or "rate_limit" in blob
        ):
            diagnosis = "network"
            likely_cause = (
                "Похоже на временную внешнюю проблему или превышение квоты API."
            )
            recommended_action = "Подожди 60-90 секунд и повтори doctor/smoke."
        elif (
            "auth" in blob
            or "forbidden" in blob
            or "permission" in blob
            or "unauthorized" in blob
        ):
            diagnosis = "auth"
            likely_cause = (
                "Похоже на проблему доступа или авторизации к внешним сервисам."
            )
            recommended_action = "Проверь credentials, токены и права доступа."

    payload = {
        "ok": proc.returncode == 0,
        "command": "smoke-explain",
        "returncode": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "diagnosis": diagnosis,
        "likely_cause": likely_cause,
        "recommended_action": recommended_action,
        "_debug": {
            "cmd": cmd,
            "timeout_sec": DOCS_AGENT_TIMEOUT_SEC,
        },
    }

    if proc.returncode != 0:
        payload.update(
            {
                "error_type": "SmokeCheckFailed",
                "error_message": "regression_smoke_explain.sh returned non-zero exit code.",
                "retryable": diagnosis == "network",
                "auth_related": diagnosis == "auth",
                "network_related": diagnosis == "network",
            }
        )

    return payload
