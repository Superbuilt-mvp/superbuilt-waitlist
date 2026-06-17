"""Mirror of src/controller/fellowshipController.ts."""
from fastapi import Request
from fastapi.responses import JSONResponse
from app.services.fellowship_services import FellowshipService


class FellowshipController:
    @staticmethod
    async def apply(request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except Exception:
            return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

        full_name      = body.get("full_name", "").strip()
        college        = body.get("college", "").strip()
        degree         = body.get("degree", "").strip()
        why_superbuilt = body.get("why_superbuilt", "").strip()
        track          = body.get("track", "").strip()

        if not all([full_name, college, degree, why_superbuilt]):
            return JSONResponse(
                status_code=400,
                content={"error": "full_name, college, degree, and why_superbuilt are required"},
            )

        if track not in ("core", "pro"):
            return JSONResponse(
                status_code=400,
                content={"error": "track must be 'core' or 'pro'"},
            )

        try:
            result = await FellowshipService.create_application({
                "full_name":          full_name,
                "college":            college,
                "degree":             degree,
                "topics_of_interest": body.get("topics_of_interest", []),
                "why_superbuilt":     why_superbuilt,
                "portfolio_link":     body.get("portfolio_link", ""),
                "track":              track,
            })
            return JSONResponse(status_code=201, content=result)
        except Exception as e:
            print(f"[FellowshipController.apply] {e}")
            return JSONResponse(status_code=500, content={"error": str(e) or "Server error"})
