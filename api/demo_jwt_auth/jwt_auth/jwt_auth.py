from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import InvalidTokenError


from db import db_helper
from .token_info import TokenInfo
from shema import UserShema
from model import crud
from api.auth import utils

router = APIRouter(prefix="/auth", tags=["Auntification"])

http_hearer = HTTPBearer()

async def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(db_helper.session_dependency)
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    user = await crud.get_user_by_username(session, username)
    if not user:
        raise unauthed_exc
    
    if not utils.validate_password(
        password=password,
        hashed_password=user.password,
    ):
        raise unauthed_exc
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactiva",
        )
    return user

def get_current_token_payload(
    cred: HTTPAuthorizationCredentials = Depends(http_hearer)
) -> UserShema:
    token = cred.credentials
    
    try:
        payload = utils.decode_jwt(
            token=token
        )
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error {e}",
        )
    return payload

async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> UserShema:
    
    username: str | None = payload.get("sub")
    user = await crud.get_user_by_username(session, username)
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid not found",
    )

async def get_curent_active_from_user(
    user: UserShema = Depends(get_current_auth_user)
):
    print(f"DEBUG user.active = {user.active}")
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="user inactive"
    )


@router.post("/loggin", response_model=TokenInfo)
async def auth_user_with_db(
    user: UserShema = Depends(validate_auth_user)):
    
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email,
    } 
    token = utils.encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer",
    ) 
    
@router.get("/user/me")
async def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserShema = Depends(get_curent_active_from_user),
):
    iat = payload.get("iat")
    return {
        "username": user.username,
        "email": user.email,
        "loggin at": iat,
    }