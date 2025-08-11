from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated
from sqlalchemy import select, Result

from api.auth import utils
from shema import UserShema
from model import UserOrm

async def create_user_db(
    user: UserShema,
    session: AsyncSession,
) -> UserOrm:
    hashed_password = utils.hash_password(user.password)
    user_data = user.model_dump()
    user_data["password"] = hashed_password
    
    user = UserOrm(**user_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user 

async def get_users( session: AsyncSession) -> list[UserOrm]:
    stmt = select(UserOrm).order_by(UserOrm.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return users

async def get_user(session: AsyncSession, user_id: int):
    return await session.get(UserOrm, user_id)

async def get_user_by_username(session: AsyncSession, username: str):
    stmt = select(UserOrm).filter(UserOrm.username == username)
    result = await session.execute(stmt)
    user = result.scalar()
    return user

