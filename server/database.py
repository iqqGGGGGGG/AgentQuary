from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import settings

engine = create_async_engine(settings.db_url, echo=False, pool_pre_ping=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def _migrate_columns(conn, metadata):
    from sqlalchemy import inspect as sa_inspect

    def _check_and_add(sync_conn):
        insp = sa_inspect(sync_conn)
        for table_name, table in metadata.tables.items():
            if table_name not in insp.get_table_names():
                continue
            existing_cols = {col["name"] for col in insp.get_columns(table_name)}
            for col in table.columns:
                if col.name not in existing_cols:
                    col_type = col.type.compile(dialect=engine.dialect)
                    nullable = "NULL" if col.nullable else "NOT NULL"
                    default = ""
                    if col.server_default is not None:
                        default = f" DEFAULT {col.server_default.arg}"
                    sync_conn.execute(text(
                        f"ALTER TABLE {table_name} ADD COLUMN {col.name} {col_type} {nullable}{default}"
                    ))

    await conn.run_sync(_check_and_add)


async def init_db():
    import models.orm  # noqa: F401 — ensure models are registered on Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _migrate_columns(conn, Base.metadata)

    async with async_session() as session:
        from services.achievements import seed_achievements
        await seed_achievements(session)


async def get_db():
    async with async_session() as session:
        yield session
