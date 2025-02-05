from pydantic import BaseModel, field_validator
from typing import Optional

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: Optional[bool] = False

    @field_validator('title')
    def validate_title(cls, value):
        if len(value) < 3:
            raise ValueError("Title must be at least 3 characters long.")
        return value

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

    @field_validator('completed')
    def validate_completed(cls, value):
        if value is not None and not isinstance(value, bool):
            raise ValueError("Completed must be a boolean value.")
        return value

class TodoResponse(TodoCreate):
    id: int
    owner_id: int  # Add owner_id

    class Config:
        orm_mode = True
