"""Mirror of src/routes/onboardingRoutes.ts."""
from fastapi import APIRouter, Request

from app.controllers.onboarding_controller import OnboardingController
from app.middleware.auth_middleware import (
    auth_middleware,
    AuthError,
    auth_error_response,
)

router = APIRouter()


@router.post("/onboarding")
async def save_onboarding(request: Request):
    try:
        email = await auth_middleware(request)
    except AuthError as e:
        return auth_error_response(e)
    return await OnboardingController.save_onboarding(email, request)


@router.get("/onboarding")
async def get_onboarding(request: Request):
    try:
        email = await auth_middleware(request)
    except AuthError as e:
        return auth_error_response(e)
    return await OnboardingController.get_onboarding(email)
