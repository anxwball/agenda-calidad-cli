# agenda/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

from agenda.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    status = Column(String, index=True)
    due_date = Column(DateTime, index=True)