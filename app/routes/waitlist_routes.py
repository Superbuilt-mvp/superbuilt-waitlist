"""Mirror of src/routes/waitListRoutes.ts."""
from fastapi import APIRouter, Request
from app.controllers.waitlist_controller import WaitlistController

router = APIRouter()


@router.post("/waitlist")
async def add_to_waitlist(request: Request):
    return await WaitlistController.add_to_waitlist(request)


@router.get("/google-login")
async def google_login(request: Request):
    return await WaitlistController.google_sign_in_sign_up(request)
