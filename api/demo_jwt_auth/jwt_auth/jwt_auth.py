from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import InvalidTokenError

from .token_info import TYPE_TOKEN_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from db import db_helper
from .token_info import TokenInfo
from shema import UserShema
from model import crud
from api.auth import utils
from .helpers import create_access_jwt, create_refresh_token

http_hearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/auth", tags=["Auntification"], dependencies=[Depends(http_hearer)])

oauth2_barer = OAuth2PasswordBearer(tokenUrl="/auth/loggin")

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

def validate_auth_token_type(payload: dict, token_type: str):
    
    current_token_type = payload.get(TYPE_TOKEN_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"invalid token type {current_token_type!r} expected {token_type}",
    )

def get_current_token_payload(
    token: str = Depends(oauth2_barer)
) -> UserShema:
    
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

async def get_user_by_token_sub(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> UserShema:
    username: str | None = payload.get("sub")
    user = await crud.get_user_by_username(username=username, session=session)
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid not found",
    )

async def get_curent_active_from_user(
    user: UserShema = Depends(get_user_by_token_sub)
):
    print(f"DEBUG user.active = {user.active}")
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="user inactive"
    )

def get_auth_user_from_token_of_type(token_type: str):
    async def get_auth_user_from_token(
        payload: dict = Depends(get_current_token_payload),
        session: AsyncSession = Depends(db_helper.session_dependency),
    ) -> UserShema:
        validate_auth_token_type(payload, token_type)
        user = await get_user_by_token_sub(payload=payload, session=session)
        return user
    return get_auth_user_from_token

get_current_auth_user_access = get_auth_user_from_token_of_type(ACCESS_TOKEN_TYPE)
get_current_auth_user_refresh =  get_auth_user_from_token_of_type(REFRESH_TOKEN_TYPE)

@router.post("/loggin", response_model=TokenInfo)
async def auth_user_with_db(
    user: UserShema = Depends(validate_auth_user),
    session: AsyncSession = Depends(db_helper.session_dependency),
    ):
    
    access_token = await create_access_jwt(user.username, session)
    refresh_token = await create_refresh_token(user.username, session)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    ) 
    
@router.post(
    "/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True)
async def auth_refresh_jwt(
    user: UserShema = Depends(get_current_auth_user_refresh),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    access_token = await create_access_jwt(user.username, session)
    return TokenInfo(
        access_token=access_token,
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