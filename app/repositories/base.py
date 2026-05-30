from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from app.database.db import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: str) -> Optional[ModelType]:
        """Fetch a record by its primary key ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Fetch all records with optional offset and limit."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj: ModelType) -> ModelType:
        """Persist a new entity in the database."""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self) -> None:
        """Commit changes on an attached, modified entity."""
        self.db.commit()

    def delete(self, obj: ModelType) -> None:
        """Delete an entity from the database."""
        self.db.delete(obj)
        self.db.commit()
