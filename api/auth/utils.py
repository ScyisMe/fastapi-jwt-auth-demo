import jwt
import bcrypt

from datetime import datetime, timedelta, timezone

from core.config import setting

def encode_jwt(
    paload: dict,
    key: str = setting.auth_jwt.private_key_path.read_text(),
    algorithm: str = setting.auth_jwt.algorithm,
    expire_timedelta: timedelta | None = None,
    expire_minutes: int = setting.auth_jwt.access_token_expire_minutes,

):
    to_encode = paload.copy()
    now = datetime.now(tz=timezone.utc)
    
    expire = now + (expire_timedelta if expire_timedelta else  timedelta(minutes=expire_minutes))
    
    to_encode.update(
        exp=expire,
        iat=now,
    )
    
    encoded = jwt.encode(
        to_encode,
        key,
        algorithm=algorithm,
    )
    return encoded
    

def hash_password(
    password: str
) -> bytes:
    salt = bcrypt.gensalt()
    pmd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pmd_bytes, salt)

def decode_jwt(
    token: str | bytes,
    public_key: str = setting.auth_jwt.public_key_path.read_text(),
    algorithm: str = setting.auth_jwt.algorithm,
):
    decode = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decode

def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )