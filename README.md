# SafePassage (ReliefRoute)

> **Autonomous, Resilient Disaster Relief Supply Chain & Multi-Agent Routing System**  
> Watches live disaster alerts across Andhra Pradesh, determines relief demand from Census populations, matches inventory against real government stock, calculates safe road routes avoiding hazard polygons, and dispatches them under human supervision.

[![Next.js 16](https://img.shields.io/badge/Frontend-Next.js%2016%20%7C%20React%2019-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostGIS](https://img.shields.io/badge/Database-PostgreSQL%2016%20%7C%20PostGIS-336791?logo=postgresql)](https://postgis.net/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini%202.5%20%7C%20LangGraph-4285F4?logo=google)](https://aistudio.google.com/)
[![Netlify](https://img.shields.io/badge/Deploy-Netlify%20Frontend-00C7B7?logo=netlify)](https://www.netlify.com/)

---

![Operations Dashboard](docs/images/dashboard.png)

---

## Core Philosophy: LLMs Reason, Solvers Compute

Disaster relief operations require mathematical certainty. In SafePassage:
- **LLMs (Google Gemini 2.5 + LangGraph)** triage incoming hazard alerts, generate situation briefs for duty officers, verify rationale, and translate multilingual turn-by-turn guidance for drivers in Telugu and English.
- **Deterministic Solvers (Google OR-Tools & Shapely)** compute logistics, solve Vehicle Routing Problems (VRP), and guarantee that truck paths maintain strict spatial clearance from dynamic hazard boundaries.
- **The LLM never hallucinates a coordinate, distance, stock figure, or route.**

---

## System Architecture

```mermaid
flowchart TD
    subgraph LiveSources["1. Real-Time Data Sources (Senses)"]
        S1["Andhra Pradesh AePDS (Live Ration Stock)"]
        S2["NASA FIRMS (Thermal Wildfire Feeds)"]
        S3["GDACS (UN Global Cyclone & Flood Alerts)"]
        S4["Open-Meteo (IMD-Classified Rainfall Forecasts)"]
        S5["NDMA SACHET (CAP Disaster Bulletins)"]
        S6["OpenStreetMap (Populated Places & Relief Facilities)"]
    end

    subgraph IngestionEngine["2. Ingestion & Health Engine"]
        Poller["Deterministic Ingestion Worker"]
        Breaker["Circuit Breaker with Exponential Backoff"]
        SeedGen["Automated Seed & Fallback Engine"]
    end

    subgraph CoreStorage["3. Core Stores"]
        DB[("PostgreSQL 16 + PostGIS")]
        RedisStream{{"Redis Streams (Event Bus & Queues)"}}
    end

    subgraph BrainAgents["4. Brain Engine (LangGraph Multi-Agent)"]
        Sentinel["Sentinel Agent (Triage & Threat Detection)"]
        Needs["Needs Assessor (Sphere Standards + Census Population)"]
        Procure["Procurement Agent (PDS Fair-Price Shop Matching)"]
        VRP["Route Planner (OR-Tools VRP + Valhalla Road Graph)"]
        Critic["Critic Agent (Multi-Pass Safety Verification)"]
        Gate{{"Human-in-the-Loop Approval Gate"}}
        Dispatch["Dispatcher Agent (PO PDFs & Bilingual Instructions)"]
        Monitor["Closed-Loop Route Monitor (GPS Drift & Hazard Intersection)"]
    end

    subgraph PresentationLayer["5. Unified Web Interface (Netlify)"]
        OpsDash["Command Center & Source Health Dashboard"]
        DriverApp["Driver Progressive Web App (PWA)"]
        SupplierPortal["Supplier Portal & Stock Reporting"]
    end

    S1 & S2 & S3 & S4 & S5 & S6 --> Poller
    Poller <--> Breaker
    Poller <--> SeedGen
    Poller -->|Upsert GeoJSON & Freshness| DB
    Poller -->|Publish Events| RedisStream

    RedisStream --> Sentinel --> Needs --> Procure --> VRP --> Critic --> Gate
    Gate -->|Approved by Officer| Dispatch
    Dispatch --> DB
    Dispatch --> DriverApp
    Monitor -->|Route Deviation Detected| Needs

    DB <--> OpsDash
    DB <--> DriverApp
    DB <--> SupplierPortal
```

---

## Multi-Agent Decision Pipeline (The Brain)

```mermaid
stateDiagram-v2
    [*] --> Sentinel: Hazard alert arrives
    Sentinel --> Needs: Severe alert covers settlement
    Sentinel --> [*]: Sub-threshold / maritime alert
    Needs --> Procurement: Relief targets calculated (Food/Water/Shelter)
    Procurement --> RoutePlanner: Stock matched from mandal FPS godowns
    RoutePlanner --> Critic: VRP wave paths generated avoiding hazard polygons
    Critic --> RoutePlanner: Rejection (hazard clearance violation)
    Critic --> HumanApproval: Route verified safe
    HumanApproval --> Dispatcher: Duty Officer approves dispatch
    HumanApproval --> Needs: Officer requests adjustment
    Dispatcher --> RouteMonitoring: Dispatched to driver PWA with PDF orders
    RouteMonitoring --> Replanning: Driver GPS drifts or hazard spreads
    Replanning --> Needs: Autonomous closed-loop replan
    RouteMonitoring --> [*]: Delivery confirmed at relief camp
```

1. **Sentinel Agent**: Filters national feeds for Andhra Pradesh. If a severe hazard intersects a settlement, it triggers plan generation.
2. **Needs Assessor**: Intersects hazard footprint with Census 2011 population data to compute nutritional and survival requirements (Sphere standards: 2.1 kg rice, 0.4 kg pulses, 3L water/person/day).
3. **Procurement Agent**: Resolves stock against live Andhra Pradesh Civil Supplies (AePDS) fair-price shops across all 684 mandals.
4. **VRP Route Planner**: Solves capacitated vehicle pickups and deliveries through Google OR-Tools and Valhalla turn-by-turn routing around dynamic hazard polygons.
5. **Critic Agent**: Performs independent spatial intersection tests between routes and expanding hazard zones. Rejects any route infringing on the safety buffer up to 3 times before escalation.
6. **Human Approval Gate**: Zero high-stakes dispatches occur without explicit duty officer sign-off.
7. **Dispatcher Agent**: Produces tamper-evident purchase order PDFs, notifies drivers, and translates instructions into Telugu and English.
8. **Route Monitor**: Ingests high-frequency GPS fixes from driver phones. If road conditions deteriorate or a truck deviates, it triggers autonomous replanning.

---

## Live Data Sources & Health Monitoring

SafePassage features dynamic health monitoring with automatic recovery and zero synthetic fallbacks:

| Data Source | Provider | Frequency | Health Metric | Resilience & Fallback |
|---|---|---|---|---|
| **AePDS Ration Stock** | Andhra Pradesh Civil Supplies ePoS Portal | 24 hours | Closing balance of Rice & Pulses across all Fair Price Shops | Match against 684 OSM mandal boundaries; per-commodity retry |
| **NASA FIRMS Fires** | NASA VIIRS Satellite | 3 hours | Thermal active fire hotspots (FRP & confidence) | Bounds clipped to Andhra Pradesh region |
| **GDACS Global Alerts** | UN / European Commission | 1 hour | Tropical cyclone tracks, storm surge, flood alerts | National feed ingestion with polygon extraction |
| **Open-Meteo Forecast** | DWD / ECMWF / GFS Models | 6 hours | 0.5° spatial rainfall grid classified into IMD categories | IMD rainfall thresholds (Heavy, Very Heavy, Extreme) |
| **OpenStreetMap Places** | OpenStreetMap Community | 30 days | Settlements, cities, towns, and Census 2011 population | Built-in offline GeoJSON sequence bootstrap |
| **OpenStreetMap Facilities** | Overpass API | 3 days | Hospitals, schools, warehouses, fuel depots, shelters | Adaptive circuit breaker (60s backoff) + offline extract fallback |
| **NDMA SACHET** | National Disaster Management Authority | 2 minutes | Common Alerting Protocol (CAP) bulletins | Name normalization fallback to OSM admin boundaries |

---

## Deployment Architecture (Netlify + Cloud Backend)

SafePassage is designed for split deployment:
- **Frontend**: Hosted on **Netlify** (Next.js 16 with Turbopack, App Router, first-party cookie proxying).
- **Backend API & Workers**: Hosted on **Render** (or any Ubuntu Cloud VPS).
- **Database**: Managed **PostgreSQL 16 + PostGIS** (Supabase or Render).
- **Event Bus**: Managed **Redis** (Upstash or Render).

```mermaid
flowchart LR
    Client["User Browser / Mobile PWA"] -->|HTTPS| Netlify["Netlify CDN (Frontend)"]
    Netlify -->|"/api/* (Proxy Rewrite)"| Backend["Backend API (FastAPI)"]
    Netlify -->|"Static Assets & Pages"| Cache["Next.js Edge Cache"]
    Backend <--> Supabase[("Supabase (PostgreSQL + PostGIS)")]
    Backend <--> Upstash[("Upstash (Redis Streams)")]
    Workers["Background Ingestion & AI Workers"] <--> Supabase
    Workers <--> Upstash
```

### 1. Backend Deployment (Render or VPS)

1. Connect your repository to Render using **Blueprint** (`render.yaml`).
2. Supply environment variables:
   - `DATABASE_URL`: Your PostgreSQL + PostGIS connection string (e.g. from Supabase).
   - `REDIS_URL`: Your Redis connection string (e.g. from Upstash).
   - `GEMINI_API_KEY`: Your Google Gemini API key from AI Studio.
3. Apply the blueprint. Render starts `reliefroute-api`, `reliefroute-ingestion`, and `reliefroute-brain`.

### 2. Frontend Deployment (Netlify)

1. In Netlify, click **Add new site** → **Import an existing project** from GitHub.
2. Select repository: `SafePassage`.
3. Set build configuration:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/.next`
4. Set environment variables in Netlify:
   - `API_ORIGIN`: `https://<YOUR-BACKEND-URL>` (without trailing slash)
   - `NEXT_PUBLIC_REGION_BBOX`: `76.6,12.5,84.9,20.1`
5. Configure API proxying in `netlify.toml`:
   ```toml
   [[redirects]]
     from = "/api/*"
     to = "https://<YOUR-BACKEND-URL>/api/:splat"
     status = 200
     force = true
   ```
6. Click **Deploy**. Netlify builds and hosts the application with zero CORS overhead.

---

## Local Development Quickstart

### Prerequisites
- Python 3.11 or 3.12
- Node.js 20 or 22
- Docker & Docker Compose

### 1. Start Infrastructure (PostGIS & Redis)
```powershell
docker compose up -d db redis
```

### 2. Set Up Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -e ..\contracts\python -r requirements\brain.txt -r requirements\senses.txt -r requirements\dev.txt

# Run migrations
python -m app.core.migrate

# Run one sync pass over all 6 data sources
python -m app.ingestion.worker --once

# Start API server
uvicorn app.main:app --reload --port 8000
```

### 3. Set Up Frontend
```powershell
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the live operations dashboard.

---

## Running Automated Tests

```powershell
cd backend

# Test resilience & circuit breaker backoff
pytest tests/brain/test_resilience.py

# Test data source health statuses (Operational, Stale, Paused, Never Synced)
pytest tests/senses/test_source_health_statuses.py

# Test live data source parsers
pytest tests/senses/test_other_sources.py tests/senses/test_aepds.py
```

---

## License

This project is licensed under the Apache 2.0 License.
