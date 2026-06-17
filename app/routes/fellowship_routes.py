"""Mirror of src/routes/fellowshipRoutes.ts."""
from fastapi import APIRouter, Request
from app.controllers.fellowship_controller import FellowshipController

router = APIRouter()


@router.post("/fellowship")
async def apply_fellowship(request: Request):
    return await FellowshipController.apply(request)
