#!/bin/sh
set -e

# Wait for PostgreSQL to become reachable
if [ -n "$DATABASE_URL" ]; then
  echo "Checking database connectivity..."
  python - <<'EOF'
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

db_url = os.environ.get("DATABASE_URL", "")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

async def wait_for_db():
    engine = create_async_engine(db_url)
    for attempt in range(1, 31):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print("Database is ready!")
            await engine.dispose()
            return
        except Exception as err:
            print(f"Waiting for database (attempt {attempt}/30)... {err}")
            await asyncio.sleep(2)
    print("Timed out waiting for database.")
    sys.exit(1)

if db_url:
    asyncio.run(wait_for_db())
EOF
fi

echo "Applying database migrations..."
alembic upgrade head

PORT_TO_USE="${PORT:-8000}"
echo "Starting server on port ${PORT_TO_USE}..."
exec uvicorn webapp.main:app --host 0.0.0.0 --port "$PORT_TO_USE"

