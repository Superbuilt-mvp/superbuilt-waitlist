"""
Mirror of src/model/waitListUser.ts.

Mongoose auto-pluralizes/lowercases model names for collection names:
  WaitlistUser -> waitlistusers
  User         -> users
  Onboarding   -> onboardings

These collection names MUST match so the Python backend reads the same data
the TS backend wrote.
"""
from datetime import datetime, timezone
from typing import Any
from motor.motor_asyncio import AsyncIOMotorCollection
from app.db.db import get_db

# Collection names (must match Mongoose pluralization).
WAITLIST_USERS = "waitlistusers"
USERS = "users"
ONBOARDINGS = "onboardings"


def now_utc() -> datetime:
    """UTC datetime — Mongoose stores timestamps as BSON Date (UTC)."""
    return datetime.now(timezone.utc)


def waitlist_users() -> AsyncIOMotorCollection:
    return get_db()[WAITLIST_USERS]


def users() -> AsyncIOMotorCollection:
    return get_db()[USERS]


def onboardings() -> AsyncIOMotorCollection:
    return get_db()[ONBOARDINGS]


# ---------- Schema-equivalent defaults / shape builders ----------

# WaitlistUserSchema fields (with defaults & timestamps).
WAITLIST_USER_FIELDS = [
    "full_name",
    "email",
    "phone_number",
    "professional_role",
    "organization",
    "location",
    "firm_size",
    "book_demo",
]


def build_waitlist_user_doc(data: dict[str, Any]) -> dict[str, Any]:
    """
    Mirror Mongoose's behavior of:
    - only persisting schema fields
    - applying defaults (book_demo: false)
    - adding createdAt / updatedAt / __v
    """
    doc: dict[str, Any] = {}
    for f in WAITLIST_USER_FIELDS:
        if f in data and data[f] is not None:
            doc[f] = data[f]
    # required fields are enforced at controller/service level if needed.
    if "book_demo" not in doc:
        doc["book_demo"] = False
    ts = now_utc()
    doc["createdAt"] = ts
    doc["updatedAt"] = ts
    doc["__v"] = 0
    return doc


# UserSchema fields.
USER_FIELDS = ["name", "email", "avatar_url", "provider", "credits"]


def build_user_doc(data: dict[str, Any]) -> dict[str, Any]:
    doc: dict[str, Any] = {}
    for f in USER_FIELDS:
        if f in data and data[f] is not None:
            doc[f] = data[f]
    if "credits" not in doc:
        doc["credits"] = 0
    ts = now_utc()
    doc["createdAt"] = ts
    doc["updatedAt"] = ts
    doc["__v"] = 0
    return doc


# OnboardingSchema fields.
ONBOARDING_FIELDS = [
    "email",
    "role",
    "org_type",
    "firm_size",
    "country",
    "use_cases",
    "how_found",
]


def build_onboarding_set(data: dict[str, Any]) -> dict[str, Any]:
    """Return the $set payload for an onboarding upsert."""
    out: dict[str, Any] = {}
    for f in ONBOARDING_FIELDS:
        if f in data and data[f] is not None:
            out[f] = data[f]
    out["updatedAt"] = now_utc()
    return out
