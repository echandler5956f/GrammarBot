# backend/main.py

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from db import SessionLocal, engine
from models import Base, Student, ErrorLog
from ml import GrammarCorrector
from schemas import CreateStudentRequest, CreateStudentResponse, AnalyzeRequest, AnalyzeResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Grammar Bot API", version="1.0.0")

# ------------------------------------------------------------------
# 1. ADD CORS MIDDLEWARE (important if the frontend is served separately)
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain or local dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

grammar_corrector = GrammarCorrector()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------------------------------------------
# 2. CREATE STUDENT: accepts JSON body with {"name": "Alice"}
# ------------------------------------------------------------------
@app.post("/students", response_model=CreateStudentResponse)
def create_student(req: CreateStudentRequest, db: Session = Depends(get_db)):
    # Check if student name already exists
    existing = db.query(Student).filter(Student.name == req.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student with that name already exists.")

    student = Student(name=req.name)
    db.add(student)
    db.commit()
    db.refresh(student)
    return {"student_id": student.id, "name": student.name}

# ------------------------------------------------------------------
# 3. ANALYZE TEXT: accepts JSON body with {"student_id": 1, "text": "..."}
# ------------------------------------------------------------------
@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(req: AnalyzeRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == req.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    analysis = grammar_corrector.analyze_text(req.text)
    corrected = analysis["corrected_text"]
    errors = analysis["errors"]

    # store each error in DB
    for e in errors:
        error_log = ErrorLog(
            student_id=student.id,
            original_text=req.text,
            corrected_text=corrected,
            error_type=e["error_type"],
            original_span=e["original_span"],
            corrected_span=e["corrected_span"]
        )
        db.add(error_log)
    db.commit()

    return {
        "original_text": req.text,
        "corrected_text": corrected,
        "errors": errors
    }

# ------------------------------------------------------------------
# 4. GET STUDENT ERRORS
# ------------------------------------------------------------------
@app.get("/students/{student_id}/errors")
def get_student_errors(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    errors = db.query(ErrorLog).filter(ErrorLog.student_id == student_id).all()
    result = [
        {
            "id": e.id,
            "original_text": e.original_text,
            "corrected_text": e.corrected_text,
            "error_type": e.error_type,
            "original_span": e.original_span,
            "corrected_span": e.corrected_span
        }
        for e in errors
    ]
    return result

# ------------------------------------------------------------------
# 5. GET STUDENT FEEDBACK
# ------------------------------------------------------------------
@app.get("/students/{student_id}/feedback")
def get_student_feedback(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    errors = db.query(ErrorLog).filter(ErrorLog.student_id == student_id).all()
    if not errors:
        return {"feedback": "No errors recorded. Great job!"}

    freq_map = {}
    for e in errors:
        freq_map[e.error_type] = freq_map.get(e.error_type, 0) + 1

    sorted_errors = sorted(freq_map.items(), key=lambda x: x[1], reverse=True)
    top_error, count = sorted_errors[0]

    feedback_str = f"Your most frequent error type is '{top_error}', occurring {count} times.\n"
    feedback_str += "Here are some suggestions:\n"

    if top_error == "Spelling Error":
        feedback_str += "- Pay attention to commonly confused words.\n- Use a spell-check tool.\n"
    elif top_error == "Punctuation Error":
        feedback_str += "- Revisit punctuation rules (commas, periods, etc.).\n"
    elif top_error == "Verb Tense Error":
        feedback_str += "- Keep your sentences in the same tense.\n- Check subject-verb agreement.\n"
    elif top_error == "Determiner Error":
        feedback_str += "- Practice using 'a', 'an', and 'the' correctly.\n"
    else:
        feedback_str += "- Review general grammar and practice with targeted exercises.\n"

    return {"feedback": feedback_str}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
