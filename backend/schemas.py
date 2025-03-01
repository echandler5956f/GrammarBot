# backend/schemas.py

from pydantic import BaseModel

class CreateStudentRequest(BaseModel):
    name: str

class CreateStudentResponse(BaseModel):
    student_id: int
    name: str

class AnalyzeRequest(BaseModel):
    student_id: int
    text: str

class AnalyzeResponse(BaseModel):
    original_text: str
    corrected_text: str

    # errors is a list of objects with these fields
    class ErrorItem(BaseModel):
        original_span: str
        corrected_span: str
        error_type: str

    errors: list[ErrorItem]
