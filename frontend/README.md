# Portfolio Rebalancer Frontend

This directory contains the React and TypeScript frontend for the Portfolio Rebalancer MVP. It provides the authenticated portfolio dashboard, holdings, transactions, target allocation, rebalance review, profile, and admin asset screens.

## Technology

- React
- TypeScript
- Vite
- ESLint

## Prerequisites

- Node.js and npm
- A running Portfolio Rebalancer backend at `http://localhost:8000` by default

## Configuration

Create `frontend/.env` when a different backend URL is required:

```text
VITE_API_BASE_URL=http://localhost:8000
```

The repository includes `.env.example` as a placeholder configuration. Do not commit local `.env` files.

## Install dependencies

```powershell
npm install
```

## Start the development server

```powershell
npm run dev
```

Vite serves the frontend at `http://localhost:5173` by default.

## Build for production

```powershell
npm run build
```

## Run lint

```powershell
npm run lint
```

The frontend expects the FastAPI backend to be running separately. The repository's Docker Compose configuration starts PostgreSQL and the backend, but not the frontend.
