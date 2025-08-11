from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import text

from core import Base

class UserOrm(Base):
    
    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[bytes] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=True)
    active: Mapped[bool] = mapped_column(default=True, server_default=text('1'), nullable=False)