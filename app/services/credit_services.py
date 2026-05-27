"""Mirror of src/services/creditServices.ts."""
from app.models.waitlist_user import users, now_utc


class CreditService:
    @staticmethod
    async def get_user_credits(email: str) -> int:
        user = await users().find_one({"email": email})
        if not user:
            raise Exception("User not found")

        # If credits field is missing (old user), initialize it to 0.
        if user.get("credits") is None:
            await users().update_one(
                {"_id": user["_id"]},
                {"$set": {"credits": 0, "updatedAt": now_utc()}},
            )
            return 0
        return user["credits"]

    @staticmethod
    async def deduct_credits(email: str, mode: str) -> int:
        if mode == "base":
            deduction = 10
        elif mode == "plus":
            deduction = 20
        elif mode == "code":
            deduction = 30
        else:
            raise Exception("Invalid mode. Use 'base', 'plus', or 'code'.")

        user = await users().find_one({"email": email})
        if not user:
            raise Exception("User not found")

        current = user.get("credits")
        if current is None:
            current = 0

        if current < deduction:
            raise Exception("Insufficient credits")

        new_credits = current - deduction
        await users().update_one(
            {"_id": user["_id"]},
            {"$set": {"credits": new_credits, "updatedAt": now_utc()}},
        )
        return new_credits
