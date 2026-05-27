"""Mirror of src/routes/creditRoutes.ts."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.controllers.credit_controller import CreditController
from app.middleware.auth_middleware import (
    auth_middleware,
    AuthError,
    auth_error_response,
)

router = APIRouter()


@router.get("/credits")
async def get_credits(request: Request):
    try:
        email = await auth_middleware(request)
    except AuthError as e:
        return auth_error_response(e)
    return await CreditController.get_credits(email)


@router.post("/deduct-credits")
async def deduct_credits(request: Request):
    try:
        email = await auth_middleware(request)
    except AuthError as e:
        return auth_error_response(e)
    return await CreditController.deduct_credits(email, request)
