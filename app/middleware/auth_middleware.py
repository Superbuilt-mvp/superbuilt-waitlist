"""
Mirror of src/middleware/authMiddleware.ts.

In Express it mutates req.email; in FastAPI we return the email string from
the dependency, and controllers grab it via Depends(auth_middleware).

Error responses preserve the exact JSON body and status codes from the TS
version so the frontend sees identical behavior.
"""
import os
from fastapi import Request
from fastapi.responses import JSONResponse
import jwt


class AuthError(Exception):
    """Raised when auth fails; caught in route to return matching JSON."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


async def auth_middleware(request: Request) -> str:
    auth_header = request.headers.get("authorization") or request.headers.get(
        "Authorization"
    )
    if not auth_header or not auth_header.startswith("Bearer "):
        raise AuthError(401, "Authentication token is required")

    token = auth_header.split(" ", 1)[1]

    try:
        jwt_secret = os.environ.get("jwt_secret", "")
        decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
    except Exception:
        raise AuthError(401, "Invalid or expired token")

    email = decoded.get("email")
    if not email:
        raise AuthError(401, "Invalid token: Email not found")

    return email


def auth_error_response(exc: AuthError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})
