import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import OUTPUTS_DIR

USERS_FILE = OUTPUTS_DIR / "users.json"
REVIEW_LOGS_FILE = OUTPUTS_DIR / "review_logs.jsonl"
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def init_db() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        users = _users_from_env()
        USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")
    if not REVIEW_LOGS_FILE.exists():
        REVIEW_LOGS_FILE.write_text("", encoding="utf-8")


def _users_from_env() -> list[dict]:
    admin_user = os.getenv("APP_ADMIN_EMAIL", os.getenv("APP_ADMIN_USERNAME", "admin@example.com"))
    admin_pass = os.getenv("APP_ADMIN_PASSWORD", "change_me_admin_password")
    analyst_user = os.getenv("APP_ANALYST_EMAIL", os.getenv("APP_ANALYST_USERNAME", "analyst@example.com"))
    analyst_pass = os.getenv("APP_ANALYST_PASSWORD", "change_me_analyst_password")
    return [
        {"username": admin_user, "password": admin_pass, "role": "legal_admin"},
        {"username": analyst_user, "password": analyst_pass, "role": "analyst"},
    ]


def _load_users() -> list[dict]:
    if not USERS_FILE.exists():
        return []
    return json.loads(USERS_FILE.read_text(encoding="utf-8"))


def authenticate_user(username: str, password: str) -> Optional[dict]:
    for user in _load_users():
        if user.get("username") == username and user.get("password") == password:
            return {"username": username, "role": user.get("role", "analyst")}
    return None


def create_user(username: str, password: str, role: str = "analyst") -> tuple[bool, str]:
    clean_username = username.strip().lower()
    clean_password = password.strip()
    if not clean_username or not clean_password:
        return False, "Email and password are required."
    if not EMAIL_REGEX.match(clean_username):
        return False, "Please enter a valid email address."
    users = _load_users()
    if any(u.get("username") == clean_username for u in users):
        return False, "Email already exists."
    users.append({"username": clean_username, "password": clean_password, "role": role})
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")
    return True, f"Account created for '{clean_username}'. You can login now."


def log_review(username: str, role: str, file_name: str, report_dict: dict) -> None:
    payload = {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "username": username,
        "role": role,
        "file_name": Path(file_name).name,
        "decision": report_dict.get("overall_decision", "unknown"),
        "risk_score": report_dict.get("overall_risk_score", 0),
        "report": report_dict,
    }
    with REVIEW_LOGS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
