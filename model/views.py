from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from db import db_helper
from shema import UserShema

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/")
async def create(
    user: UserShema,
    session: AsyncSession = Depends(db_helper.session_dependency),
                 ):
    return await crud.create_user_db(user=user, session=session)

@router.get("/get")
async def get_users(session: AsyncSession = Depends(db_helper.session_dependency)):
    return await crud.get_users(session=session)