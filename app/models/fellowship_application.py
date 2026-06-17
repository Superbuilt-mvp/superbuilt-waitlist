"""Mirror of FellowshipApplicationSchema in src/model/waitListUser.ts."""
from motor.motor_asyncio import AsyncIOMotorCollection
from app.db.db import get_db

FELLOWSHIP_APPLICATIONS = "fellowshipapplications"


def fellowship_applications() -> AsyncIOMotorCollection:
    return get_db()[FELLOWSHIP_APPLICATIONS]


FELLOWSHIP_FIELDS = [
    "full_name",
    "college",
    "degree",
    "topics_of_interest",
    "why_superbuilt",
    "portfolio_link",
    "track",
    "payment_link_id",
    "payment_link_url",
    "payment_status",
]

TRACK_AMOUNTS: dict[str, int] = {
    "core": 49900,  # paise (₹499)
    "pro":  99900,  # paise (₹999)
}
