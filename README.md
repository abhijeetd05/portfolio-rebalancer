# Portfolio Rebalancer

Portfolio Rebalancer is an MVP web application for tracking investment portfolios, comparing current allocations with target allocations, and generating recommendation-only rebalance reviews.

## Problem statement

Portfolio information is often split across spreadsheets and broker screens. That makes it difficult to maintain holdings, understand current allocation, compare it with an intended allocation, and identify where a portfolio is drifting.

## Solution

The application combines portfolio data, holdings, transactions, target allocations, market prices, and optional foreign-exchange conversion into one authenticated workspace. A dashboard summarizes the portfolio, while the rebalance engine produces a persisted review without executing trades.

## Key features

- **Authentication:** Registration, login, JWT-protected API access, logout, and read-only profile information.
- **Multiple portfolios:** Create, list, select, and delete user-owned portfolios with a base currency.
- **Admin asset management:** Authorized administrators can manage available assets and their external mappings.
- **Yahoo Finance asset mapping:** Search and resolve Yahoo Finance instruments into server-generated application assets.
- **Holdings management:** Add, view, update, and delete portfolio holdings.
- **Current market prices:** Retrieve the latest available price through the configured market-data provider.
- **Transactions:** Record and view BUY and SELL transactions with units, price, fees, dates, and notes.
- **Target allocation:** Create, update, list, and delete target percentages with portfolio total validation.
- **FX conversion:** Convert supported mixed-currency holding values into the portfolio base currency.
- **Dashboard:** View portfolio value, current allocation, targets, visual allocation comparisons, and the latest rebalance review.
- **Rebalancing recommendations:** Generate and review recommendation-only BUY/SELL actions and rebalance history.
- **Profile:** View the authenticated account details.

## Tech stack

| Area | Technology |
| --- | --- |
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| Persistence | PostgreSQL, SQLAlchemy 2.0 |
| Migrations | Alembic |
| Authentication | JWT, `pwdlib` password hashing |
| External data | Yahoo Finance chart endpoints for prices and FX |
| Local orchestration | Docker Compose |

## Architecture

The main request path is:

```text
React/Vite frontend
        |
        v
FastAPI API routes
        |
        v
Application services
        |
        v
Repositories and market-data providers
        |
        v
PostgreSQL
```

Portfolio ownership, validation, valuation, target allocation, and rebalance behavior are implemented in services. Repositories encapsulate database access. External market and FX requests are made through the market-data provider layer; prices and FX rates can be cached in PostgreSQL.

## Core application flow

```text
Registration
  -> Portfolio
  -> Assets
  -> Holdings
  -> Transactions
  -> Target Allocation
  -> Dashboard
  -> Rebalance review
```

## Market data

Assets can contain an external provider and external asset identifier, such as a Yahoo Finance ticker. The external provider retrieves the latest available Yahoo Finance chart price and records provider currency and timestamp in the price data.

The provider first checks persisted prices using the configured market-price cache window, which defaults to 300 seconds. New timestamps are persisted without intentionally duplicating the same cached observation.

If an asset has no usable mapping or no available price, valuation-dependent endpoints return an explicit market-data error rather than fabricating a price. The frontend presents an unavailable-valuation state.

## FX conversion

Holding values are calculated in the portfolio base currency. When a provider price uses another currency, the currency conversion service requests an FX rate from the same external market-data provider and caches the rate using the market-data cache configuration.

At minimum, the MVP supports INR and USD conversion, including inverse-pair lookup where available. If an FX rate cannot be obtained, valuation fails with a clear error. Rates are not fabricated, and provider prices remain stored in their original currencies.

## Asset classification

The canonical application asset types are:

- Equity
- Debt
- Precious Metal
- Crypto

Yahoo instrument metadata is mapped deterministically where the available type or category is sufficiently clear. Cryptocurrency instruments map to Crypto, money-market instruments map to Debt, and suitable equity instruments map to Equity. Mutual funds and ETFs are not blindly assigned to Equity: structured category metadata is preferred, and ambiguous or hybrid classifications require explicit confirmation. Existing asset identifiers are preserved when an asset is corrected.

## Admin functionality

Admin-only asset endpoints support creating, updating, listing, and deleting assets, including asset type, currency, symbol, active state, and external Yahoo mapping information. Non-admin users are denied access by the existing authorization checks.

## Rebalancing behavior

Rebalancing is recommendation-only. A review compares current allocation with target allocation and persists a rebalance event with generated actions for existing holdings.

Target asset classes without current holdings are treated as having 0% current allocation and are explained in the review. The system does not create fake holdings, assets, prices, transactions, or executable trades. A rebalance review can therefore identify missing target classes while keeping actionable recommendations limited to real holdings.

## MVP scope

