# Superbuilt Backend (Python)

Drop-in Python port of the original Express + Mongoose backend.
**Same routes, same env vars, same response shapes, same MongoDB collections.**

## Stack

- **Runtime**: Python 3.11+
- **Framework**: FastAPI (ASGI, async) — replaces Express
- **Database**: MongoDB via Motor (async PyMongo) — replaces Mongoose
- **Auth**: Google OAuth 2.0 + JWT via PyJWT (HS256, same as `jsonwebtoken`)
- **HTTP client**: httpx (async) — replaces axios
- **Server**: uvicorn

## Endpoints (unchanged)

| Method | Path                       | Auth   | Description                            |
|--------|----------------------------|--------|----------------------------------------|
| POST   | `/api/v1/waitlist`         | None   | Add user to waitlist                   |
| GET    | `/api/v1/google-login`     | None   | Exchange Google code → JWT + redirect  |
| GET    | `/api/v1/credits`          | Bearer | Get user credit balance                |
| POST   | `/api/v1/deduct-credits`   | Bearer | Deduct credits (mode: base/plus/code)  |
| POST   | `/api/v1/onboarding`       | Bearer | Save onboarding answers (upsert)       |
| GET    | `/api/v1/onboarding`       | Bearer | Get onboarding answers                 |
| GET    | `/`                        | None   | Liveness — `{ message: "Superbuilt API is running ✅" }` |
| GET    | `/health`                  | None   | `{ status: "ok" }`                     |

## Project Structure

```
backend-py/
├── app/
│   ├── server.py                 # FastAPI app + lifespan + CORS + routers
│   ├── db/db.py                  # Motor connect/close
│   ├── models/waitlist_user.py   # Collection names + Mongoose-style doc builders
│   ├── helpers/
│   │   ├── token.py              # JWT generation (matches helper/token.ts)
│   │   └── serialize.py          # Mongo doc → Mongoose-style JSON
│   ├── middleware/auth_middleware.py
│   ├── controllers/
│   │   ├── waitlist_controller.py
│   │   ├── credit_controller.py
│   │   └── onboarding_controller.py
│   ├── services/
│   │   ├── waitlist_services.py
│   │   ├── credit_services.py
│   │   └── onboarding_services.py
│   └── routes/
│       ├── waitlist_routes.py
│       ├── credit_routes.py
│       └── onboarding_routes.py
├── requirements.txt
├── render.yaml                   # Render Blueprint
├── Procfile                      # Fallback start command
├── runtime.txt                   # Python version pin
├── .env.example
└── README.md
```

## Environment Variables

**Names are identical to the TS backend** (some are intentionally camelCase
because the original code reads them that way — do not rename):

| Variable                  | Required | Notes                                          |
|---------------------------|----------|------------------------------------------------|
| `MONGO_URI`               | ✅       | DB name MUST be in the URI                     |
| `jwt_secret`              | ✅       | Same secret as TS backend — tokens stay valid  |
| `accessExpirationMinutes` | ✅       | Default 60 if unset                            |
| `googleClientId`          | ✅       | Google OAuth client ID                         |
| `googleClientSecret`      | ✅       | Google OAuth client secret                     |
| `redirectUri`             | ✅       | Must match Google Console                      |
| `frontendUrl`             | ✅       | Used in OAuth redirect                         |
| `PORT`                    | —        | Default 8080                                   |

## Run Locally

```bash
cd backend-py

# 1. Create venv (Python 3.11+)
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install deps
pip install -r requirements.txt

# 3. Copy and fill env
cp .env.example .env
# edit .env

# 4. Run dev server (autoreload)
uvicorn app.server:app --reload --host 0.0.0.0 --port 8080

# OR run via Python entrypoint
python -m app.server
```

## Deploy to Render

### Option A — Blueprint (recommended)
1. Commit `render.yaml` and push the repo.
2. In Render dashboard → **New → Blueprint** → connect repo.
3. Set the env var values in the dashboard (they're marked `sync: false`).

### Option B — Manual Web Service
- **Environment**: Python
- **Build command**: `pip install -r requirements.txt`
- **Start command**: `uvicorn app.server:app --host 0.0.0.0 --port $PORT`
- **Python version**: 3.11 (via `runtime.txt`)
- Add all env vars listed above.

After deploy, point `NEXT_PUBLIC_BACKEND_URL` in the frontend to the new
Render URL. **No frontend changes needed** — routes and response shapes are
identical to the TS backend.

## Parity Notes (read before migrating production)

Behavior preserved exactly:
- **Collection names**: `waitlistusers`, `users`, `onboardings` — match
  Mongoose's auto-pluralization of model names. Existing data is read
  without migration.
- **JWT**: HS256, same payload shape (`userId`, `email`, `type: "ACCESS"`,
  `exp`). Tokens issued by the TS backend remain valid here and vice versa.
- **Timestamps**: `createdAt`, `updatedAt`, `__v` added on insert; serialized
  as ISO-8601 with `Z` (matches `Date.prototype.toISOString()`).
- **Defaults**: `book_demo` defaults to `false`; `credits` defaults to `0`;
  missing `credits` on existing users is back-filled to `0` (same lazy
  init logic as the TS version).
- **Onboarding upsert**: `findOneAndUpdate(..., { upsert, new, setDefaultsOnInsert })`
  → Motor `find_one_and_update` with `upsert=True`,
  `return_document=ReturnDocument.AFTER`, plus `$setOnInsert` for
  `createdAt`/`__v`.
- **Google OAuth redirect**: same query-param order/encoding via `urlencode`.
- **CORS**: same allowlist; preflight + credentials behavior matches.
- **Error responses**: identical status codes and JSON bodies (including
  `{ status: false, message: ... }`, `{ message: ... }`, `{ error: ... }`
  shapes the frontend already handles).
- **`/` and `/health`**: identical bodies, including the ✅ emoji.

## Switching Back

Both backends speak to the same MongoDB collections with the same field
names and types. You can switch traffic between them at the LB / DNS level
with no data migration. JWTs are signed with the same secret, so users stay
logged in across the switch.
