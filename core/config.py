from pydantic import BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / 'db.sqlite3'

class DbSetting(BaseModel):
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    echo: bool = True
    
class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "cert" / "private_key.pem"
    public_key_path: Path = BASE_DIR / "cert" / "public_key.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 3
    refresh_token_expire_days: int = 15

class Setting(BaseModel):
    
    db: DbSetting = DbSetting()
    
    auth_jwt: AuthJWT = AuthJWT()
    

setting = Setting()