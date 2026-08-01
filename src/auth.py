import json
import os
import re
import hashlib
import secrets
from datetime import datetime, timedelta

USERS_FILE = "users.json"
SESSIONS_FILE = "sessions.json"
PENDING_FILE = "pending_signups.json"

CODE_EXPIRY_MINUTES = 10


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()


# ---------- Validation ----------

def is_valid_username(username: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z]+", username))


def is_valid_gmail(email: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@gmail\.com", email))


def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=]", password):
        return False
    return True


# ---------- Pending Signups (before email verification) ----------

def create_pending_signup(username: str, email: str, password: str) -> str:
    pending = load_json(PENDING_FILE)

    code = f"{secrets.randbelow(1000000):06d}"
    salt = secrets.token_hex(16)

    pending[email] = {
        "username": username,
        "salt": salt,
        "password_hash": hash_password(password, salt),
        "code": code,
        "expires_at": (datetime.now() + timedelta(minutes=CODE_EXPIRY_MINUTES)).isoformat()
    }
    save_json(PENDING_FILE, pending)
    return code


def verify_pending_code(email: str, code: str):
    pending = load_json(PENDING_FILE)
    entry = pending.get(email)

    if not entry:
        return None, "No signup found for this email"

    if datetime.now() > datetime.fromisoformat(entry["expires_at"]):
        del pending[email]
        save_json(PENDING_FILE, pending)
        return None, "Verification code expired, please sign up again"

    if entry["code"] != code:
        return None, "Incorrect verification code"

    return entry, None


def finalize_signup(email: str):
    pending = load_json(PENDING_FILE)
    entry = pending.get(email)

    if not entry:
        return False

    users = load_json(USERS_FILE)
    users[entry["username"]] = {
        "email": email,
        "salt": entry["salt"],
        "password_hash": entry["password_hash"],
        "created_at": datetime.now().isoformat()
    }
    save_json(USERS_FILE, users)

    del pending[email]
    save_json(PENDING_FILE, pending)
    return True


def username_exists(username: str) -> bool:
    users = load_json(USERS_FILE)
    return username in users


def email_exists(email: str) -> bool:
    users = load_json(USERS_FILE)
    return any(u.get("email") == email for u in users.values())


# ---------- Login ----------

def verify_user(username: str, password: str) -> bool:
    users = load_json(USERS_FILE)
    user = users.get(username)

    if not user:
        return False

    return hash_password(password, user["salt"]) == user["password_hash"]


# ---------- Sessions ----------

def create_session(username: str) -> str:
    sessions = load_json(SESSIONS_FILE)
    token = secrets.token_hex(32)

    sessions[token] = {
        "username": username,
        "created_at": datetime.now().isoformat()
    }
    save_json(SESSIONS_FILE, sessions)
    return token


def get_username_from_token(token: str):
    if not token:
        return None

    sessions = load_json(SESSIONS_FILE)
    session = sessions.get(token)

    if not session:
        return None

    return session["username"]


def delete_session(token: str):
    sessions = load_json(SESSIONS_FILE)
    if token in sessions:
        del sessions[token]
        save_json(SESSIONS_FILE, sessions)


# ---------- Account Deletion ----------

def delete_user(username: str) -> bool:
    users = load_json(USERS_FILE)
    if username not in users:
        return False
    del users[username]
    save_json(USERS_FILE, users)
    return True


def delete_all_sessions_for_user(username: str):
    sessions = load_json(SESSIONS_FILE)
    tokens_to_delete = [t for t, data in sessions.items() if data.get("username") == username]
    for token in tokens_to_delete:
        del sessions[token]
    save_json(SESSIONS_FILE, sessions)
