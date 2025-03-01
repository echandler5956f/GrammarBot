# backend/models.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # student's name or username

    # Relationship to the ErrorLog table
    errors = relationship("ErrorLog", back_populates="student")

class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    original_text = Column(String)
    corrected_text = Column(String)
    error_type = Column(String)
    original_span = Column(String)
    corrected_span = Column(String)

    student = relationship("Student", back_populates="errors")
