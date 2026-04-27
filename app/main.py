from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, customers, orders, products, stores, themes, variants, webhooks
from app.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import RequestContextMiddleware
from app.database import create_selected_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_selected_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

register_exception_handlers(app)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(stores.router, prefix="/api/v1")
app.include_router(themes.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(variants.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
