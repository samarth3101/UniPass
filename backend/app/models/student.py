from sqlalchemy import Column, Integer, String
from app.db.base import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    prn = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    division = Column(String, nullable=True)