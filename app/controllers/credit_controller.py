"""Mirror of src/controller/creditController.ts."""
from fastapi import Request
from fastapi.responses import JSONResponse
from app.services.credit_services import CreditService


class CreditController:
    @staticmethod
    async def get_credits(email: str):
        try:
            if not email:
                return JSONResponse(
                    status_code=401,
                    content={
                        "status": False,
                        "message": "Unauthorized: Email not found in token",
                    },
                )
            credits_value = await CreditService.get_user_credits(email)
            return JSONResponse(
                status_code=200,
                content={
                    "status": True,
                    "message": "Credits fetched successfully",
                    "credits": credits_value,
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "status": False,
                    "message": str(error) or "Internal Server Error",
                },
            )

    @staticmethod
    async def deduct_credits(email: str, request: Request):
        try:
            if not email:
                return JSONResponse(
                    status_code=401,
                    content={
                        "status": False,
                        "message": "Unauthorized: Email not found in token",
                    },
                )

            body = {}
            try:
                body = await request.json()
            except Exception:
                body = {}
            mode = body.get("mode") if isinstance(body, dict) else None

            if not mode:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": False,
                        "message": "Mode is required (base, plus, or code)",
                    },
                )

            updated = await CreditService.deduct_credits(email, mode)
            return JSONResponse(
                status_code=200,
                content={
                    "status": True,
                    "message": f"Credits deducted successfully for mode: {mode}",
                    "updatedCredits": updated,
                },
            )
        except Exception as error:
            msg = str(error)
            status_code = 400 if msg == "Insufficient credits" else 500
            return JSONResponse(
                status_code=status_code,
                content={
                    "status": False,
                    "message": msg or "Internal Server Error",
                },
            )
