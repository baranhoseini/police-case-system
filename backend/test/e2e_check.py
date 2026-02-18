import os
import sys
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, List

import requests

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


@dataclass
class StepResult:
    name: str
    ok: bool
    detail: str = ""


def _pretty(obj: Any) -> str:
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        return str(obj)


def _request(
    method: str,
    path: str,
    token: Optional[str] = None,
    json_body: Optional[Dict[str, Any]] = None,
    expected: Tuple[int, ...] = (200, 201),
) -> Tuple[bool, int, Any, Dict[str, str]]:
    url = BASE_URL.rstrip("/") + path
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    resp = requests.request(method, url, headers=headers, json=json_body, timeout=25)
    try:
        data = resp.json()
    except Exception:
        data = resp.text

    ok = resp.status_code in expected
    return ok, resp.status_code, data, dict(resp.headers)


def _discover_token_endpoint() -> Optional[str]:
    candidates = [
        "/api/auth/token/",
        "/api/token/",
        "/api/token/obtain/",
        "/api/token/obtain_pair/",
        "/api/jwt/create/",
        "/api/login/",
        "/api/auth/login/",
    ]
    for c in candidates:
        _, code, _, _ = _request("GET", c, expected=(200, 401, 403, 405))
        if code != 404:
            return c
    return None


def _login(username: str, password: str) -> Tuple[Optional[str], str]:
    token_ep = _discover_token_endpoint()
    if not token_ep:
        return None, "Could not discover token endpoint (all candidates returned 404)."

    payload_variants = [
        {"username": username, "password": password},
        {"email": username, "password": password},
        {"identifier": username, "password": password},
    ]
    last_data: Any = None

    for payload in payload_variants:
        ok, _, data, _ = _request("POST", token_ep, json_body=payload, expected=(200, 201))
        last_data = data
        if ok:
            if isinstance(data, dict):
                for key in ("access", "token", "access_token", "jwt"):
                    if key in data and isinstance(data[key], str):
                        return data[key], f"Logged in via {token_ep} using keys {list(payload.keys())}"

                for key in ("data", "result"):
                    if key in data and isinstance(data[key], dict):
                        for tkey in ("access", "token", "access_token"):
                            if tkey in data[key] and isinstance(data[key][tkey], str):
                                return data[key][tkey], f"Logged in via {token_ep} (nested)"

            return None, f"Login succeeded but token field not recognized. Response: {_pretty(data)}"

    return None, f"Login failed on {token_ep}. Last response: {_pretty(last_data)}"


def _find_first_working_endpoint(endpoints: List[Tuple[str, str]]) -> Optional[Tuple[str, str]]:
    for method, path in endpoints:
        _, code, _, _ = _request(method, path, expected=(200, 401, 403, 405))
        if code != 404:
            return method, path
    return None


def _options(path: str, token: str) -> Tuple[bool, int, Any]:
    ok, code, data, _ = _request("OPTIONS", path, token=token, expected=(200, 204))
    return ok, code, data


def _extract_writable_fields_from_options(options_payload: Any) -> Dict[str, Any]:
    fields: Dict[str, Any] = {}

    if isinstance(options_payload, dict):
        actions = options_payload.get("actions")
        if isinstance(actions, dict):
            post = actions.get("POST")
            if isinstance(post, dict):
                return post

        f = options_payload.get("fields")
        if isinstance(f, dict):
            return f

    return fields


