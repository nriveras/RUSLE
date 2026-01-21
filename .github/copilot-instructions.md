# RUSLE Project Copilot Instructions

## Project Structure & Architecture
The project applies the Revised Universal Soil Loss Equation (RUSLE) using Google Earth Engine (GEE). It is split into two distinct parts that share logic patterns but are structurally separate:
1.  **Web Application** (`app/`): A FastAPI application for production use.
    -   **Entry Points**: `run.py` (CLI wrapper), `app/main.py`.
    -   **Services** (`app/services/`): Encapsulate core logic. `gee_service.py` handles GEE auth; `rusle_calculator.py` implements the model.
    -   **Routers** (`app/routers/`): API endpoints.
2.  **Research Scripts** (`00_scripts/`): Standalone scripts and notebooks (`RUSLE.ipynb`) for analysis and algorithm development.

**Key Dependencies**: `uv` (manager), `earthengine-api`, `geemap`, `geopandas`, `fastapi`, `folium`.

## Developer Workflows
-   **Environment**: Dependencies are managed via `uv` in `pyproject.toml`.
    -   Install: `uv sync`
    -   Activate: `source .venv/bin/activate`
-   **Run Application**:
    -   Dev (reload): `python run.py --reload`
    -   Prod: `python run.py`
    -   Access: `http://localhost:8000/app`
-   **Google Earth Engine (GEE)**:
    -   Authentication is critical. Local dev requires `earthengine authenticate`.
    -   Containerized environments mount credentials from `~/.config/earthengine`.
    -   Initialization handles errors in `app/main.py` -> `initialize_earth_engine`.

## Conventions & Patterns
-   **Configuration**:
    -   Use `app/config.py` with `Pydantic` settings.
    -   Environment variables are prefixed with `RUSLE_` (e.g., `RUSLE_GEE_PROJECT`).
    -   Directory paths (uploads, outputs) are defined in settings.
-   **Service Logic**:
    -   `rusle_calculator.py` is the primary reference for app logic.
    -   **Note**: Logic in `app/services/` often mirrors `00_scripts/rusle_utils.py`. When updating algorithms, check both locations to maintain consistency if intended.
-   **GEE Usage**:
    -   Wrap GEE operations in functions within services.
    -   Handle `ee.EEException` explicitly.
    -   Use `initialize_earth_engine` from `app.services.gee_service`.

## Critical Files
-   `pyproject.toml`: Dependency source of truth.
-   `app/services/rusle_calculator.py`: Core RUSLE implementation (P-factors, equation logic).
-   `00_scripts/RUSLE.ipynb`: Interactive research workflow.
-   `docker-compose.yml`: Deployment context, showing volume mounts for data and creds.
