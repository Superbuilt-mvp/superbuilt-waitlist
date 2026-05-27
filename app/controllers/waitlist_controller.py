"""Mirror of src/controller/waitListController.ts."""
import os
import traceback
from urllib.parse import urlencode

import httpx
from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.services.waitlist_services import WaitlistService
from app.helpers.token import generate_access_token


class WaitlistController:
    @staticmethod
    async def add_to_waitlist(request: Request):
        try:
            body = await request.json()
            print("Request Body:", body)
            result = await WaitlistService.add_user(body)
            return JSONResponse(
                status_code=201,
                content={"message": "User added to waitlist", "result": result},
            )
        except Exception as err:
            return JSONResponse(status_code=500, content={"error": str(err)})

    @staticmethod
    async def google_sign_in_sign_up(request: Request):
        try:
            print("Google login initiated")
            code = request.query_params.get("code")

            if not code:
                # Match TS: 400 with body { status: false, message: ... }
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": False,
                        "message": "Authorization code is required",
                    },
                )

            # Exchange Google code for tokens.
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    token_resp = await client.post(
                        "https://oauth2.googleapis.com/token",
                        json={
                            "code": code,
                            "client_id": os.environ.get("googleClientId"),
                            "client_secret": os.environ.get("googleClientSecret"),
                            "redirect_uri": os.environ.get("redirectUri"),
                            "grant_type": "authorization_code",
                        },
                    )
                    token_resp.raise_for_status()
                    validate_user = token_resp.json()
            except httpx.HTTPStatusError as token_err:
                # Mirror TS error-shape extraction.
                err_data = {}
                try:
                    err_data = token_err.response.json()
                except Exception:
                    pass
                print("[GOOGLE TOKEN EXCHANGE FAILED]", err_data or str(token_err))
                err_desc = (
                    err_data.get("error_description")
                    or err_data.get("error")
                    or str(token_err)
                )
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": False,
                        "message": f"Token exchange failed: {err_desc}",
                    },
                )
            except Exception as token_err:
                print("[GOOGLE TOKEN EXCHANGE FAILED]", str(token_err))
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": False,
                        "message": f"Token exchange failed: {str(token_err)}",
                    },
                )

            access_token = validate_user.get("access_token")

            # Fetch user info.
            async with httpx.AsyncClient(timeout=30.0) as client:
                userinfo_resp = await client.get(
                    "https://www.googleapis.com/oauth2/v1/userinfo?alt=json",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                userinfo = userinfo_resp.json()

            email = userinfo.get("email")
            name = userinfo.get("name")
            picture = userinfo.get("picture")

            if not email:
                raise Exception("Error fetching email, please try again")

            # Handle user in DB.
            auth_result = await WaitlistService.auth_handler(
                {
                    "email": email,
                    "name": name,
                    "avatar_url": picture,
                    "provider": "google",
                }
            )
            user = auth_result["user"]
            new_sign_up = auth_result["newSignUp"]

            print(
                "New user created" if new_sign_up else "Existing user found",
                "| email:",
                email,
            )

            # Generate access token. TS uses user.id (Mongoose virtual = _id.toString()).
            auth_token = generate_access_token(str(user["_id"]), email)

            # Build redirect URL with proper & separators (matches URLSearchParams).
            params: dict[str, str] = {"token": auth_token}
            if email:
                params["email"] = email
            if name:
                params["name"] = name
            if picture:
                params["avatar_url"] = picture

            frontend_url = os.environ.get("frontendUrl", "")
            redirect_url = (
                f"{frontend_url}/auth/callback/google?{urlencode(params)}"
            )
            return RedirectResponse(url=redirect_url, status_code=302)

        except Exception as error:
            print("Google login error:", str(error))
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"status": False, "message": str(error)},
            )
