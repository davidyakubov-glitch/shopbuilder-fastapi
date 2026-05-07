import json
import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

base_dir = tempfile.gettempdir()
platform_db = os.path.join(base_dir, "shopbuilder_platform_test.db")
tenant_alpha_db = os.path.join(base_dir, "shopbuilder_tenant_alpha_test.db")
tenant_beta_db = os.path.join(base_dir, "shopbuilder_tenant_beta_test.db")

os.environ["APP_ENV"] = "test"
os.environ["APP_NAME"] = "ShopBuilder Test API"
os.environ["PLATFORM_DATABASE_URL"] = f"sqlite:///{platform_db}"
os.environ["TENANT_DATABASE_URLS"] = json.dumps(
    {
        "merchant_alpha": f"sqlite:///{tenant_alpha_db}",
        "merchant_beta": f"sqlite:///{tenant_beta_db}",
    }
)
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["JWT_SECRET_KEY"] = "test-access-secret-key-1234567890"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret-key-0987654321"
os.environ["WEBHOOK_SIGNING_SECRET"] = "test-webhook-secret-key-1234567890"
os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://localhost:8000"

from app.core.redis_client import get_redis_client
from app.database import create_selected_tables, platform_engine, tenant_engines
from app.main import app
from app.models import platform_tables, tenant_tables


@pytest.fixture(autouse=True)
def reset_databases():
    get_redis_client().flushall()
    SQLModel.metadata.drop_all(platform_engine, tables=platform_tables())
    for engine in tenant_engines.values():
        SQLModel.metadata.drop_all(engine, tables=tenant_tables())
    create_selected_tables()
    yield


@pytest.fixture
def client():
    return TestClient(app)
