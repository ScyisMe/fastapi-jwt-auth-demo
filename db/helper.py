from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator

from core import setting

class DataBase:
    def __init__(self, url: str, echo: bool = True):
        self.async_engine = create_async_engine(
            url=url,
            echo=echo,
        )

        self.async_factory = async_sessionmaker(
            bind=self.async_engine,
            autoflush=False,
            expire_on_commit=False,
            autocommit=False,
            )
    
    async def session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_factory() as session:
            yield session
            

db_helper = DataBase(
    url=setting.db.url,
    echo=setting.db.echo,
)
        