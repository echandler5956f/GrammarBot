# GrammarBot

## Overview

**GrammarBot** is an end-to-end application that detects and corrects grammatical errors, categorizes them, logs them for each student, and provides personalized feedback. The application is composed of:

1. **Backend** (Python/FastAPI):  
   - Handles user creation and authentication (in a simple manner).  
   - Performs the grammar correction and error classification using state-of-the-art NLP models (e.g., T5, BERT).  
   - Stores errors and user data in a relational database (SQLite by default).  
   - Exposes RESTful endpoints for front-end interaction.

2. **Frontend** (HTML/CSS/JavaScript):  
   - Provides a user interface to create students, submit text, view corrections, and receive feedback.  
   - Communicates with the backend over HTTP/JSON.

### Key Features

- **Grammar Error Correction**: Generates corrected sentences using a T5-based model.  
- **Error Classification**: Labels each error (e.g., Spelling Error, Punctuation Error, Verb Tense Error, etc.).  
- **Database Storage**: Logs each student’s errors in a relational DB.  
- **Personalized Feedback**: Aggregates error types to give user-specific tips (e.g., “Your most common issue is verb tense!”).  
- **Web Interface**: A simple UI that displays corrected text, annotated mistakes, and real-time feedback.

---

## Table of Contents

1. [Demo Video Placeholder](#demo-video-placeholder)  
2. [Architecture](#architecture)  
3. [Installation](#installation)  
4. [Configuration](#configuration)  
5. [Running the Backend](#running-the-backend)  
6. [Running the Frontend](#running-the-frontend)  
7. [Testing the Application](#testing-the-application)  
8. [Usage Flow](#usage-flow)  
9. [Deployment Notes](#deployment-notes)  
10. [Future Improvements](#future-improvements)  
11. [License](#license)

---

## Demo Video Placeholder

*(Replace this section with an actual link to a hosted video of your GrammarBot demonstration. For now, it’s a placeholder to show where you could embed or link a screen recording.)*

---

## Architecture

```
grammar_bot/
├── backend
│   ├── main.py           # FastAPI entry point
│   ├── db.py             # Database setup (SQLAlchemy engine & session)
│   ├── models.py         # SQLAlchemy ORM models (Student, ErrorLog)
│   ├── ml.py             # ML pipeline (grammar correction & classification)
│   ├── schemas.py        # Pydantic models for request/response schemas
│   ├── requirements.txt  # Python dependencies
└── frontend
    ├── index.html        # Minimal front-end interface
    └── script.js         # JavaScript for front-end logic
```

- **Database**: Default is SQLite (`grammarbot.db`), but can be changed to PostgreSQL or another RDBMS.  
- **Models**:  
  - `Student` stores student info (name, unique ID).  
  - `ErrorLog` stores each logged grammar error (type, original text, corrected text, spans).  
- **ML**:  
  - Grammar Correction uses a sequence-to-sequence model (T5).  
  - Error Classification uses a classification model (BERT/DistilBERT) to label the error type.

---

## Installation

### 1. Prerequisites

- **Python 3.7+**  
- **Git** (optional, if you want to clone a repository)  
- **A modern browser** (Chrome, Firefox, Safari, or Edge)  
- (Optional) **Node.js** or **any local web server** for serving the front-end

### 2. Clone or Download the Repository

```bash
git clone https://github.com/YourUsername/GrammarBot.git
cd GrammarBot
```

Or manually download the files and ensure the structure matches the diagram above.

---

## Configuration

By default, the app uses an **SQLite** database named `grammarbot.db` located in the `backend` folder. If you want to use a different database (e.g., PostgreSQL), update `DATABASE_URL` in **`db.py`** accordingly:

```python
DATABASE_URL = "postgresql://username:password@localhost:5432/yourdb"
```

If you change it, run migrations or recreate tables as needed.

---

## Running the Backend

1. **Navigate** to the `backend` directory:
   ```bash
   cd grammar_bot/backend
   ```
2. **(Optional but recommended)** Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or on Windows
   # venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Start the server**:
   ```bash
   uvicorn main:app --reload
   ```
   - The app should now be running on `http://127.0.0.1:8000`.

When first started, it will create `grammarbot.db` (if using SQLite) and automatically set up the tables.

---

## Running the Frontend

1. **Navigate** to the `frontend` folder:
   ```bash
   cd ../frontend
   ```
2. **Serve** the front-end files. You have a couple of choices:
   - **Simple Python HTTP server**:
     ```bash
     python -m http.server 8080
     ```
     Then open [http://127.0.0.1:8080/index.html](http://127.0.0.1:8080/index.html) in your browser.
   - **Or** open `index.html` directly in your browser. *(May cause CORS issues. A local HTTP server is recommended.)*

3. **Configure** the front-end’s base URL if needed:
   - In `script.js`, confirm `const BASE_URL = "http://localhost:8000";` matches your backend host/port.

---

## Testing the Application

1. **Open** [http://127.0.0.1:8080/index.html](http://127.0.0.1:8080/index.html).  
2. **Create Student**:
   - In the “Create New Student Name” field, type e.g. `Alice`.
   - Click **Create Student**. A pop-up should confirm the new student ID.
3. **Analyze Text**:
   - Type some text with errors in the text area (e.g., `She go to the store yesterday.`).
   - Click **Analyze**.
   - The page should display corrected text (e.g., `She went to the store yesterday.`) and highlight the detected errors.
   - The **Feedback** section will show aggregated tips based on error frequencies.
4. **Check Logs**:
   - Go to [http://127.0.0.1:8000/students/1/errors](http://127.0.0.1:8000/students/1/errors) to see raw JSON of logged errors for student ID 1.
   - Go to [http://127.0.0.1:8000/students/1/feedback](http://127.0.0.1:8000/students/1/feedback) to see the aggregated feedback JSON.

---

## Usage Flow

1. **Create a Student** → obtains a unique ID in the backend DB.  
2. **Analyze** arbitrary text → grammar corrections and error logs are stored.  
3. **Review** mistakes and feedback from your front-end UI or directly via the REST endpoints.

---

## Deployment Notes

1. **Production Database**:  
   - For concurrent usage, consider switching from SQLite to PostgreSQL or MySQL.  
   - Update `DATABASE_URL` in `db.py` and run any migrations (if needed).

2. **Production Server**:  
   - Use a **reverse proxy** (Nginx, Apache) or run in a container (Docker) for better scalability.  
   - Deploy to AWS, Azure, Google Cloud, Heroku, or your preferred platform.

3. **Security/Authentication**:  
   - Add robust user authentication if you plan to expose it publicly.  
   - The current system is a basic demonstration of user creation with minimal validation.

4. **GPU Inference** (optional):  
   - If you scale to large T5/BERT models, you may need a GPU-based environment. This can be more expensive but significantly faster for heavy loads.

---

## Future Improvements

- **Fine-tuned Models**:  
  - Train a custom grammar correction model on a domain-specific corpus for improved accuracy.
- **More Granular Error Types**:  
  - Expand classification categories (e.g., subject-verb agreement, preposition usage).
- **User Authentication**:  
  - Implement OAuth or JWT to secure endpoints.
- **Front-End**:  
  - Upgrade from a raw HTML/JS approach to a modern framework (React, Vue, or Angular) for a richer UI/UX.
- **Internationalization**:  
  - Support multiple languages or localize the UI.

---

## License

```
MIT License

Copyright (c) [2025] [Ethan Chandler]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

**Happy Grammar Checking!**