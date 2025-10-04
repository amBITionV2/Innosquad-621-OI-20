from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

# This will now correctly import all necessary functions
from rag_pipeline import (
    get_jigyasa_response, 
    check_for_contradictions,
    structure_financial_data,
    get_socratic_guidance,
    get_contextual_summary 
)

app = FastAPI(title="Jigyasa Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

notes_db: List[str] = []

# --- API Models ---
class Note(BaseModel): text: str
class Question(BaseModel): question: str
class RawText(BaseModel): text: str
class InquiryRequest(BaseModel): financial_data: str
class URLRequest(BaseModel): url: str


# --- Endpoints ---

@app.post("/add-note")
def add_note(note: Note):
    notes_db.append(note.text)
    return {"status": "success", "note_count": len(notes_db)}

@app.get("/notes")
def get_notes():
    return {"notes": notes_db}

@app.post("/ask")
def ask_question(question: Question):
    user_input = question.question.lower().strip()
    greetings = ["hello", "hi", "hey"]
    if user_input in greetings:
        return {"answer": "Hello! How can I help you with your research?"}
    if not notes_db:
        return {"answer": "My notebook is empty. Please add some notes first."}
    return {"answer": get_jigyasa_response(question.question, notes_db)}

@app.post("/check-contradictions")
def run_contradiction_check():
    """Runs the heavy AI analysis only when the user asks for it."""
    print("Running contradiction check...")
    if len(notes_db) < 2:
        return {"result": "You need at least two notes to check for contradictions."}
    
    # We check the most recent note against all previous notes
    latest_note = notes_db[-1]
    previous_notes = notes_db[:-1]
    
    contradiction_warning = check_for_contradictions(latest_note, previous_notes)
    
    if contradiction_warning:
        return {"result": contradiction_warning}
    else:
        return {"result": "No contradictions found among your recent notes."}

@app.post("/extract-data")
def extract_data(request: RawText):
    return {"structured_data": structure_financial_data(request.text)}

@app.post("/guide-research")
def guide_research(request: InquiryRequest):
    return {"guidance": get_socratic_guidance(notes_db, request.financial_data)}

@app.post("/summarize-url")
def summarize_url(request: URLRequest):
    """Receives a URL, scrapes it, and generates a context-aware summary."""
    print(f"Received URL to summarize: {request.url}")
    summary = get_contextual_summary(request.url, notes_db)
    return {"summary": summary}

# @app.post("/add-manual-note")
# def add_manual_note(note: Note):
#     print(f"Received manual note: {note.text[:50]}...")
#     formatted_note = f"Manual Note or AI Summary: {note.text}"
#     notes_db.append(formatted_note)
#     return {"status": "success", "note_count": len(notes_db)}

