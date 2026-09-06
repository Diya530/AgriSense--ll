# AgriSense — AI Smart Farming Advisor

AgriSense is an AI-powered farming assistant: a multilingual chatbot backed by
real weather data and a curated agricultural knowledge base, plus crop
recommendation, soil analysis, plant-health image diagnosis, an irrigation
advisor, and market price info.

**This is a stateless application: no database, no login, no server-side
storage.** The farmer profile lives entirely in the browser (`localStorage`);
the backend is a pure request/response API with no persistence layer at all.
This was a deliberate simplification — see Section 2 for the reasoning and
exactly what trade-offs it involves.

---

## 1. Honest status of this build

This codebase was written and verified in an environment with no internet
access, so nothing here has been run against real APIs end-to-end by me —
every external call (weather, geocoding, LLM, market) is real integration
code, verified by direct execution wherever the logic didn't require a live
network call (chat location-resolution, language priority, crop/soil
scoring, market data loading and search, memory-capping — all confirmed
correct by actually running them, not just reading the code). You are the
first to run the full stack together with real API keys.

**What's genuinely solid:**
- LLM provider abstraction (Gemini default, OpenAI/Groq/Ollama as drop-in
  alternates, automatic fallback chain — with the Ollama-masking bug fixed)
- Weather service with real API calls, in-memory caching, and a hard "never
  invent data" contract enforced in code
- RAG pipeline (ChromaDB, local embeddings, no extra API key needed) — a
  local file on disk, not a database service
