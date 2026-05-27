"""Mirror of src/controller/onboardingController.ts."""
from fastapi import Request
from fastapi.responses import JSONResponse
from app.services.onboarding_services import OnboardingService


class OnboardingController:
    @staticmethod
    async def save_onboarding(email: str, request: Request):
        try:
            if not email:
                return JSONResponse(
                    status_code=401,
                    content={"status": False, "message": "Unauthorized"},
                )

            body = {}
            try:
                body = await request.json()
            except Exception:
                body = {}

            payload = {
                "role": body.get("role"),
                "org_type": body.get("org_type"),
                "firm_size": body.get("firm_size"),
                "country": body.get("country"),
                "use_cases": body.get("use_cases"),
                "how_found": body.get("how_found"),
            }

            result = await OnboardingService.save_onboarding(email, payload)
            return JSONResponse(
                status_code=200,
                content={
                    "status": True,
                    "message": "Onboarding saved successfully",
                    "data": result,
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
    async def get_onboarding(email: str):
        try:
            if not email:
                return JSONResponse(
                    status_code=401,
                    content={"status": False, "message": "Unauthorized"},
                )
            data = await OnboardingService.get_onboarding(email)
            return JSONResponse(
                status_code=200,
                content={"status": True, "data": data if data else None},
            )
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "status": False,
                    "message": str(error) or "Internal Server Error",
                },
            )
