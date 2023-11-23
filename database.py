from typing import AsyncGenerator
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


engine = create_async_engine("postgresql+asyncpg://admin:admin@db/db", pool_timeout=60)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class LineSymbolCounter(Base):
    __tablename__ = "linesymbolcounter"

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    title = Column(String)
    text = Column(String)
    value_count = Column(Integer)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
