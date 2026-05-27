"""
Mirror of src/helper/token.ts.

generateAccessToken signs a JWT with the same claims and same default
expiration logic as the TS version.

Note: jsonwebtoken (Node) defaults to HS256 for string secrets — PyJWT
defaults to HS256 too, so signatures are interchangeable.
"""
import os
import time
import jwt

TOKEN_TYPE_ACCESS = "ACCESS"
TOKEN_TYPE_REFRESH = "REFRESH"

TokenTypes = {
    "ACCESS": TOKEN_TYPE_ACCESS,
    "REFRESH": TOKEN_TYPE_REFRESH,
}


def generate_access_token(user_id, email: str) -> str:
    """
    Equivalent to:
      const exp = Math.floor(Date.now() / 1000) + expiresInMinutes * 60;
      jwt.sign({ userId, email, type: 'ACCESS', exp }, jwt_secret)

    Notes:
    - jsonwebtoken accepts numeric `exp` in the payload directly; PyJWT
      does the same.
    - The TS code reads accessExpirationMinutes as a string from env then
      uses it in arithmetic (auto-coerced). In Python we coerce explicitly.
      Default is 60 (1h), same as TS.
    """
    raw = os.environ.get("accessExpirationMinutes", "60")
    try:
        minutes = int(raw)
    except (TypeError, ValueError):
        minutes = 60

    exp = int(time.time()) + minutes * 60
    jwt_secret = os.environ.get("jwt_secret")
    if not jwt_secret:
        # TS code would crash here too if secret missing — mirror behavior.
        raise RuntimeError("jwt_secret is not set in environment")

    payload = {
        "userId": str(user_id),
        "email": email,
        "type": TOKEN_TYPE_ACCESS,
        "exp": exp,
    }
    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    # PyJWT >=2 returns str; older returned bytes. Ensure str.
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


# Startup warning, mirrors the TS module-level check.
if not os.environ.get("jwt_secret"):
    print(
        "⚠️ WARNING: jwt_secret is not defined in environment variables. "
        "JWT Strategy might fail."
    )
