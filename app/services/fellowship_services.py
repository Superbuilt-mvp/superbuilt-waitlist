"""Mirror of src/services/fellowshipServices.ts."""
import os
from typing import Any
from bson import ObjectId
import razorpay

from app.models.fellowship_application import (
    fellowship_applications,
    TRACK_AMOUNTS,
)
from app.models.waitlist_user import now_utc
from app.helpers.serialize import serialize_doc


class FellowshipService:
    @staticmethod
    async def create_application(data: dict[str, Any]) -> dict[str, Any]:
        col = fellowship_applications()

        # Save application first (mirrors TS: save before payment link)
        doc = {
            "full_name":          data["full_name"],
            "college":            data["college"],
            "degree":             data["degree"],
            "topics_of_interest": data.get("topics_of_interest", []),
            "why_superbuilt":     data["why_superbuilt"],
            "portfolio_link":     data.get("portfolio_link", ""),
            "track":              data["track"],
            "payment_link_id":    "",
            "payment_link_url":   "",
            "payment_status":     "pending",
            "createdAt":          now_utc(),
            "updatedAt":          now_utc(),
            "__v":                0,
        }
        result = await col.insert_one(doc)
        application_id = str(result.inserted_id)

        # Create Razorpay Payment Link
        client = razorpay.Client(
            auth=(os.environ["RAZORPAY_KEY_ID"], os.environ["RAZORPAY_KEY_SECRET"])
        )
        track = data["track"]
        frontend_url = os.environ.get("FRONTEND_URL", "https://superbuilt.ai")
        callback_url = os.environ.get("RAZORPAY_CALLBACK_URL", f"{frontend_url}/Fellowship")

        payment_link = client.payment_link.create({
            "amount":          TRACK_AMOUNTS[track],
            "currency":        "INR",
            "accept_partial":  False,
            "description":     (
                f"Superbuilt AI Fellowship — "
                f"{'Core Track (₹499)' if track == 'core' else 'Pro Track (₹999)'}"
            ),
            "customer":        {"name": data["full_name"]},
            "notify":          {"sms": False, "email": False},
            "reminder_enable": False,
            "notes": {
                "application_id": application_id,
                "track":          track,
                "college":        data["college"],
            },
            "callback_url":    callback_url,
            "callback_method": "get",
        })

        # Persist payment link back to the document
        await col.update_one(
            {"_id": ObjectId(application_id)},
            {"$set": {
                "payment_link_id":  payment_link["id"],
                "payment_link_url": payment_link["short_url"],
                "updatedAt":        now_utc(),
            }},
        )

        return {
            "application_id":   application_id,
            "payment_link_url": payment_link["short_url"],
        }