def _build_evidence_payload(case_id: int, writable_meta: Dict[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}

    def set_if_exists(key: str, value: Any) -> None:
        payload[key] = value

    case_keys = ["case", "case_id", "case_pk", "related_case", "case_ref"]
    chosen_case_key = None
    for k in case_keys:
        if k in writable_meta:
            chosen_case_key = k
            break
    if not chosen_case_key:
        chosen_case_key = "case"
    set_if_exists(chosen_case_key, case_id)

    required_fields = []
    for fname, meta in (writable_meta or {}).items():
        if isinstance(meta, dict) and meta.get("required") is True:
            required_fields.append(fname)

    if "evidence_type" in (writable_meta or {}) or "evidence_type" in required_fields:
        set_if_exists("evidence_type", "MEDICAL")
    if "title" in (writable_meta or {}) or "title" in required_fields:
        set_if_exists("title", "E2E Evidence")
    if "description" in (writable_meta or {}) or "description" in required_fields:
        set_if_exists("description", "E2E created evidence record")

    if "image_url" in (writable_meta or {}) or "image_url" in required_fields:
        set_if_exists("image_url", "https://example.com/e2e.jpg")
    if "image_urls" in (writable_meta or {}) or "image_urls" in required_fields:
        set_if_exists("image_urls", ["https://example.com/e2e.jpg"])

    for rf in required_fields:
        if rf in payload:
            continue
        if rf in ("case", "case_id", "case_pk", "related_case", "case_ref"):
            continue
        meta = writable_meta.get(rf) if isinstance(writable_meta, dict) else None
        field_type = meta.get("type") if isinstance(meta, dict) else None

        if field_type in ("string", "text", "choice", "email", "url") or field_type is None:
            payload[rf] = "E2E"
        elif field_type in ("integer", "number"):
            payload[rf] = 1
        elif field_type == "boolean":
            payload[rf] = True
        elif field_type == "datetime":
            payload[rf] = "2026-02-18T09:00:00Z"
        elif field_type == "list":
            payload[rf] = []
        else:
            payload[rf] = "E2E"

    return payload


def _post_evidence_variant(
    evidence_path: str,
    token: str,
    base: Dict[str, Any],
    extra: Dict[str, Any],
    expected: Tuple[int, ...],
) -> Tuple[bool, int, Any]:
    payload = dict(base)
    payload.update(extra)
    ok, code, data, _ = _request("POST", evidence_path, token=token, json_body=payload, expected=expected)
    return ok, code, data


def _safe_get_first_id(data: Any) -> Optional[int]:
    if isinstance(data, dict):
        cid = data.get("id") or data.get("case_id")
        if isinstance(cid, int):
            return cid
        if isinstance(cid, str) and cid.isdigit():
            return int(cid)
    return None


def run() -> int:
    results: List[StepResult] = []

    ok, code, data, _ = _request("GET", "/api/schema/", expected=(200,))
    results.append(
        StepResult(
            "schema_available",
            ok,
            f"status={code}" if ok else f"status={code} body={_pretty(data)[:600]}",
        )
    )

    admin_token, msg = _login("admin", "admin1234")
    results.append(StepResult("login_admin", admin_token is not None, msg))
    if not admin_token:
        _print_results(results)
        return 1

    intake_candidates = [
        ("GET", "/api/intake/complaints/"),
        ("GET", "/api/complaints/"),
    ]
    cases_candidates = [
        ("GET", "/api/cases/"),
    ]
    evidence_candidates = [
        ("GET", "/api/evidence/"),
        ("GET", "/api/evidences/"),
    ]
    stats_candidates = [
        ("GET", "/api/stats/"),
        ("GET", "/api/analytics/"),
    ]

    found_intake = _find_first_working_endpoint(intake_candidates)
    found_cases = _find_first_working_endpoint(cases_candidates)
    found_evidence = _find_first_working_endpoint(evidence_candidates)
    found_stats = _find_first_working_endpoint(stats_candidates)

    results.append(StepResult("intake_endpoint_exists", found_intake is not None, str(found_intake)))
    results.append(StepResult("cases_endpoint_exists", found_cases is not None, str(found_cases)))
    results.append(StepResult("evidence_endpoint_exists", found_evidence is not None, str(found_evidence)))
    results.append(StepResult("stats_endpoint_exists", found_stats is not None, str(found_stats)))

    if not found_cases:
        _print_results(results)
        return 1

    ok, code, data, _ = _request("GET", "/api/cases/", token=admin_token, expected=(200,))
    results.append(StepResult("cases_list", ok, f"status={code}" if ok else f"status={code} body={_pretty(data)[:600]}"))

    if found_stats:
        ok, code, data, _ = _request(found_stats[0], found_stats[1], token=admin_token, expected=(200,))
        results.append(StepResult("stats", ok, f"status={code}" if ok else f"status={code} body={_pretty(data)[:600]}"))

    officer_token, msg = _login("officer1", "Pass1234!")
    results.append(StepResult("login_officer1", officer_token is not None, msg))
    if not officer_token:
        _print_results(results)
        return 1

    crime_scene_candidates = [
        ("POST", "/api/cases/from-crime-scene/"),
        ("POST", "/api/cases/from_crime_scene/"),
        ("POST", "/api/cases/crime-scene/"),
    ]
    crime_ep = _find_first_working_endpoint(crime_scene_candidates)
    created_case_id: Optional[int] = None

    if crime_ep:
        payload = {
            "title": "E2E Crime Scene Case",
            "crime_level": 2,
            "scene_time": "2026-02-18T09:00:00Z",
            "location": "E2E Street",
            "report": "E2E report",
            "witnesses": [
                {"national_id": "1111111111", "phone": "09120000000"},
                {"national_id": "2222222222", "phone": "09120000001"},
            ],
            "description": "E2E generated",
            "witnessed_phone": "09123334444",
            "witnessed_national_id": "0022222222",
        }
        ok, code, data, _ = _request(crime_ep[0], crime_ep[1], token=officer_token, json_body=payload, expected=(200, 201))
        created_case_id = _safe_get_first_id(data) if ok else None

        detail = f"status={code} case_id={created_case_id}"
        if not ok:
            detail += f" body={_pretty(data)[:1200]}"
        results.append(StepResult("create_case_from_crime_scene", ok, detail))
    else:
        results.append(StepResult("create_case_from_crime_scene", False, "endpoint_not_found (skipped)"))

    if created_case_id:
        ok, code, data, _ = _request("GET", f"/api/cases/{created_case_id}/", token=officer_token, expected=(200,))
        results.append(StepResult("case_detail_get", ok, f"status={code}" if ok else f"status={code} body={_pretty(data)[:600]}"))

        ok, code, data, _ = _request("GET", "/api/cases/notifications/", token=officer_token, expected=(200,))
        count = None
        notif_id = None
        if ok and isinstance(data, list):
            count = len(data)
            if data and isinstance(data[0], dict):
                notif_id = data[0].get("id")
        results.append(StepResult("notifications_list", ok, f"status={code} count={count}" if ok else f"status={code} body={_pretty(data)[:600]}"))

        if notif_id:
            ok, code, data, _ = _request("POST", f"/api/cases/notifications/{notif_id}/mark_read/", token=officer_token, expected=(200,))
            results.append(StepResult("notification_mark_read", ok, f"status={code}" if ok else f"status={code} body={_pretty(data)[:600]}"))
        else:
            results.append(StepResult("notification_mark_read", False, "no_notification_found"))

        if found_evidence:
            evidence_path = found_evidence[1]
            opt_ok, _, opt_data = _options(evidence_path, officer_token)
            writable = _extract_writable_fields_from_options(opt_data) if opt_ok else {}

            ev_payload = _build_evidence_payload(int(created_case_id), writable)

            ok, code, data, _ = _request("POST", evidence_path, token=officer_token, json_body=ev_payload, expected=(200, 201))
            if not ok:
                if isinstance(data, dict) and "error" in data and isinstance(data["error"], dict):
                    detail = data["error"].get("detail")
                    if isinstance(detail, dict) and ("case" in detail or "case_id" in detail):
                        alt_payload = dict(ev_payload)
                        if "case" in alt_payload and "case_id" not in alt_payload:
                            alt_payload["case_id"] = alt_payload.pop("case")
                        elif "case_id" in alt_payload and "case" not in alt_payload:
                            alt_payload["case"] = alt_payload.pop("case_id")
                        ok2, code2, data2, _ = _request("POST", evidence_path, token=officer_token, json_body=alt_payload, expected=(200, 201))
                        ok, code, data = ok2, code2, data2

            results.append(
                StepResult(
                    "evidence_create",
                    ok,
                    f"status={code}" if ok else f"status={code} body={_pretty(data)[:1200]} payload={_pretty(ev_payload)[:600]}",
                )
            )

            base_ev = {
                "case": int(created_case_id),
                "title": "E2E Evidence Variant",
                "description": "E2E variant evidence record",
            }

            ok_m, code_m, data_m = _post_evidence_variant(
                evidence_path,
                officer_token,
                base_ev,
                {"evidence_type": "MEDICAL", "image_urls": ["https://example.com/a.jpg"]},
                expected=(200, 201),
            )
            results.append(StepResult("evidence_medical_min", ok_m, f"status={code_m}" if ok_m else f"status={code_m} body={_pretty(data_m)[:500]}"))

            ok_m0, code_m0, data_m0 = _post_evidence_variant(
                evidence_path,
                officer_token,
                base_ev,
                {"evidence_type": "MEDICAL"},
                expected=(400,),
            )
            results.append(StepResult("evidence_medical_requires_image", ok_m0, f"status={code_m0}"))

            ok_v_bad, code_v_bad, data_v_bad = _post_evidence_variant(
                evidence_path,
                officer_token,
                base_ev,
                {"evidence_type": "VEHICLE", "plate_number": "11الف111", "serial_number": "SER123"},
                expected=(400,),
            )
            results.append(StepResult("evidence_vehicle_xor_reject_both", ok_v_bad, f"status={code_v_bad}"))

            ok_v_ok, code_v_ok, data_v_ok = _post_evidence_variant(
                evidence_path,
                officer_token,
                base_ev,
                {"evidence_type": "VEHICLE", "plate_number": "11الف111", "vehicle_model": "X", "vehicle_color": "Black"},
                expected=(200, 201),
            )
            results.append(StepResult("evidence_vehicle_ok_plate", ok_v_ok, f"status={code_v_ok}" if ok_v_ok else f"status={code_v_ok} body={_pretty(data_v_ok)[:500]}"))

            ok_v_empty, code_v_empty, data_v_empty = _post_evidence_variant(
                evidence_path,
                officer_token,
                base_ev,
                {"evidence_type": "VEHICLE"},
                expected=(400,),
            )
            results.append(StepResult("evidence_vehicle_requires_plate_or_serial", ok_v_empty, f"status={code_v_empty}"))

            ok_id, code_id, data_id = _post_evidence_variant(
                evidence_path,
                officer_token,
                base_ev,
                {"evidence_type": "ID_DOC", "id_fields": {"full_name": "John Doe", "national_id": "1234567890"}},
                expected=(200, 201),
            )
            results.append(StepResult("evidence_id_doc_kv", ok_id, f"status={code_id}" if ok_id else f"status={code_id} body={_pretty(data_id)[:500]}"))

            ok_w_bad, code_w_bad, data_w_bad = _post_evidence_variant(
                evidence_path,
                officer_token,
                base_ev,
                {"evidence_type": "WITNESS"},
                expected=(400,),
            )
            results.append(StepResult("evidence_witness_requires_text_or_media", ok_w_bad, f"status={code_w_bad}"))

            ok_w_ok, code_w_ok, data_w_ok = _post_evidence_variant(
                evidence_path,
                officer_token,
                base_ev,
                {"evidence_type": "WITNESS", "transcription": "Witness statement"},
                expected=(200, 201),
            )
            results.append(StepResult("evidence_witness_ok_transcription", ok_w_ok, f"status={code_w_ok}" if ok_w_ok else f"status={code_w_ok} body={_pretty(data_w_ok)[:500]}"))

            ok, code, data, _ = _request("GET", evidence_path, token=officer_token, expected=(200,))
            results.append(StepResult("evidence_list", ok, f"status={code}" if ok else f"status={code} body={_pretty(data)[:600]}"))

        ok, code, data, _ = _request(
            "POST",
            f"/api/cases/{created_case_id}/complainants/",
            token=officer_token,
            json_body={"user_id": 1},
            expected=(200, 201, 400),
        )
        ok2 = ok or code == 400
        results.append(StepResult("complainants_add", ok2, f"status={code} body={_pretty(data)[:400]}"))

        ok, code, data, _ = _request("GET", f"/api/cases/{created_case_id}/dossier/", token=officer_token, expected=(200,))
        results.append(StepResult("case_dossier", ok, f"status={code}" if ok else f"status={code} body={_pretty(data)[:600]}"))
    else:
        results.append(StepResult("case_detail_get", False, "no_case_created"))
        results.append(StepResult("notifications_list", False, "no_case_created"))
        results.append(StepResult("notification_mark_read", False, "no_case_created"))
        results.append(StepResult("evidence_create", False, "no_case_created"))
        results.append(StepResult("evidence_medical_min", False, "no_case_created"))
        results.append(StepResult("evidence_medical_requires_image", False, "no_case_created"))
        results.append(StepResult("evidence_vehicle_xor_reject_both", False, "no_case_created"))
        results.append(StepResult("evidence_vehicle_ok_plate", False, "no_case_created"))
        results.append(StepResult("evidence_vehicle_requires_plate_or_serial", False, "no_case_created"))
        results.append(StepResult("evidence_id_doc_kv", False, "no_case_created"))
        results.append(StepResult("evidence_witness_requires_text_or_media", False, "no_case_created"))
        results.append(StepResult("evidence_witness_ok_transcription", False, "no_case_created"))
        results.append(StepResult("evidence_list", False, "no_case_created"))
        results.append(StepResult("complainants_add", False, "no_case_created"))
        results.append(StepResult("case_dossier", False, "no_case_created"))

    _print_results(results)

    critical = [
        "schema_available",
        "login_admin",
        "cases_endpoint_exists",
        "cases_list",
        "create_case_from_crime_scene",
        "evidence_create",
        "evidence_vehicle_xor_reject_both",
        "evidence_vehicle_requires_plate_or_serial",
        "evidence_medical_requires_image",
        "evidence_witness_requires_text_or_media",
    ]
    failed_critical = [r for r in results if (r.name in critical and not r.ok)]
    return 1 if failed_critical else 0


def _print_results(results: List[StepResult]) -> None:
    print("\n=== E2E CHECK RESULTS ===")
    max_name = max((len(r.name) for r in results), default=10)
    for r in results:
        status = "PASS" if r.ok else "FAIL"
        print(f"{status:<4}  {r.name:<{max_name}}  {r.detail}")
    print("=========================\n")


if __name__ == "__main__":
    sys.exit(run())