This MVP covers authenticated portfolio tracking, allocation planning, market-price-backed valuation, supported FX conversion, and recommendation-only rebalancing.

The following are **not included**:

- Tax optimization
- Transaction-cost optimization
- Live trade execution
- Advanced risk optimization
- Unsupported financial predictions, returns, or market forecasts

## Project structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI routes
│   │   ├── core/                # configuration, database, security
│   │   ├── engine/              # allocation and rebalance calculations
│   │   ├── models/              # SQLAlchemy models
│   │   ├── providers/           # market-data providers
│   │   ├── repositories/        # database access
│   │   ├── schemas/             # Pydantic request/response models
│   │   └── services/            # application services
│   ├── migration/               # Alembic configuration and revisions
│   ├── tests/                   # test package
│   ├── test_phase_*.py           # phase validation scripts
│   ├── Dockerfile
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                 # API client modules
│   │   ├── components/          # shared layout components
│   │   └── pages/               # application screens
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
└── compose.yaml
```

## Prerequisites

- Docker Desktop with Docker Compose
- Python 3.11+ for local backend tooling
- Node.js and npm for the Vite frontend
- Network access to Yahoo Finance when external prices or FX rates are required

## Environment configuration

Do not commit real credentials or secrets. Use environment variables or a local, ignored `.env` file.

Backend settings include:

```text
APP_ENV=development
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:<port>/<database>
JWT_SECRET=<long-random-development-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
MARKET_PRICE_CACHE_SECONDS=300
```

The backend reads settings from its environment and its local `.env` file. The repository does not provide production secret management.

Frontend configuration is supplied through `frontend/.env`:

```text
VITE_API_BASE_URL=http://localhost:8000
```

## Docker/local development setup

### A. Docker backend and PostgreSQL

From the repository root:

```powershell
docker compose up --build -d
```

This starts PostgreSQL and the FastAPI backend. Compose does **not** start the frontend.

Check service status:

```powershell
docker compose ps
```

Stop the services:

```powershell
docker compose down
```

### B. Frontend Vite development server

In a second terminal:

```powershell
cd frontend
npm install
npm.cmd run dev
```

The frontend is normally available at `http://localhost:5173`.

Run only one backend server on port 8000. Do not start a host Uvicorn process while the Docker backend is running on the same port; competing backend processes can produce inconsistent code or database behavior.

## Database migrations

The backend uses Alembic. With the Docker backend and database running:

```powershell
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current
docker compose exec backend alembic heads
```

Run migrations against the same database used by the application. A host Alembic command pointed at a different local database does not validate the Docker database.

## Frontend development setup

```powershell
cd frontend
npm install
npm.cmd run dev
```

Production build:

```powershell
npm.cmd run build
```

Lint:

```powershell
npm.cmd run lint
```

## API documentation

When the backend is running, interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

The health response is available at `http://localhost:8000/`.

## Validation and testing commands

Frontend validation:

```powershell
cd frontend
npm.cmd run lint
npm.cmd run build
```

Backend compilation/import validation:

```powershell
cd backend
python -m compileall -q app migration
python -c "from app.main import app; print(len(app.routes))"
```

The repository includes phase-specific validation scripts under `backend/test_phase_*.py`. They are historical/manual phase validations rather than a single configured automated test command. Run them only with the required backend environment and database available. A pytest command is not guaranteed by the current dependency configuration.

## Known limitations

- Market and FX availability depends on Yahoo Finance network responses and provider metadata.
- The MVP officially supports INR and USD FX conversion; broader currency coverage is not guaranteed.
- Ambiguous Yahoo instrument classifications require explicit user or admin confirmation.
- Compose is intended for local development, not production deployment.
- The frontend is not containerized by the current Compose file.
- Market prices and FX rates are cached; they are not guaranteed to be tick-by-tick live quotes.
- Rebalancing generates recommendations only and does not execute trades.
- There is no automated production deployment, monitoring, backup, or secret-management configuration.

## Security considerations

- Keep `.env` files, database credentials, JWT secrets, and local database files out of version control.
- Use a strong, unique JWT secret outside local development.
- Run migrations and the application against the intended database; do not mix host and Docker services accidentally.
- Ownership checks protect user portfolios and related resources.
- Admin asset endpoints require admin authorization.
- Passwords are hashed by the backend and are not returned by the API.
- The frontend stores the access token in browser local storage; deployment environments should assess the associated XSS and browser-storage risks.
- This project has not been hardened or documented as a production deployment.

## Future improvements

Potential future work includes stronger automated test execution, production secret management, containerized frontend deployment, expanded provider and currency support, improved operational observability, backups, and more sophisticated risk-aware planning. These are outside the current MVP scope.

## License

Portfolio Rebalancer is licensed under the [MIT License](LICENSE).

You are free to use, modify, and distribute this project under the terms of the license.
