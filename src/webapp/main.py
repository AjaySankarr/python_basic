from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html  # <--- 1. Import this

import webapp.models
from webapp.api.v1.router import api_router
from webapp.core.database import Base, engine
from webapp.core.rate_limiter import limiter

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded 
from slowapi.middleware import SlowAPIMiddleware

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     await engine.dispose()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

# 2. Disable default docs_url
app = FastAPI(
    title="College Management API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
)

# Rate Limiting Configuration
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,_rate_limit_exceeded_handler
)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


# 3. Add custom /docs route using Cloudflare CDNJS
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.17.14/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.17.14/swagger-ui.min.css",
    )


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}