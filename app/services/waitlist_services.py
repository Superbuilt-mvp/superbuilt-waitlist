"""Mirror of src/services/waitListServices.ts."""
from typing import Any
from app.models.waitlist_user import (
    waitlist_users,
    users,
    build_waitlist_user_doc,
    build_user_doc,
)
from app.helpers.serialize import serialize_doc


class WaitlistService:
    @staticmethod
    async def add_user(data: dict[str, Any]) -> dict[str, Any]:
        """
        Mirror:
          const existingUser = await WaitlistUser.findOne({ email: data.email });
          if (existingUser) return { message: "Already submitted" };
          const user = new WaitlistUser(data);
          await user.save();
          return { message: "Successfully submitted", user };
        """
        email = data.get("email") if isinstance(data, dict) else None
        existing = await waitlist_users().find_one({"email": email})
        if existing:
            return {"message": "Already submitted"}

        doc = build_waitlist_user_doc(data)
        result = await waitlist_users().insert_one(doc)
        # Re-fetch to return the doc with _id (matches Mongoose new-doc shape).
        saved = await waitlist_users().find_one({"_id": result.inserted_id})
        return {"message": "Successfully submitted", "user": serialize_doc(saved)}

    @staticmethod
    async def auth_handler(payload: dict[str, Any]) -> dict[str, Any]:
        """
        Mirror:
          let user = await User.findOne({ email });
          if (user) return { user, newSignUp: false };
          user = await User.create({ email, name, avatar_url, provider });
          return { user, newSignUp: true };
        """
        email = payload.get("email")
        existing = await users().find_one({"email": email})
        if existing:
            return {"user": existing, "newSignUp": False}

        doc = build_user_doc(
            {
                "email": email,
                "name": payload.get("name"),
                "avatar_url": payload.get("avatar_url"),
                "provider": payload.get("provider"),
            }
        )
        result = await users().insert_one(doc)
        created = await users().find_one({"_id": result.inserted_id})
        return {"user": created, "newSignUp": True}
