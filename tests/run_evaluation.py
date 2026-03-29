from __future__ import annotations

import json
import os
import pickle
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
RESPONSES_DIR = ROOT / "tests" / "responses"
SERVER_LOG = ROOT / "tests" / "backend_server.log"
SERVER_ERR = ROOT / "tests" / "backend_server.err"
TEST_PORT = int(os.getenv("NIMBUS_TEST_PORT", "5000"))
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"

sys.path.insert(0, str(BACKEND_DIR))

from config import settings  # noqa: E402
from utils.bedrock_client import invoke_bedrock  # noqa: E402
from utils.dynamo_client import _get_table  # noqa: E402


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def read_json_response(response) -> tuple[str, Any]:
    raw = response.read().decode("utf-8", errors="replace")
    try:
        return raw, json.loads(raw)
    except json.JSONDecodeError:
        return raw, None


def request_json(method: str, path: str, payload: dict | None = None) -> dict[str, Any]:
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw, parsed = read_json_response(response)
            return {"status": response.status, "raw": raw, "json": parsed}
    except urllib.error.HTTPError as exc:
        raw, parsed = read_json_response(exc)
        return {"status": exc.code, "raw": raw, "json": parsed}
    except Exception as exc:  # noqa: BLE001
        return {"status": 0, "raw": str(exc), "json": None}


def is_port_open(host: str, port: int) -> bool:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(1)
        return sock.connect_ex((host, port)) == 0


class ServerManager:
    def __init__(self) -> None:
        self.process: subprocess.Popen[str] | None = None

    def start(self) -> None:
        SERVER_LOG.parent.mkdir(parents=True, exist_ok=True)
        SERVER_LOG.write_text("", encoding="utf-8")
        SERVER_ERR.write_text("", encoding="utf-8")
        self.process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(TEST_PORT)],
            cwd=BACKEND_DIR,
            stdout=SERVER_LOG.open("w", encoding="utf-8"),
            stderr=SERVER_ERR.open("w", encoding="utf-8"),
            text=True,
        )
        self.wait_until_ready()

    def wait_until_ready(self, timeout: int = 60) -> None:
        deadline = time.time() + timeout
        last_error = ""
        while time.time() < deadline:
            if self.process and self.process.poll() is not None:
                err_text = SERVER_ERR.read_text(encoding="utf-8", errors="replace")
                log_text = SERVER_LOG.read_text(encoding="utf-8", errors="replace")
                raise RuntimeError(f"Backend exited early.\nSTDERR:\n{err_text}\nSTDOUT:\n{log_text}")
            if is_port_open("127.0.0.1", TEST_PORT):
                health = request_json("GET", "/health")
                if health["status"] == 200:
                    return
                last_error = health["raw"]
            time.sleep(1)
        raise TimeoutError(f"Backend did not become healthy in time. Last health error: {last_error}")

    def ensure_running(self) -> None:
        if self.process is None or self.process.poll() is not None or not is_port_open("127.0.0.1", TEST_PORT):
            self.stop()
            self.start()

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        self.process = None


def count_index_chunks() -> dict[str, int]:
    counts = {}
    base = ROOT / "embeddings"
    for source in ("compliance", "azure", "gcp"):
        with (base / f"{source}_index.pkl").open("rb") as handle:
            counts[source] = len(pickle.load(handle))
    return counts


def check_dynamodb() -> dict[str, Any]:
    table = _get_table()
    description = table.meta.client.describe_table(TableName=table.name)["Table"]
    return {
        "table": table.name,
        "status": description.get("TableStatus"),
        "itemCount": description.get("ItemCount"),
        "region": settings.AWS_REGION,
    }


def check_bedrock() -> dict[str, Any]:
    response = invoke_bedrock("Reply with exactly OK.", max_tokens=10, temperature=0.0)
    return {"modelId": settings.BEDROCK_MODEL_ID, "response": response.strip()}


def record_case(path: Path, label: str, calls: list[dict[str, Any]], meta: dict[str, Any] | None = None) -> None:
    payload = {
        "label": label,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "calls": calls,
    }
    if meta:
        payload["meta"] = meta
    save_json(path, payload)


