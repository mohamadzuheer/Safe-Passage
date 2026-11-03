# ReliefRoute (SafePassage) — Complete Environment Audit & Setup Guide

This document provides a thorough audit of every environment variable in the ReliefRoute codebase, detailing where it belongs, why it is needed, which files read it, and how to safely configure your own credentials.

---

## 1. Environment Variable Master Inventory

| Variable | Service / Component | Purpose | Target File | Required in Dev? | Where to Obtain / Default Value |
|---|---|---|---|---|---|
| `APP_ENV` | Application Core | Sets runtime mode (`development` or `production`) | `backend/.env` | **Yes** | Set to `development` locally |
| `LOG_LEVEL` | Application Core | Controls logging verbosity (`INFO`, `DEBUG`, `WARNING`) | `backend/.env` | **Yes** | Set to `INFO` |
| `DATABASE_URL` | PostgreSQL + PostGIS | Database connection string | `backend/.env` | **Yes** | Local docker: `postgresql://reliefroute:reliefroute@localhost:55432/reliefroute` |
| `REDIS_URL` | Redis Streams & Cache | Redis connection string | `backend/.env` | **Yes** | Local docker: `redis://localhost:6380/0` |
| `VALHALLA_URL` | Valhalla Routing | Address of Valhalla routing container | `backend/.env` | **Yes** | Local docker: `http://localhost:8002` |
| `REGION_BBOX` | Geospatial Poller | Bounding box for Andhra Pradesh (`min_lon,min_lat,max_lon,max_lat`) | `backend/.env` | **Yes** | Default: `76.6,12.5,84.9,20.1` |
| `REGION_NAME` | Geospatial Poller | Display name of the active region | `backend/.env` | **Yes** | Default: `Andhra Pradesh` |
| `CORS_ORIGINS` | FastAPI Middleware | Allowed origins for web browser API requests | `backend/.env` | **Yes** | Default: `["http://localhost:3000"]` |
| `LLM_PROVIDER` | LLM Module | Specifies LLM provider | `backend/.env` | **Yes** | Set to `gemini` |
| `GEMINI_API_KEY` | Google AI Studio | API key for Gemini models | `backend/.env` | **Recommended** | [Google AI Studio](https://aistudio.google.com/apikey) (Free tier available) |
| `LLM_MODEL` | LLM Module | Specific Gemini model override (optional) | `backend/.env` | Optional | Leave blank; backend auto-probes the best available Flash model |
| `OPERATOR_TOKEN` | Auth / Admin | 64-char hex token for bootstrapping duty officers and scripts | `backend/.env` | Auto | Generated automatically by `stack.ps1` if left unset |
| `ENROLMENT_CODE` | Auth / Telemetry | 16-char token for legacy vehicle registration | `backend/.env` | Auto | Generated automatically by `stack.ps1` if left unset |
| `FIRMS_MAP_KEY` | NASA FIRMS | Key for real-time thermal/wildfire satellite feeds | `backend/.env` | Optional | [NASA Earthdata FIRMS](https://firms.modaps.eosdis.nasa.gov/api/map_key/) (Off if blank) |
| `TWILIO_ACCOUNT_SID` | Twilio SMS/WhatsApp | Account SID for driver SMS notifications | `backend/.env` | Optional | [Twilio Console](https://www.twilio.com/console) (Off if blank) |
| `TWILIO_AUTH_TOKEN` | Twilio SMS/WhatsApp | Auth token for WhatsApp webhook signature | `backend/.env` | Optional | [Twilio Console](https://www.twilio.com/console) (Off if blank) |
| `TWILIO_FROM_NUMBER` | Twilio SMS/WhatsApp | Sender phone number | `backend/.env` | Optional | [Twilio Console](https://www.twilio.com/console) (Off if blank) |
| `DRILL_SEND_MESSAGES`| Safety Flag | Guardrail preventing drills from sending real SMS/WhatsApp | `backend/.env` | Optional | Default: `false` (Never send real messages during test drills) |
| `LANGFUSE_PUBLIC_KEY`| Langfuse | Public key for LLM tracing and observability | `backend/.env` | Optional | [Langfuse Cloud](https://cloud.langfuse.com) (Off if blank) |
| `LANGFUSE_SECRET_KEY`| Langfuse | Secret key for Langfuse tracing | `backend/.env` | Optional | [Langfuse Cloud](https://cloud.langfuse.com) (Off if blank) |
| `LANGFUSE_HOST` | Langfuse | URL of Langfuse server | `backend/.env` | Optional | Default: `https://cloud.langfuse.com` |
| `SMTP_HOST` | Email Dispatcher | SMTP server hostname for password reset emails | `backend/.env` | Optional | Off if blank; duty officers can reset passwords via Team tab |
| `SMTP_PORT` | Email Dispatcher | SMTP server port | `backend/.env` | Optional | Default: `587` |
| `SMTP_USER` | Email Dispatcher | SMTP authentication username | `backend/.env` | Optional | Off if blank |
| `SMTP_PASSWORD` | Email Dispatcher | SMTP authentication password | `backend/.env` | Optional | Off if blank |
| `MAIL_FROM` | Email Dispatcher | Sender email address | `backend/.env` | Optional | e.g. `reliefroute@yourdomain.com` |
| `API_ORIGIN` | Next.js Rewrites | Backend address forwarded by Next.js in dev mode | `frontend/.env.local` | **Yes** | `http://127.0.0.1:8000` |
| `NEXT_PUBLIC_REGION_BBOX`| Frontend Map | Initial map viewport bounds matching backend | `frontend/.env.local` | **Yes** | `76.6,12.5,84.9,20.1` |
| `DB_HOST_PORT` | Docker Compose | Host port for PostgreSQL container | Root `.env` (optional) | Optional | Default is `55432` in `docker-compose.yml` |

---

## 2. In-Depth Variable Breakdown

### `GEMINI_API_KEY`
- **What it means:** The API key providing access to Google's Gemini models.
- **Why required:** ReliefRoute uses Gemini in the `Sentinel` agent (to interpret unstructured weather alerts and triage disaster severity), in the `Brief` agent (to draft concise situation reports for human commanders), and in the `Dispatcher` (to translate turn-by-turn route instructions into Telugu and Hindi for local drivers).
- **Files using it:** `backend/app/llm/factory.py`, `backend/app/llm/client.py`, `backend/app/core/settings_brain.py`.
- **How to obtain:**
  1. Visit [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey).
  2. Sign in with your Google account.
  3. Click **Create API key**.
  4. Copy the key.
- **Target file:** `backend/.env` as `GEMINI_API_KEY=AIzaSy...`

### `DATABASE_URL`
- **What it means:** PostgreSQL connection URI including username, password, host, port, and database name.
- **Why required:** All spatial tables (hazards, facilities, routes, vehicles), relational records (orders, users, stock), and LangGraph execution checkpoints are persisted in PostGIS.
- **Files using it:** `backend/app/core/db.py`, `backend/app/core/migrate.py`, `backend/app/core/config.py`.
- **Target file:** `backend/.env` (`postgresql://reliefroute:reliefroute@localhost:55432/reliefroute`).

### `REDIS_URL`
- **What it means:** Redis connection URI.
- **Why required:** Serves as the central asynchronous event stream (`Redis Streams`) linking data ingestion workers to the LangGraph brain worker and powering live Server-Sent Events (SSE) to the frontend.
- **Files using it:** `backend/app/core/bus.py`, `backend/app/core/config.py`.
- **Target file:** `backend/.env` (`redis://localhost:6380/0`).

### `VALHALLA_URL`
- **What it means:** Endpoint of the local Valhalla routing server container.
- **Why required:** Computes shortest-path driving routes and calculates polygon avoidance buffers to steer trucks around flood zones.
- **Files using it:** `backend/app/routing/client.py`, `backend/app/core/settings_brain.py`.
- **Target file:** `backend/.env` (`http://localhost:8002`).

### `OPERATOR_TOKEN` & `ENROLMENT_CODE`
- **What they mean:** Cryptographic master bearer tokens.
- **Why required:** The `OPERATOR_TOKEN` authorizes the initial setup of the first Duty Officer account and authenticates administrative automation scripts. The `ENROLMENT_CODE` authenticates vehicle telemetry registration.
- **Files using it:** `backend/app/core/auth.py`, `backend/app/core/security.py`, `backend/app/telemetry/registration.py`.
- **Target file:** `backend/.env`. (Can be left blank; `stack.ps1` will automatically generate random 64-character tokens on first startup if missing).

---

## 3. Configuration Audit Findings

1. **Frontend vs Backend Secret Isolation:**
   - Secrets (`GEMINI_API_KEY`, `DATABASE_URL`, `REDIS_URL`, `OPERATOR_TOKEN`, `TWILIO_*`, `SMTP_*`) are strictly contained within `backend/.env` and are never prefixed with `NEXT_PUBLIC_` or bundled into client code.
   - The frontend only contains `API_ORIGIN` (server-side Next.js rewrite rule) and `NEXT_PUBLIC_REGION_BBOX` (public map coordinates).
2. **Duplicate Variable Resolution:**
   - In upstream example templates (`env/brain.env.example` vs `env/senses.env.example`), both listed `DATABASE_URL` and `REDIS_URL` with slightly different ports (5432 vs 55432, 6379 vs 6380). 
   - **Resolution:** In our created `backend/.env`, we unified them to the correct local Docker mappings: `55432` for PostGIS and `6380` for Redis.
3. **No Hardcoded Credentials in Source Code:**
   - Codebase inspection confirmed that no real credentials or keys are hardcoded in application source code.
4. **Git Protection:**
   - `.gitignore` was audited and hardened with `*.env*` and `.env*` patterns to ensure no local credential file can ever be accidentally committed.

