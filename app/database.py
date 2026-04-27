from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings


def _build_engine_kwargs(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {
            "echo": False,
            "connect_args": {"check_same_thread": False},
        }
    return {
        "echo": False,
        "pool_pre_ping": True,
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_timeout": settings.db_pool_timeout,
    }

platform_engine = create_engine(settings.platform_database_url, **_build_engine_kwargs(settings.platform_database_url))
tenant_engines = {
    tenant_key: create_engine(database_url, **_build_engine_kwargs(database_url))
    for tenant_key, database_url in settings.parsed_tenant_database_urls.items()
}


def get_platform_session() -> Generator[Session, None, None]:
    with Session(platform_engine) as session:
        yield session


def get_tenant_session(tenant_key: str) -> Session:
    engine = tenant_engines.get(tenant_key)
    if engine is None:
        raise ValueError(f"Unknown tenant key: {tenant_key}")
    return Session(engine)


def create_selected_tables() -> None:
    from app.models import platform_tables, tenant_tables

    SQLModel.metadata.create_all(platform_engine, tables=platform_tables())
    for engine in tenant_engines.values():
        SQLModel.metadata.create_all(engine, tables=tenant_tables())