def session_snapshot(session_id: str) -> dict[str, Any]:
    return request_json("GET", f"/sessions/{session_id}")


def choose_fields(config_payload: dict[str, Any], limit: int = 2) -> list[tuple[str, dict[str, Any]]]:
    config = (config_payload or {}).get("config") or {}
    items = []
    for field_id, entry in config.items():
        if isinstance(entry, dict):
            items.append((field_id, entry))
    chosen = [item for item in items if item[1].get("value") is not None][:limit]
    return chosen or items[:limit]


def run_case_1() -> dict[str, Any]:
    description = (
        "We are a mid-sized healthcare company operating in the US. "
        "We handle patient records and medical imaging data. "
        "We must comply with HIPAA. We are risk-averse and prioritize security over cost."
    )
    calls = []
    intent = request_json("POST", "/intent", {"description": description, "provider": "azure"})
    calls.append({"endpoint": "/intent", "request": {"description": description, "provider": "azure"}, "response": intent})
    session_id = ((intent.get("json") or {}).get("sessionId")) if intent["status"] == 200 else None
    config = request_json(
        "POST",
        "/config",
        {"sessionId": session_id, "service": "Blob Storage", "provider": "azure"},
    )
    calls.append(
        {
            "endpoint": "/config",
            "request": {"sessionId": session_id, "service": "Blob Storage", "provider": "azure"},
            "response": config,
        }
    )
    if session_id:
        calls.append({"endpoint": f"/sessions/{session_id}", "request": None, "response": session_snapshot(session_id)})
    record_case(RESPONSES_DIR / "test_case_1.json", "Test Case 1 - Healthcare Azure Recommendation", calls)
    return {"session_id": session_id, "intent": intent, "config": config}


def run_case_2() -> dict[str, Any]:
    description = (
        "We are a fintech startup processing payments and storing card data. "
        "We must comply with PCI-DSS. We are cost-sensitive but cannot compromise on encryption or access control."
    )
    calls = []
    intent = request_json("POST", "/intent", {"description": description, "provider": "gcp"})
    calls.append({"endpoint": "/intent", "request": {"description": description, "provider": "gcp"}, "response": intent})
    session_id = ((intent.get("json") or {}).get("sessionId")) if intent["status"] == 200 else None
    config = request_json(
        "POST",
        "/config",
        {"sessionId": session_id, "service": "Cloud Storage", "provider": "gcp"},
    )
    calls.append(
        {
            "endpoint": "/config",
            "request": {"sessionId": session_id, "service": "Cloud Storage", "provider": "gcp"},
            "response": config,
        }
    )
    if session_id:
        calls.append({"endpoint": f"/sessions/{session_id}", "request": None, "response": session_snapshot(session_id)})
    record_case(RESPONSES_DIR / "test_case_2.json", "Test Case 2 - Fintech GCP Recommendation", calls)
    return {"session_id": session_id, "intent": intent, "config": config}


def run_case_3() -> dict[str, Any]:
    description = (
        "We are a mid-sized legal firm storing confidential client documents on Azure Blob Storage. "
        "We must comply with SOC2."
    )
    existing_config = {
        "encryption": "Microsoft-managed keys",
        "public_access": "enabled",
        "redundancy": "LRS",
        "soft_delete": "disabled",
        "versioning": "disabled",
        "access_tier": "Hot",
        "firewall": "disabled",
    }
    calls = []
    intent = request_json("POST", "/intent", {"description": description, "provider": "azure"})
    calls.append({"endpoint": "/intent", "request": {"description": description, "provider": "azure"}, "response": intent})
    session_id = ((intent.get("json") or {}).get("sessionId")) if intent["status"] == 200 else None
    config = request_json(
        "POST",
        "/config",
        {"sessionId": session_id, "service": "Blob Storage", "provider": "azure"},
    )
    calls.append(
        {
            "endpoint": "/config",
            "request": {"sessionId": session_id, "service": "Blob Storage", "provider": "azure"},
            "response": config,
        }
    )
    optimize = request_json(
        "POST",
        "/optimize",
        {"sessionId": session_id, "service": "Blob Storage", "existingConfig": existing_config},
    )
    calls.append(
        {
            "endpoint": "/optimize",
            "request": {"sessionId": session_id, "service": "Blob Storage", "existingConfig": existing_config},
            "response": optimize,
        }
    )
    if session_id:
        calls.append({"endpoint": f"/sessions/{session_id}", "request": None, "response": session_snapshot(session_id)})
    record_case(RESPONSES_DIR / "test_case_3.json", "Test Case 3 - Azure Storage Optimization", calls)
    return {"session_id": session_id, "config": config, "optimize": optimize}


