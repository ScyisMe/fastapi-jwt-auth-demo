from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from datetime import timedelta

from model.crud import get_user_by_username
from db.helper import db_helper
from core.config import setting
from .token_info import TYPE_TOKEN_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from api.auth import utils as auth_utils

async def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = setting.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) ->str:
    jwt_payload = {TYPE_TOKEN_FIELD: token_type}
    jwt_payload.update(token_data)
    
    return auth_utils.encode_jwt(
        paload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )

async def create_access_jwt(
    username: str,
    session: AsyncSession,
):
    user = await get_user_by_username(username=username, session=session)
    
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email,
    } 
    return await create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=setting.auth_jwt.access_token_expire_minutes,
    )
    
async def create_refresh_token(
    username: str,
    session: AsyncSession,
):
    user = await get_user_by_username(username=username, session=session)
    
    jwt_payload = {
        "sub": user.username
    }
    return await create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=setting.auth_jwt.refresh_token_expire_days,
    )