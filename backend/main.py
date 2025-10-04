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

# Import financial tools functions
from financial_tools import (
    calculate_future_value,
    calculate_compound_interest,
    calculate_npv,
    calculate_break_even,
    get_initial_data,
    calculate_final_report
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

# Financial Calculator Models
class FutureValueRequest(BaseModel):
    present_value: float
    rate: float
    periods: int

class CompoundInterestRequest(BaseModel):
    principal: float
    rate: float
    periods: int
    compounds_per_period: int = 1

class NPVRequest(BaseModel):
    initial_investment: float
    cash_flows: List[float]
    discount_rate: float

class BreakEvenRequest(BaseModel):
    fixed_costs: float
    variable_cost_per_unit: float
    price_per_unit: float

class CompanySymbolRequest(BaseModel):
    symbol: str

class CompanyAnalysisRequest(BaseModel):
    company_data: dict


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

@app.post("/add-manual-note")
def add_manual_note(note: Note):
    print(f"Received manual note: {note.text[:50]}...")
    formatted_note = f"Manual Note or AI Summary: {note.text}"
    notes_db.append(formatted_note)
    return {"status": "success", "note_count": len(notes_db)}
<<<<<<< HEAD

# --- Financial Calculator Endpoints ---

@app.post("/calculate-future-value")
def calc_future_value(request: FutureValueRequest):
    """Calculate Future Value using compound interest formula."""
    try:
        result = calculate_future_value(request.present_value, request.rate, request.periods)
        return {"future_value": result}
    except Exception as e:
        return {"error": str(e)}

@app.post("/calculate-compound-interest")
def calc_compound_interest(request: CompoundInterestRequest):
    """Calculate compound interest with different compounding frequencies."""
    try:
        result = calculate_compound_interest(
            request.principal, 
            request.rate, 
            request.periods, 
            request.compounds_per_period
        )
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/calculate-npv")
def calc_npv(request: NPVRequest):
    """Calculate Net Present Value (NPV)."""
    try:
        result = calculate_npv(
            request.initial_investment,
            request.cash_flows,
            request.discount_rate
        )
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/calculate-break-even")
def calc_break_even(request: BreakEvenRequest):
    """Calculate Break-Even Point."""
    try:
        result = calculate_break_even(
            request.fixed_costs,
            request.variable_cost_per_unit,
            request.price_per_unit
        )
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/get-company-data")
def get_company_data(request: CompanySymbolRequest):
    """Fetch initial company data using yfinance."""
    try:
        result = get_initial_data(request.symbol)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze-company")
def analyze_company(request: CompanyAnalysisRequest):
    """Generate complete financial analysis report."""
    try:
        # Calculate all financial metrics
        metrics = calculate_final_report(request.company_data)
        
        # Generate AI summary using the existing LLM
        from rag_pipeline import Ollama, StrOutputParser, PromptTemplate
        
        # Create a prompt for financial analysis
        analysis_prompt = PromptTemplate(
            template="""You are a professional financial analyst. Based on the following company data and calculated metrics, provide a comprehensive investment analysis.

Company Data:
{company_data}

Calculated Metrics:
{metrics}

Please provide:
1. A brief company overview
2. Key financial strengths and weaknesses
3. Valuation assessment (if DCF data is available)
4. Investment recommendation (Buy/Hold/Sell) with reasoning
5. Key risks to consider

Base your analysis ONLY on the provided data. If certain metrics are 'N/A', acknowledge the limitation.""",
            input_variables=["company_data", "metrics"]
        )
        
        llm = Ollama(model="gemma:2b")
        chain = analysis_prompt | llm | StrOutputParser()
        
        # Format the data for the prompt
        company_summary = {k: v for k, v in request.company_data.items() 
                          if k in ['company_name', 'sector', 'industry', 'market_cap', 'current_price']}
        
        ai_summary = chain.invoke({
            "company_data": str(company_summary),
            "metrics": str(metrics)
        })
        
        return {
            "metrics": metrics,
            "ai_summary": ai_summary,
            "company_data": request.company_data
        }
    except Exception as e:
        return {"error": str(e)}
=======
>>>>>>> 4d39348620f30337417af8257c41cf0843d24623