- Chat orchestration implementing intent → tool call → RAG → LLM → response,
  with correct location-priority logic (explicit place named in a message
  always overrides the saved profile location, verified against the
  original spec's test cases)
- A complete React frontend covering every page, wired to the real API

**What's intentionally minimal:**
- Crop recommendation uses transparent range-based agronomic scoring, not a
  trained ML model (see Section 7 for why)
- Knowledge base is a handful of curated documents, not a large ICAR/FAO corpus
- Market prices are a small static demo dataset unless you configure a
  data.gov.in key
- No automated end-to-end run against real keys has happened yet (see above)

---

## 2. Why stateless, and what it means for you

**No login, no accounts, no database, no server-side history.** Every
request the frontend makes either needs no context at all (weather by
lat/lon, market search) or carries the farmer's profile as part of the
request body (chat, irrigation). The backend never looks anything up by
"who is this user" — there is no such concept server-side.

**What this buys you:**
- Zero setup: no database to install, configure, or migrate — `pip install
  -r requirements.txt` and you're running
- Nothing to lose: no accidentally-shared multi-user data, no auth bugs, no
  migration headaches
- Deploy the backend anywhere stateless containers are cheap/free (it holds
  no state between requests except an in-memory weather cache that's fine
  to lose on restart)

**What you give up, on purpose:**
- **No cross-device sync.** The farmer profile is saved in this browser's
  `localStorage` only. Open the app on a different device or browser and
  you'll see a blank profile — it doesn't follow you.
- **No persistent chat history.** Conversation memory lives in React state
  for the current browser tab. Refresh the page and the conversation
  restarts. Long conversations within a single session still get
  capped/summarized sensibly (see `app/services/memory_service.py`) — this
  only affects persistence *across* sessions, not memory *within* one.
- **No History page.** Past crop/soil/irrigation/plant-health results aren't
  saved anywhere — each analysis is a one-off request/response. (This page
  existed in an earlier version of this project and was removed along with
  the database.)
- **No multi-user support.** If you deploy this publicly, everyone who
  visits sees their *own* independent `localStorage` profile (that part is
  actually fine, since localStorage is per-browser) — but there's no way to
  share a farm's data between two people's devices, and no admin/account
  system of any kind.

**Adding a database back later, if you need it:** the architecture is
already shaped for this. `app/schemas/schemas.py`'s `FarmerProfileContext`
is the exact shape a `FarmerProfile` database model would have — you'd add
a database layer, an auth mechanism, and swap the frontend's
`localStorage`-reading (`utils/farmerProfile.js`) for API calls, without
needing to redesign the rest of the request/response contracts. The
now-deleted `models.py`/`database/db.py`/auth code from the previous
version of this project (SQLAlchemy + JWT) is a reasonable starting point
to resurrect if/when that's needed — check your version history if you
kept it, or ask for it to be rebuilt.

---

## 3. Architecture

```
Farmer message (+ farmer_profile from localStorage, + recent chat history from React state)
      ↓
Language detection (script-based + heuristics) + profile language priority
      ↓
Intent detection (weather / irrigation / plant health / general)
      ↓
   ┌──────────────┴──────────────┐
   │                             │
Needs live data?              General question
   │                             │
Weather API call            RAG retrieval (ChromaDB, local file index)
(OpenWeatherMap)                 │
   │                             │
Verified data or            Knowledge excerpts or
honest failure               "no match" signal
   │                             │
   └──────────────┬──────────────┘
                   ↓
   LLM (Gemini, with hard rules against inventing data)
                   ↓
            Verified response
```

No database touches this flow anywhere. The only server-side state is an
in-memory weather cache (a plain Python dict, reset on restart) that exists
purely to survive brief upstream API hiccups within a single run.

---

## 4. Tech stack

- **Backend:** FastAPI (stateless — no ORM, no database driver)
- **AI:** Gemini (default), pluggable OpenAI/Groq/Ollama
- **Weather:** OpenWeatherMap (default), Open-Meteo as a no-key alternative
- **RAG:** ChromaDB with local embeddings (a file on disk, not a DB service)
- **Frontend:** React 18, Vite, Tailwind CSS, React Router
- **Farmer profile & chat memory:** browser `localStorage` + React state —
  no backend involvement at all

---

## 5. Setup (Windows-first, with macOS/Linux equivalents)

### 5.1 Clone and enter the project

```bash
git clone <your-repo-url>
cd agrisense
```

### 5.2 Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
```
macOS/Linux: `source venv/bin/activate`

```bash
pip install -r requirements.txt
```

Copy the environment template and fill in your keys:

```powershell
copy .env.example .env
```
macOS/Linux: `cp .env.example .env`

Open `backend/.env` and set at minimum:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key-from-https://aistudio.google.com/app/apikey
WEATHER_PROVIDER=openweathermap
OPENWEATHERMAP_API_KEY=your-key-from-https://openweathermap.org/api
```

> **No API keys yet?** Set `WEATHER_PROVIDER=open-meteo` to skip the weather
> key entirely (free, no signup). Gemini's free tier is generous and takes
> about a minute to generate a key.

Run the backend:

```bash
uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000`. Check
`http://localhost:8000/api/health` — it reports `database_required: false`,
`stateless: true`, and whether your LLM/weather keys are picked up, without
leaking the key values.

### 5.3 Frontend

Open a **second terminal**:

```bash
cd frontend
npm install
npm run dev
```

Visit the URL Vite prints (usually `http://localhost:5173` — if that port's
busy, Vite picks the next one, e.g. `5174`; use whatever it actually prints).

### 5.4 First run

1. Open the app, click **Open AgriSense** — you're straight into the
   Dashboard, no account needed.
2. Go to **Farmer Profile** and set your location (type a place, or click
   "Use my location"), current crop, and soil type. This saves to your
   browser's `localStorage` immediately — no "saving..." spinner needed.
3. Go to **Chat** and ask *"What's the weather today?"* — this should hit
   the real weather API and the real LLM, using your saved location.

---

## 6. Testing

### 6.1 Automated backend tests (pure logic, no external calls, no database)

```bash
cd backend
pytest tests/ -v
```

These cover crop/soil scoring math, language/intent detection, weather
error handling (mocked HTTP), and the stateless conversation-memory capping
logic — none require API keys, network access, or a database.

### 6.2 Manual end-to-end checklist

- [ ] `GET /api/health` returns `stateless: true`, `database_required: false`,
  `llm_configured: true`, `weather_configured: true`
- [ ] Set a Farmer Profile, refresh the page — profile persists (localStorage)
- [ ] Open the app in a different browser (or incognito) — profile is
  **empty there**, confirming it's per-browser as expected, not shared
- [ ] Chatbot: "What's the weather today?" uses your saved location; "What's
  the weather in Kalka?" uses Kalka instead, for that one request only
- [ ] Crop Recommendation, Soil Analysis, Plant Health, Irrigation, Market
  all return results without any database running
- [ ] Refresh the Chat page mid-conversation — history resets (expected,
  documented trade-off)

---

## 7. Known limitations

- **Crop recommendation model:** transparent range-based agronomic scoring
  (`app/services/agriculture_service.py`), not a trained ML model — a
  deliberate choice to avoid confidently-wrong scores from a model trained
  on synthetic data. See in-file comments for how to swap in a real trained
  model later.
- **No persistence, by design** (see Section 2) — no cross-device sync, no
  chat history beyond the current tab, no analysis history page.
- **Market data:** a 14-entry static JSON demo dataset
  (`data/market/demo_prices.json`) unless you configure a free
  `DATA_GOV_IN_API_KEY`. Demo results are always clearly labeled as such.
- **Weather cache resets on backend restart** — it's an in-memory dict, not
  persisted, which is the intended trade-off for statelessness.
- **Plant disease detection** uses the configured vision-capable LLM rather
  than a dedicated trained CV model — reasonable for common, visually
  distinct issues, less reliable for subtle/early-stage disease.
- **i18n coverage:** navigation, page titles, and common labels are
  translated (en/hi/pa); deeper form field labels and longer body text are
  not yet — see `frontend/src/i18n/translations.js` for how to extend it.
- **No security audit beyond basics:** upload size/type validation, CORS
  allow-list. There's no auth to audit since there's no login — if you
  deploy this publicly, remember anyone with the link can see whatever
  their own browser's localStorage profile contains (which is only their
  own, but still worth knowing).

