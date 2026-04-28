"""
MongoDB Atlas — Central Database Module
সব ফাইল এই module ব্যবহার করবে।
MONGODB_URI environment variable set করতে হবে।
"""

import os
import json
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError

MONGODB_URI = os.environ.get("MONGODB_URI", "")

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        if not MONGODB_URI:
            raise RuntimeError("❌ MONGODB_URI environment variable not set!")
        _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
        _db = _client["otp_bot"]
    return _db

# ─── Collections ────────────────────────────────────────────────
def col_users():
    return get_db()["users"]

def col_numbers():
    return get_db()["numbers"]

def col_used_stats():
    return get_db()["used_stats"]

def col_seen():
    return get_db()["seen_ids"]

# ─── Users ──────────────────────────────────────────────────────
def get_user(user_id: int) -> dict:
    uid = str(user_id)
    doc = col_users().find_one({"_id": uid})
    if doc is None:
        doc = {
            "_id": uid,
            "balance": 0.0,
            "total_earned": 0.0,
            "withdraw_requests": [],
            "active_number": None,
            "active_platform": None,
            "active_country": None,
            "active_usdt": 0.0,
            "waiting_otp": False,
            "otp_count": 0,
            "old_numbers": [],
            "tracked_numbers": [],
            "first_name": "",
            "last_name": "",
            "username": "",
        }
        col_users().insert_one(doc)
    doc.setdefault("old_numbers", [])
    doc.setdefault("tracked_numbers", [])
    return doc

def save_user(user: dict):
    uid = user["_id"]
    col_users().replace_one({"_id": uid}, user, upsert=True)

def get_all_users() -> dict:
    """Returns {uid_str: user_doc} dict"""
    return {doc["_id"]: doc for doc in col_users().find()}

def get_active_numbers() -> dict:
    """active_numbers: {number: user_id_int}"""
    active = {}
    for doc in col_users().find():
        uid = int(doc["_id"])
        for t in doc.get("tracked_numbers", []):
            if t.get("status") in ("waiting", "received"):
                active[t["number"]] = uid
        if not doc.get("tracked_numbers") and doc.get("active_number"):
            active[doc["active_number"]] = uid
    return active

# ─── Numbers DB ─────────────────────────────────────────────────
def get_numbers_db() -> dict:
    """Returns full numbers_db dict"""
    doc = col_numbers().find_one({"_id": "numbers_db"})
    if doc is None:
        return {}
    return doc.get("data", {})

def save_numbers_db(numbers_db: dict):
    col_numbers().replace_one(
        {"_id": "numbers_db"},
        {"_id": "numbers_db", "data": numbers_db},
        upsert=True
    )

# ─── Used Stats ─────────────────────────────────────────────────
def get_used_stats() -> dict:
    doc = col_used_stats().find_one({"_id": "used_stats"})
    if doc is None:
        return {}
    return doc.get("data", {})

def save_used_stats(used_stats: dict):
    col_used_stats().replace_one(
        {"_id": "used_stats"},
        {"_id": "used_stats", "data": used_stats},
        upsert=True
    )

# ─── Seen IDs (OTP Monitor) ─────────────────────────────────────
def load_seen() -> set:
    doc = col_seen().find_one({"_id": "seen"})
    if doc is None:
        return set()
    return set(doc.get("ids", []))

def save_seen(seen_set: set):
    seen_list = list(seen_set)[-2000:]
    col_seen().replace_one(
        {"_id": "seen"},
        {"_id": "seen", "ids": seen_list},
        upsert=True
    )