def run_case_4() -> dict[str, Any]:
    description = (
        "We are an e-commerce company storing user data and transaction records on GCP Cloud Storage. "
        "We handle EU customer data and must comply with GDPR."
    )
    existing_config = {
        "uniform_bucket_level_access": "disabled",
        "public_access_prevention": "inherited",
        "versioning": "disabled",
        "encryption": "Google-managed",
        "retention_policy": "none",
        "logging": "disabled",
    }
    calls = []
    intent = request_json("POST", "/intent", {"description": description, "provider": "gcp"})
    calls.append({"endpoint": "/intent", "request": {"description": description, "provider": "gcp"}, "response": intent})
    session_id = ((intent.get("json") or {}).get("sessionId")) if intent["status"] == 200 else None
    config = request_json(
        "POST",
        "/config",
        {"sessionId": session_id, "service": "Cloud Storage", "provider": "gcp"},
    )
    calls.append(
        {
            "endpoint": "/config",
            "request": {"sessionId": session_id, "service": "Cloud Storage", "provider": "gcp"},
            "response": config,
        }
    )
    optimize = request_json(
        "POST",
        "/optimize",
        {"sessionId": session_id, "service": "Cloud Storage", "existingConfig": existing_config},
    )
    calls.append(
        {
            "endpoint": "/optimize",
            "request": {"sessionId": session_id, "service": "Cloud Storage", "existingConfig": existing_config},
            "response": optimize,
        }
    )
    if session_id:
        calls.append({"endpoint": f"/sessions/{session_id}", "request": None, "response": session_snapshot(session_id)})
    record_case(RESPONSES_DIR / "test_case_4.json", "Test Case 4 - GCP Optimization", calls)
    return {"session_id": session_id, "config": config, "optimize": optimize}


def run_case_5(case_1: dict[str, Any]) -> dict[str, Any]:
    calls = []
    session_id = case_1["session_id"]
    before = session_snapshot(session_id)
    calls.append({"endpoint": f"/sessions/{session_id}", "request": None, "response": before})
    config_payload = (case_1.get("config") or {}).get("json") or {}
    fields = choose_fields(config_payload, limit=2)
    for field_id, entry in fields:
        explain_request = {
            "sessionId": session_id,
            "fieldId": field_id,
            "fieldLabel": field_id,
            "currentValue": entry.get("value"),
            "inlineReason": entry.get("reason", ""),
            "message": f"Explain exactly why you recommended {field_id} and which evidence supported it.",
        }
        explain = request_json("POST", "/explain", explain_request)
        calls.append({"endpoint": "/explain", "request": explain_request, "response": explain})
    after = session_snapshot(session_id)
    calls.append({"endpoint": f"/sessions/{session_id}", "request": None, "response": after})
    record_case(RESPONSES_DIR / "test_case_5.json", "Test Case 5 - Explain Flow", calls)
    return {"session_id": session_id, "before": before, "after": after}


