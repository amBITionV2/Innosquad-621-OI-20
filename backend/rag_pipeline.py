import os
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# --- Synthesis Agent Prompt ---
synthesis_prompt_template = """
You are Jigyasa, an expert financial analyst and research assistant. Your primary skill is synthesis.
Your user has provided you with several research notes. Your task is to deeply analyze these notes, connect the dots between them, and generate a single, coherent answer to their question.

- **Synthesize, do not just summarize.** Find the hidden connections and trade-offs.
- **Formulate a conclusion** or key takeaway, even if the notes don't explicitly state one.
- **You must base your answer ONLY on the information provided in the "Context" notes below.** Do not use any outside knowledge.
- If the context is truly insufficient to answer, state that clearly.

Context:
---
{context}
---

Question: {question}

Expert Analysis:
"""
SYNTHESIS_PROMPT = PromptTemplate(
    template=synthesis_prompt_template, input_variables=["context", "question"]
)

# --- Verifier Agent Prompt ---
VERIFIER_PROMPT_TEMPLATE = """
You are a meticulous fact-checking agent. Your task is to determine if a "New Note" contradicts any information within the "Existing Notes".
Analyze the context and answer with only one of two possible responses:
1. If there is a clear contradiction, respond with: "CONTRADICTION: [Briefly explain the contradiction in one sentence]."
2. If there is no contradiction, respond with: "NO_CONTRADICTION".

Existing Notes:
---
{context}
---

New Note: {new_note}

Your Analysis:
"""
VERIFIER_PROMPT = PromptTemplate(
    template=VERIFIER_PROMPT_TEMPLATE, input_variables=["context", "new_note"]
)

# --- Smart Summarizer Agent Prompt ---
SMART_SUMMARY_PROMPT_TEMPLATE = """
You are Jigyasa, an expert research analyst. Your user is reading a "New Article" and wants a summary that is personalized to their "Existing Research Notes".

Your task is to:
1. Read the New Article.
2. Read the Existing Research Notes to understand the user's current interests.
3. Write a concise summary of the New Article, focusing ONLY on the parts that are directly relevant to the topics found in the Existing Research Notes. Ignore all other information.

Existing Research Notes:
---
{context}
---

New Article:
---
{new_article}
---

Your Smart Summary:
"""
SMART_SUMMARY_PROMPT = PromptTemplate(
    template=SMART_SUMMARY_PROMPT_TEMPLATE, input_variables=["context", "new_article"]
)

# --- Data Extraction Agent Prompt ---
DATA_EXTRACTION_PROMPT_TEMPLATE = """
You are a Data Structuring Agent. Your task is to analyze the following raw text, identify what kind of financial statement it is (e.g., "Profit & Loss Statement", "Balance Sheet"), and reformat it into a clean, readable Markdown table.

Raw Text:
---
{raw_text}
---

Your Structured Output:
"""
DATA_EXTRACTION_PROMPT = PromptTemplate(
    template=DATA_EXTRACTION_PROMPT_TEMPLATE, input_variables=["raw_text"]
)

# --- Inquiry Agent ("Master Analyst") Prompt ---
INQUIRY_PROMPT_TEMPLATE = """
You are a Senior Financial Analyst mentoring a junior analyst. The junior has provided "Research Notes" and a "Structured Financial Statement".

Your task is to act as a teacher. Analyze all the information and guide the junior on the single most important next step in their valuation process.
1.  **Identify the next logical model:** Based on the forward financials, this will likely be a Discounted Cash Flow (DCF) analysis.
2.  **Briefly explain the model:** In one sentence, what is it for?
3.  **Provide the core formula:** Write out the formula for the model.
4.  **Identify the key missing variable:** Point out the most important component of the formula that is not in the provided data (e.g., WACC or a Growth Rate) and explain why it's needed.

Research Notes:
---
{notes_context}
---

Structured Financial Statement:
---
{financial_data}
---

Your Mentorship and Guidance:
"""
INQUIRY_PROMPT = PromptTemplate(
    template=INQUIRY_PROMPT_TEMPLATE, input_variables=["notes_context", "financial_data"]
)

