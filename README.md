# Mycelium Webhook Hub

A simple, fast webhook receiver for GitHub events built with FastAPI and PostgreSQL.

I built this to learn more about async Python and how to properly validate webhook signatures. The whole thing is dockerized so it's easy to spin up and test without needing to configure a local database.

## How to run it

You just need Docker installed.

1. Clone the repo
2. Run `docker compose up --build`

This will:
- Start a Postgres database
- Run Alembic migrations automatically
- Start the FastAPI server on port 8000

## Testing locally

You can test the endpoint without setting up a real GitHub webhook or a tunneling service. I pre-calculated a signature for a test payload using the dummy secret in the docker-compose file.

Run this in another terminal:

**Mac/Linux (Bash/Zsh):**
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -H "X-GitHub-Delivery: test-123" \
  -H "X-Hub-Signature-256: sha256=74ba25a76edf3da29d88cc00b987247117890cbbc43bfeb30e2595c9f4f4ded9" \
  -d '{"zen": "Non-blocking is better than blocking."}'
```

**Windows (PowerShell):**
```powershell
$headers = @{
    "Content-Type" = "application/json"
    "X-GitHub-Event" = "ping"
    "X-GitHub-Delivery" = "test-123"
    "X-Hub-Signature-256" = "sha256=74ba25a76edf3da29d88cc00b987247117890cbbc43bfeb30e2595c9f4f4ded9"
}
$body = '{"zen": "Non-blocking is better than blocking."}'
Invoke-RestMethod -Uri "http://localhost:8000/webhook" -Method POST -Headers $headers -Body $body
```

You should get a `{"status": "received"}` response back.

## Tech stack
- FastAPI
- PostgreSQL + asyncpg
- SQLAlchemy + Alembic
- uv (for fast dependency management)
- Docker