def run_case_6(case_3: dict[str, Any]) -> dict[str, Any]:
    session_id = case_3["session_id"]
    calls = []
    terraform_request = {"sessionId": session_id, "service": "Blob Storage", "provider": "azure"}
    terraform = request_json("POST", "/terraform", terraform_request)
    calls.append({"endpoint": "/terraform", "request": terraform_request, "response": terraform})
    calls.append({"endpoint": f"/sessions/{session_id}", "request": None, "response": session_snapshot(session_id)})
    record_case(RESPONSES_DIR / "test_case_6.json", "Test Case 6 - Terraform Generation", calls)
    return {"session_id": session_id, "terraform": terraform}


def run_case_7() -> dict[str, Any]:
    message = "We are a small startup. We are not sure what compliance we need. We just want a good cloud setup."
    chat_request = {"message": message, "objective": "recommendation", "userId": "evaluation-user"}
    response = request_json("POST", "/chat", chat_request)
    calls = [{"endpoint": "/chat", "request": chat_request, "response": response}]
    session_id = ((response.get("json") or {}).get("sessionId")) if response["status"] == 200 else None
    if session_id:
        calls.append({"endpoint": f"/sessions/{session_id}", "request": None, "response": session_snapshot(session_id)})
    record_case(RESPONSES_DIR / "test_case_7.json", "Test Case 7 - Ambiguous Company", calls)
    return {"session_id": session_id, "chat": response}


def run_case_8() -> dict[str, Any]:
    message = "We are a healthcare company that prefers Azure but our CTO wants to use GCP."
    chat_request = {"message": message, "objective": "recommendation", "userId": "evaluation-user"}
    response = request_json("POST", "/chat", chat_request)
    calls = [{"endpoint": "/chat", "request": chat_request, "response": response}]
    session_id = ((response.get("json") or {}).get("sessionId")) if response["status"] == 200 else None
    if session_id:
        calls.append({"endpoint": f"/sessions/{session_id}", "request": None, "response": session_snapshot(session_id)})
    record_case(RESPONSES_DIR / "test_case_8.json", "Test Case 8 - Provider Conflict", calls)
    return {"session_id": session_id, "chat": response}


def main() -> int:
    server = ServerManager()
    summary: dict[str, Any] = {"generatedAt": datetime.now(timezone.utc).isoformat()}
    try:
        server.start()
        summary["precheck"] = {
            "health": request_json("GET", "/health"),
            "indexCounts": count_index_chunks(),
            "dynamodb": check_dynamodb(),
            "bedrock": check_bedrock(),
        }

        expected = {"compliance": 80, "azure": 65, "gcp": 46}
        if summary["precheck"]["health"]["status"] != 200:
            raise RuntimeError(f"Health check failed: {summary['precheck']['health']}")
        if summary["precheck"]["indexCounts"] != expected:
            raise RuntimeError(
                f"Index counts mismatch: expected {expected}, got {summary['precheck']['indexCounts']}"
            )
        if summary["precheck"]["dynamodb"].get("status") != "ACTIVE":
            raise RuntimeError(f"DynamoDB table not ACTIVE: {summary['precheck']['dynamodb']}")
        if "OK" not in summary["precheck"]["bedrock"].get("response", ""):
            raise RuntimeError(f"Bedrock smoke test failed: {summary['precheck']['bedrock']}")

        results = {}
        for case_name, runner in [
            ("test_case_1", run_case_1),
            ("test_case_2", run_case_2),
            ("test_case_3", run_case_3),
            ("test_case_4", run_case_4),
        ]:
            server.ensure_running()
            results[case_name] = runner()

        server.ensure_running()
        results["test_case_5"] = run_case_5(results["test_case_1"])
        server.ensure_running()
        results["test_case_6"] = run_case_6(results["test_case_3"])
        server.ensure_running()
        results["test_case_7"] = run_case_7()
        server.ensure_running()
        results["test_case_8"] = run_case_8()

        summary["results"] = results
    finally:
        server.stop()
        summary["serverLog"] = SERVER_LOG.read_text(encoding="utf-8", errors="replace") if SERVER_LOG.exists() else ""
        summary["serverErr"] = SERVER_ERR.read_text(encoding="utf-8", errors="replace") if SERVER_ERR.exists() else ""
        save_json(ROOT / "tests" / "evaluation_data.json", summary)

    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
