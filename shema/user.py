from pydantic import BaseModel, EmailStr, ConfigDict

class UserShema(BaseModel):
    model_config =  ConfigDict(strict=True)
    
    username: str
    password: bytes | str
    email: EmailStr
    active: bool = True