XRAY_PROMPT_TEMPLATE = """
You are an expert financial analyst agent specializing in document analysis. Your task is to read a dense financial document and extract the following critical data points.
If a data point is not mentioned, you must explicitly state "Not Found".

DOCUMENT TEXT:
---
{context}
---

Based on the text, provide the following in a simple, clear format:
- **Expense Ratio:**
- **Lock-in Period:**
- **Exit Load:**
- **Pre-existing Disease Waiting Period:**
- **Room Rent Capping:**
- **Co-payment Clause:**
"""
XRAY_PROMPT = PromptTemplate(
    template=XRAY_PROMPT_TEMPLATE, input_variables=["context"]
)

# --- Agent Functions ---

def get_jigyasa_response(question: str, notes: list[str]) -> str:
    if not notes: return "The notebook is empty."
    docs = [Document(page_content=note) for note in notes]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)
    embeddings = FastEmbedEmbeddings()
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm = Ollama(model="gemma:2b")
    rag_chain = ({"context": retriever, "question": RunnablePassthrough()} | SYNTHESIS_PROMPT | llm | StrOutputParser())
    answer = rag_chain.invoke(question)
    vectorstore.delete_collection()
    return answer

def check_for_contradictions(new_note: str, existing_notes: list[str]) -> str | None:
    if not existing_notes: return None
    docs = [Document(page_content=note) for note in existing_notes]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)
    embeddings = FastEmbedEmbeddings()
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm = Ollama(model="gemma:2b")
    def format_docs(docs): return "\n\n".join(doc.page_content for doc in docs)
    verifier_chain = ({"context": retriever | format_docs, "new_note": RunnablePassthrough()} | VERIFIER_PROMPT | llm | StrOutputParser())
    try:
        response = verifier_chain.invoke(new_note)
        if response and response.strip().startswith("CONTRADICTION:"):
            return response.strip()
        else:
            return None
    except Exception as e:
        print(f"An error occurred in the verifier chain: {e}")
        return "Error: The Verifier Agent encountered a problem."
    finally:
        try:
            vectorstore.delete_collection()
        except Exception as e:
            print(f"Could not delete temporary collection: {e}")

def get_contextual_summary(url: str, existing_notes: list[str]) -> str:
    if not existing_notes:
        return "Your notebook is empty. Please add some notes before trying to get a smart summary."
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        new_article_text = ' '.join(p.get_text() for p in soup.find_all('p'))
        if not new_article_text: return "Error: Could not extract readable text from this URL."
    except Exception as e:
        return f"Error: Failed to fetch or parse the URL. Details: {e}"
    docs = [Document(page_content=note) for note in existing_notes]
    embeddings = FastEmbedEmbeddings()
    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = Ollama(model="gemma:2b")
    smart_summary_chain = ({"context": retriever, "new_article": RunnablePassthrough()} | SMART_SUMMARY_PROMPT | llm | StrOutputParser())
    summary = smart_summary_chain.invoke(new_article_text[:8000])
    vectorstore.delete_collection()
    return summary

def structure_financial_data(raw_text: str) -> str:
    llm = Ollama(model="gemma:2b")
    extraction_chain = (DATA_EXTRACTION_PROMPT | llm | StrOutputParser())
    structured_data = extraction_chain.invoke({"raw_text": raw_text})
    return structured_data

def get_socratic_guidance(notes: list[str], financial_data: str) -> str:
    llm = Ollama(model="gemma:2b")
    notes_context = "\n".join(notes)
    inquiry_chain = (INQUIRY_PROMPT | llm | StrOutputParser())
    guidance = inquiry_chain.invoke({"notes_context": notes_context, "financial_data": financial_data})
    return guidance

def analyze_document_with_xray(file_path: str) -> str:
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        full_text = " ".join(page.page_content for page in pages)
    except Exception as e:
        return f"Error: Could not read the PDF file. Details: {e}"
    llm = Ollama(model="gemma:2b")
    xray_chain = (XRAY_PROMPT | llm | StrOutputParser())
    analysis = xray_chain.invoke({"context": full_text})
    return analysis

