"""
Helpers to serialize MongoDB docs into the same JSON shape that
Mongoose + Express produce.

Mongoose's default res.json serialization:
- _id: ObjectId -> string
- createdAt / updatedAt: Date -> ISO 8601 string with Z (UTC)
- __v: number stays as number
- nested ObjectIds also stringified

We mimic that here.
"""
from datetime import datetime, timezone
from typing import Any
from bson import ObjectId


def _convert(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        # Mongoose serializes Date as ISO with milliseconds + Z.
        # JS: new Date().toISOString() -> "2024-01-02T03:04:05.678Z"
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)
        # Format to millisecond precision with Z suffix (matches JS toISOString).
        return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"
    if isinstance(value, list):
        return [_convert(v) for v in value]
    if isinstance(value, dict):
        return {k: _convert(v) for k, v in value.items()}
    return value


def serialize_doc(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    """Convert a Mongo doc into a JSON-safe dict matching Mongoose output."""
    if doc is None:
        return None
    return {k: _convert(v) for k, v in doc.items()}
