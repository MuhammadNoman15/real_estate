# Real Estate Search MVP

FastAPI + Postgres/PostGIS MVP that answers 10 deterministic real-estate questions for a given property address in Metro Vancouver.

## Tech Stack
- FastAPI (Python)
- Postgres + PostGIS (local install)
- SQLAlchemy + GeoAlchemy2
- Simple static web UI (HTML/JS)

## MVP Scope (10 Queries)
The backend must return correct, structured answers for exactly these queries:
1. What is the BC Assessment value of [property address]?
2. What is the lot size and year built of [property address]?
3. What is the zoning designation of [property address]?
4. What schools are within 1 km of [property address]?
5. Which school catchment does [property address] belong to?
6. How far is the nearest bus stop or SkyTrain station from [property address]?
7. What is the demographic profile of the neighborhood around [property address]?
8. What parks or community centers are within walking distance of [property address]?
9. What is the average BC Assessment value of properties in the same neighborhood as [property address]?
10. Which transit routes connect this property to downtown Vancouver?

Deterministic database-first approach: the LLM (optional) only parses natural language into structured parameters and formats the results. All retrieval happens via SQL and PostGIS.

## Getting Started
1. Copy environment variables
   - Create a `.env` from `.env.example` and fill in values.

2. Install Postgres + PostGIS locally
   - Create a database named in `POSTGRES_DB` (default `realestate`).
   - Create the user and grant privileges (or use your own credentials and update `.env`).

3. Install backend
   - `python -m venv .venv && .venv/Scripts/activate` (Windows PowerShell)
   - `pip install -r requirements.txt`

4. Run API
   - `uvicorn app.main:app --reload`

5. Open UI
   - Open `ui/index.html` in a browser (or serve statically).

## Data Sources (MVP)
- BC Assessment (public search pages / downloadable open data where available)
- Municipal zoning shapefiles/open data portals
- Schools and catchments: provincial/municipal open datasets
- Transit (TransLink GTFS/static and Stops API); Google Maps for geocoding/routing if provided
- Parks/community centers: municipal open data
- Demographics: Statistics Canada census profiles by dissemination area

For MVP we will provide ETL scaffolding and minimal seed data to demonstrate end-to-end behavior for a few test addresses (e.g., 1366 Kings Avenue).

## Repository Layout (planned)
- `db/init/` — schema and seed SQL
- `app/` — FastAPI backend
- `ui/` — simple static client
- `etl/` — scripts/placeholders to load external datasets

## Environment Variables
See `.env.example`. API keys (e.g., Google, TransLink) can be added as provided.

## Testing the 10 Queries
We will expose a single `/query` endpoint plus typed endpoints for each of the 10 questions. The UI provides buttons/templates to test.

## License
Internal MVP for client demo.


