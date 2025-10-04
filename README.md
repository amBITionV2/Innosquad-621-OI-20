# Fintwin: See the Numbers. Understand the Story.

**Fintwin** is a comprehensive AI-powered financial analysis platform that combines traditional financial calculations with modern AI insights. Built for investors, analysts, and business professionals who need reliable financial tools with intelligent analysis.

## 🚀 The Problem: Fragmented Financial Analysis

Financial analysis typically requires multiple tools, spreadsheets, and manual calculations. Analysts spend time switching between different platforms for basic calculations, company research, and generating insights. Fintwin consolidates everything into one intelligent platform.

## ✨ The Solution: Integrated Financial Intelligence

Fintwin provides a complete financial analysis suite with three core modules:
- **Company Analysis**: AI-powered stock analysis with DCF valuation, WACC calculation, and investment recommendations
- **Investment Calculators**: Essential financial calculators for personal and professional use
- **Business Tools**: Project evaluation and business planning calculators

## 🎯 Core Features

### 📊 Company Analysis Tool
- **Real-time Data Fetching**: Automatically pulls financial data using yfinance
- **Interactive Data Review**: Pre-filled forms with manual override capability
- **Comprehensive Metrics**: WACC, DCF valuation, financial ratios, and key performance indicators
- **AI Investment Analysis**: LLM-generated investment recommendations and risk assessments
- **Professional Reports**: Clean data tables with AI-powered summaries

### 💰 Investment Calculators
- **Future Value Calculator**: Compound interest calculations for investment planning
- **Advanced Compound Interest**: Multiple compounding frequencies (daily, monthly, quarterly, annually)
- **User-Friendly Interface**: Clean forms with instant results

### 🏢 Business & Project Tools
- **Net Present Value (NPV)**: Multi-year cash flow analysis for project evaluation
- **Break-Even Analysis**: Calculate break-even points for business planning
- **Scenario Planning**: Test different assumptions and variables

### 🤖 AI-Powered Insights
- **Local AI Processing**: Uses Ollama with Gemma 2B model for complete privacy
- **Context-Aware Analysis**: AI understands financial context and provides relevant insights
- **Investment Recommendations**: Buy/Hold/Sell recommendations with detailed reasoning

## 🛠️ Tech Stack

**Backend:**
- Python 3.9+
- FastAPI (REST API)
- yfinance (Financial data)
- LangChain (AI pipeline)
- Ollama (Local LLM)
- Pandas (Data processing)

**Frontend:**
- Streamlit (Web interface)
- Responsive design with tabbed navigation

**AI & Data:**
- Gemma 2B model (via Ollama)
- ChromaDB (Vector storage)
- FastEmbed (Embeddings)

## 🏃‍♀️ Quick Start Guide

### Prerequisites
- **Python 3.9+**
- **Ollama** installed and running
- **Git** (for cloning)

### 1. Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd fintwin

# Navigate to backend and install dependencies
cd backend
pip install -r requirements.txt
```

### 2. Download AI Model
```bash
# In a separate terminal, download the AI model (one-time setup)
ollama run gemma:2b
```

### 3. Run the Application

**Terminal 1 - Backend Server:**
```bash
# From the backend directory
uvicorn main:app --reload
```
*Backend will run on http://127.0.0.1:8000*

**Terminal 2 - Frontend UI:**
```bash
# From the ui directory
cd ../ui
pip install streamlit pandas
streamlit run app.py
```
*Frontend will open automatically in your browser at http://localhost:8501*

## 📈 How to Use

### Company Analysis Workflow
1. **Enter Symbol**: Input any stock ticker (e.g., AAPL, MSFT, GOOGL)
2. **Review Data**: Check auto-fetched financial data and fill missing values
3. **Generate Report**: Get comprehensive analysis with AI insights
4. **Investment Decision**: Review metrics, valuation, and AI recommendations

### Calculator Usage
- **Investment Calculators**: Enter principal, rate, and time period
- **Business Tools**: Input costs, cash flows, and business parameters
- **Instant Results**: Get immediate calculations with clear explanations

## 🔧 API Documentation

Once running, visit `http://127.0.0.1:8000/docs` for interactive API documentation with all available endpoints.

## 🎨 Features Highlights

- **Privacy-First**: All AI processing happens locally
- **Real-Time Data**: Live financial data from Yahoo Finance
- **Professional Grade**: Institutional-quality financial calculations
- **User-Friendly**: Clean, intuitive interface suitable for all skill levels
- **Comprehensive**: Everything from basic calculators to advanced DCF models
- **AI-Enhanced**: Intelligent insights and recommendations

## 🚀 Future Enhancements

- Portfolio analysis and optimization
- Technical analysis indicators
- Sector and peer comparison
- Historical performance analysis
- Export capabilities (PDF reports)
- Multi-currency support

---

**Built with ❤️ for the financial community**

*Fintwin: See the Numbers. Understand the Story. - Combining the precision of traditional financial analysis with the intelligence of modern AI, all while maintaining complete privacy through local processing.*
