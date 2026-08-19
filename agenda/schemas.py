from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = Field(default="")
    status: Literal["pendiente", "completada"] = "pendiente"
    due_date: Optional[datetime] = Field(default_factory=datetime.now)

    @field_validator("title", "description", mode="before")
    @classmethod
    def clean_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("due_date", mode="before")
    @classmethod
    def parse_due_date(cls, value):
        if not value or (isinstance(value, str) and not value.strip()):
            return datetime.now()
        if isinstance(value, str):
            try:
                return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError("La fecha debe tener el formato YYYY-MM-DD HH:MM:SS")
        return value


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = Field(default=None)
    status: Optional[Literal["pendiente", "completada"]] = None
    due_date: Optional[datetime] = None

    @field_validator("title", "description", mode="before")
    @classmethod
    def clean_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("due_date", mode="before")
    @classmethod
    def parse_due_date(cls, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        if isinstance(value, str):
            try:
                return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError("La fecha debe tener el formato YYYY-MM-DD HH:MM:SS")
        return value