---

## 8. Project structure

```
agrisense/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, no DB init
│   │   ├── config.py                # Settings from .env (no DATABASE_URL)
│   │   ├── api/                     # Route handlers — all stateless
│   │   │   ├── chat.py              # farmer_profile + history in request body
│   │   │   ├── crop.py / soil.py / plant_health.py / irrigation.py / market.py
│   │   │   └── weather.py
│   │   ├── schemas/schemas.py       # FarmerProfileContext + request/response shapes
│   │   ├── services/
│   │   │   ├── llm_provider.py      # Abstract provider + fallback chain
│   │   │   ├── weather_service.py   # Real weather API + in-memory cache
│   │   │   ├── memory_service.py    # Stateless conversation-history capping
│   │   │   ├── market_demo_data.py  # Loads data/market/demo_prices.json
│   │   │   ├── agriculture_service.py
│   │   │   ├── plant_health_service.py
│   │   │   └── intent_service.py / geocoding_service.py
│   │   ├── rag/knowledge_base.py    # Local ChromaDB index (file, not a DB service)
│   │   └── utils/language.py, json_extract.py
│   ├── tests/
│   ├── requirements.txt             # No SQLAlchemy, no passlib/bcrypt/jose
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/                   # Landing, Dashboard, Chatbot, Weather,
│   │   │                            # CropRecommendation, SoilAnalysis,
│   │   │                            # PlantHealth, Irrigation, Market,
│   │   │                            # Profile, Settings
│   │   ├── components/              # Layout, Logo, Card, Feedback
│   │   ├── context/LanguageContext.jsx  # Reads profile language from localStorage
│   │   ├── utils/farmerProfile.js   # localStorage read/write — the whole "database"
│   │   └── api/                     # client.js, services.js
│   ├── package.json
│   └── vite.config.js
└── data/
    ├── knowledge/                   # RAG source documents (.md)
    └── market/demo_prices.json      # Static demo market data
```

---

## 9. Deployment notes

- **Backend:** any stateless ASGI host works well here precisely because
  there's no database to provision (Render, Railway, Fly.io, a bare VPS
  with `uvicorn`). Set `CORS_ORIGINS` to your frontend's real domain, and
  your API keys, as environment variables on the host — never commit a
  real `.env`.
- **Frontend:** `npm run build` → deploy `frontend/dist/` as a static site
  (Vercel, Netlify, or served by any static host). Since the dev-server
  proxy (`vite.config.js`) only works locally, set an API base URL for
  production — see `frontend/src/api/client.js`, change `baseURL: '/api'`
  to read from an environment variable pointing at your deployed backend.
- **No volume/disk persistence needed** for farmer data (it's client-side),
  though the RAG vector store (`backend/vector_store/`) is rebuilt fresh
  from `data/knowledge/*.md` on every startup, so it doesn't need to persist
  either — one less thing to worry about in a stateless deployment.

---

## 10. Troubleshooting

| Symptom | Likely cause |
|---|---|
| Chatbot says "AI assistant is temporarily unavailable" | Missing/invalid LLM API key, or the model name is deprecated — check `/api/health` and your backend terminal logs (errors are logged there) |
| Weather answers say "temporarily unavailable" | Missing/invalid `OPENWEATHERMAP_API_KEY`, or try `WEATHER_PROVIDER=open-meteo` |
| Farmer profile looks empty after opening the app | Expected on first visit, or in a different browser/incognito — it's per-browser localStorage, not synced |
| Chat conversation disappeared | Expected after a page refresh — conversation memory isn't persisted (see Section 2) |
| Market page shows "Demo / Sample Data" | Expected unless you've configured `DATA_GOV_IN_API_KEY` — this is the intended honest-labeling behavior, not a bug |
| Frontend can't reach backend | Confirm backend is running on port 8000, and check which port Vite actually printed (it may not be 5173 if that port was already in use) |
