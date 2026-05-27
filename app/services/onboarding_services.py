"""Mirror of src/services/onboardingServices.ts."""
from typing import Any
from pymongo import ReturnDocument
from app.models.waitlist_user import onboardings, build_onboarding_set, now_utc
from app.helpers.serialize import serialize_doc


class OnboardingService:
    @staticmethod
    async def save_onboarding(email: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Mirror Mongoose:
          OnboardingModel.findOneAndUpdate(
            { email },
            { email, ...data },
            { upsert: true, new: true, setDefaultsOnInsert: true }
          );
        """
        update_set = build_onboarding_set({**data, "email": email})
        # On insert we also need createdAt and __v (Mongoose timestamps + defaults).
        ts = now_utc()
        update_doc = {
            "$set": update_set,
            "$setOnInsert": {"createdAt": ts, "__v": 0},
        }
        result = await onboardings().find_one_and_update(
            {"email": email},
            update_doc,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return serialize_doc(result)

    @staticmethod
    async def get_onboarding(email: str) -> dict[str, Any] | None:
        doc = await onboardings().find_one({"email": email})
        return serialize_doc(doc)
