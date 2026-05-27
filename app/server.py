"""
Mirror of src/server.ts.

Express + Mongoose -> FastAPI + Motor.
- Same routes mounted at /api/v1
- Same CORS allowlist
- Same / and /health endpoints with identical JSON bodies
- DB connects on startup; process exits on failure (matches TS)
"""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load .env before anything else reads env vars.
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.db import connect_db, close_db
from app.routes.waitlist_routes import router as waitlist_router
from app.routes.credit_routes import router as credit_router
from app.routes.onboarding_routes import router as onboarding_router

# Same allowlist as server.ts
ALLOWED_ORIGINS = [
    "https://www.superbuilt.ai",
    "https://superbuilt.ai",
    "http://localhost:3000",
    "http://localhost:3001",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

# CORS: equivalent to the Express cors() callback that allows only listed origins.
# In Express, requests with no Origin (server-to-server, curl) passed through;
# CORSMiddleware only adds headers when there IS an Origin and it matches,
# which is the relevant behavior browsers care about.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers under /api/v1 — matches app.use("/api/v1", router).
app.include_router(waitlist_router, prefix="/api/v1")
app.include_router(credit_router, prefix="/api/v1")
app.include_router(onboarding_router, prefix="/api/v1")


@app.get("/")
async def root():
    return JSONResponse(
        status_code=200, content={"message": "Superbuilt API is running ✅"}
    )


@app.get("/health")
async def health():
    return JSONResponse(status_code=200, content={"status": "ok"})


# Entrypoint for `python -m app.server` / Render start command.
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8080"))
    print(f"🚀 Superbuilt backend running on port {port}")
    uvicorn.run("app.server:app", host="0.0.0.0", port=port, log_level="info")
