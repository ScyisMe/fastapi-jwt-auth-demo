from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

class Base(DeclarativeBase):
    __abstract__ = True
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f'{cls.__name__.lower()}s'
    
    def __repr__(self):
        colunms = [f"{col.name}={getattr(self, col.name)!r}" for col in self.__table__.columns]
        return f"<{self.__class__.__name__}({', '.join(colunms)})>"
    
    id: Mapped[int] = mapped_column(primary_key=True)