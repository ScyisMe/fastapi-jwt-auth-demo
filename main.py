import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager


from db import db_helper
from core import Base
from model.views import router
from api.demo_jwt_auth.jwt_auth import auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await db_helper.async_engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(router)
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)