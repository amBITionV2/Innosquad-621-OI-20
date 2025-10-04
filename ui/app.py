import streamlit as st
import requests
import pandas as pd

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"

# --- UI Setup ---
st.set_page_config(
    page_title="Fintwin - See the Numbers. Understand the Story.", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="📊"
)

# --- Custom CSS Styling ---
st.markdown("""
<style>
    /* Import Classic Minimalist Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Source+Sans+Pro:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Main background with black and green gradient */
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 25%, #0d4f3c 50%, #1a1a1a 75%, #000000 100%);
        position: relative;
        font-family: 'Source Sans Pro', sans-serif;
        min-height: 100vh;
    }
    
    /* Main container styling */
    .main .block-container {
        position: relative;
        z-index: 1;
        padding: 3rem 2rem;
        background: rgba(0, 0, 0, 0.85);
        border-radius: 0;
        backdrop-filter: blur(20px);
        box-shadow: none;
        border: none;
        margin: 0;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Header styling - Larger fonts for dark background */
    h1 {
        font-family: 'Playfair Display', serif;
        font-weight: 600;
        color: #00ff88;
        text-align: center;
        font-size: 4.5rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    
    /* Subheader styling */
    h2, h3 {
        font-family: 'Playfair Display', serif;
        font-weight: 500;
        color: #ffffff;
        margin-top: 2rem !important;
        letter-spacing: -0.01em;
        font-size: 2.2rem !important;
    }
    
    /* Tab styling - Dark theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        border-bottom: 1px solid #333333;
        border-radius: 0;
        padding: 0;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 0px 32px;
        background: transparent;
        border-radius: 0;
        color: #cccccc;
        font-weight: 400;
        font-size: 18px;
        font-family: 'Source Sans Pro', sans-serif;
        border: none;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff;
        border-bottom-color: #666666;
    }
    
    .stTabs [aria-selected="true"] {
        background: transparent;
        color: #00ff88 !important;
        border-bottom-color: #00ff88;
        font-weight: 500;
        box-shadow: none;
    }
    
    /* Form styling - Dark theme */
    .stForm {
        background: rgba(26, 26, 26, 0.9);
        border-radius: 8px;
        padding: 2.5rem;
        border: 1px solid #333333;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    /* Input field styling - Dark theme */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background: #2a2a2a;
        border: 1px solid #444444;
        border-radius: 4px;
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 16px;
        color: #ffffff;
        transition: all 0.2s ease;
        padding: 12px 16px;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #00ff88;
        box-shadow: 0 0 0 3px rgba(0, 255, 136, 0.2);
        outline: none;
    }
    
    /* Button styling - Dark theme */
    .stButton > button {
        background: #00ff88;
        color: #000000;
        border: none;
        border-radius: 4px;
        padding: 14px 28px;
        font-family: 'Source Sans Pro', sans-serif;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.2s ease;
        box-shadow: none;
        letter-spacing: 0.025em;
    }
    
    .stButton > button:hover {
        background: #00cc6a;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3);
    }
    
    /* Form submit button - Green accent */
    .stForm > div > div > button {
        background: #00ff88;
        color: #000000;
        border: none;
        border-radius: 4px;
        padding: 16px 32px;
        font-family: 'Source Sans Pro', sans-serif;
        font-weight: 600;
        font-size: 17px;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: none;
        letter-spacing: 0.025em;
    }
    
    .stForm > div > div > button:hover {
        background: #00cc6a;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 255, 136, 0.4);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: #ffffff;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    /* Message styling - Clean */
    .stSuccess {
        background: #f0fff4;
        color: #22543d;
        border-radius: 6px;
        padding: 16px;
        border: 1px solid #9ae6b4;
        box-shadow: none;
    }
    
    .stError {
        background: #fff5f5;
        color: #742a2a;
        border-radius: 6px;
        padding: 16px;
        border: 1px solid #feb2b2;
        box-shadow: none;
    }
    
    .stInfo {
        background: #ebf8ff;
        color: #2a4365;
        border-radius: 6px;
        padding: 16px;
        border: 1px solid #90cdf4;
        box-shadow: none;
    }
    
    /* Column styling - Clean */
    .stColumn {
        background: transparent;
        border-radius: 0;
        padding: 1rem;
        margin: 0;
        backdrop-filter: none;
        border: none;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: #ffffff;
        border-radius: 6px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Spinner styling */
    .stSpinner {
        color: #ff8c00;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        color: #718096;
        background: transparent;
        border-radius: 0;
        margin-top: 3rem;
        backdrop-filter: none;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Label styling - Dark theme */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label {
        font-family: 'Source Sans Pro', sans-serif;
        font-weight: 500;
        color: #cccccc;
        font-size: 16px;
        margin-bottom: 8px;
    }
    
    /* Markdown text styling - Dark theme */
    .stMarkdown {
        font-family: 'Source Sans Pro', sans-serif;
        color: #cccccc;
        line-height: 1.7;
        font-size: 16px;
    }
    
    /* Custom icons using CSS */
    .icon-chart::before { content: "📊"; margin-right: 8px; }
    .icon-calculator::before { content: "🧮"; margin-right: 8px; }
    .icon-business::before { content: "🏢"; margin-right: 8px; }
    .icon-analysis::before { content: "📈"; margin-right: 8px; }
    .icon-money::before { content: "💰"; margin-right: 8px; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tagline styling - Dark theme */
    .tagline {
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 1.5rem;
        color: #cccccc;
        font-weight: 300;
        letter-spacing: 0.05em;
        margin-top: -0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize session state ---
if "company_data" not in st.session_state:
    st.session_state.company_data = None
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

# --- Main Header ---
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem;">
    <h1>Fintwin</h1>
    <p class="tagline">See the Numbers. Understand the Story.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Create Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["Company Analysis", "Investment Calculators", "Business Tools", "Notes & Chat"])

# ============================================================================
# TAB 1: COMPANY ANALYSIS
# ============================================================================
with tab1:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h2>Company Analysis</h2>
        <p style="color: #cccccc; font-size: 1.2rem; font-weight: 300;">Deep dive into any publicly traded company with comprehensive financial analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Step 1: Company Input
    col1, col2 = st.columns([3, 1])
    with col1:
        company_symbol = st.text_input("Enter Company Symbol (e.g., AAPL, MSFT, GOOGL):", placeholder="AAPL")
    with col2:
        analyze_button = st.button("Analyze Company", type="primary")
    
    if analyze_button and company_symbol:
        with st.spinner(f"Fetching data for {company_symbol.upper()}..."):
            try:
                response = requests.post(f"{BACKEND_URL}/get-company-data", 
                                       json={"symbol": company_symbol})
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        st.error(f"Error: {data['error']}")
                    else:
                        st.session_state.company_data = data
                        st.success(f"Data fetched for {data.get('company_name', company_symbol.upper())}!")
                else:
                    st.error("Failed to fetch company data.")
            except requests.exceptions.RequestException:
                st.error("Could not connect to the backend server.")
    
    # Step 2: Interactive Data Form
    if st.session_state.company_data:
        st.markdown("---")
        st.subheader("📝 Review and Complete Company Data")
        st.write("Review the fetched data below. Fill in any missing values and click 'Generate Report'.")
        
        with st.form("company_data_form"):
            data = st.session_state.company_data.copy()
            
            # Company Info Section
            st.markdown("**Company Information**")
            col1, col2 = st.columns(2)
            with col1:
                data['company_name'] = st.text_input("Company Name", value=data.get('company_name', ''))
                data['sector'] = st.text_input("Sector", value=data.get('sector', ''))
            with col2:
                data['industry'] = st.text_input("Industry", value=data.get('industry', ''))
                data['market_cap'] = st.number_input("Market Cap", value=data.get('market_cap') or 0, format="%.0f")
            
            # Market Data Section
            st.markdown("**Market Data**")
            col1, col2, col3 = st.columns(3)
            with col1:
                data['current_price'] = st.number_input("Current Price ($)", value=data.get('current_price') or 0.0, format="%.2f")
            with col2:
                data['shares_outstanding'] = st.number_input("Shares Outstanding", value=data.get('shares_outstanding') or 0, format="%.0f")
            with col3:
                data['beta'] = st.number_input("Beta", value=data.get('beta') or 1.0, format="%.2f")
            
            # Financial Statement Data
            st.markdown("**Financial Statement Data**")
            col1, col2 = st.columns(2)
            with col1:
                data['total_revenue'] = st.number_input("Total Revenue", value=data.get('total_revenue') or 0, format="%.0f")
                data['net_income'] = st.number_input("Net Income", value=data.get('net_income') or 0, format="%.0f")
                data['total_assets'] = st.number_input("Total Assets", value=data.get('total_assets') or 0, format="%.0f")
                data['free_cash_flow'] = st.number_input("Free Cash Flow", value=data.get('free_cash_flow') or 0, format="%.0f")
            with col2:
                data['total_debt'] = st.number_input("Total Debt", value=data.get('total_debt') or 0, format="%.0f")
                data['cash_and_equivalents'] = st.number_input("Cash & Equivalents", value=data.get('cash_and_equivalents') or 0, format="%.0f")
                data['total_equity'] = st.number_input("Total Equity", value=data.get('total_equity') or 0, format="%.0f")
                data['tax_rate'] = st.number_input("Tax Rate (%)", value=(data.get('tax_rate') or 0.25) * 100, format="%.1f") / 100
            
            # WACC & DCF Inputs
            st.markdown("**Valuation Inputs (Required for DCF)**")
            col1, col2, col3 = st.columns(3)
            with col1:
                data['risk_free_rate'] = st.number_input("Risk-Free Rate (%)", value=data.get('risk_free_rate') or 4.5, format="%.2f")
                data['market_risk_premium'] = st.number_input("Market Risk Premium (%)", value=data.get('market_risk_premium') or 6.0, format="%.2f")
            with col2:
                data['revenue_growth_rate'] = st.number_input("Revenue Growth Rate (%)", value=data.get('revenue_growth_rate') or 5.0, format="%.2f")
                data['terminal_growth_rate'] = st.number_input("Terminal Growth Rate (%)", value=data.get('terminal_growth_rate') or 2.5, format="%.2f")
            with col3:
                data['projection_years'] = st.number_input("Projection Years", value=data.get('projection_years') or 5, min_value=1, max_value=10)
            
            # Generate Report Button
            generate_report = st.form_submit_button("📈 Generate Financial Report", type="primary")
            
            if generate_report:
                with st.spinner("Generating comprehensive financial analysis..."):
                    try:
                        response = requests.post(f"{BACKEND_URL}/analyze-company", 
                                               json={"company_data": data})
                        if response.status_code == 200:
                            st.session_state.analysis_results = response.json()
                            st.success("Analysis complete!")
                        else:
                            st.error("Failed to generate analysis.")
                    except requests.exceptions.RequestException:
                        st.error("Could not connect to the backend server.")
    
    # Step 3: Display Results
    if st.session_state.analysis_results:
        st.markdown("---")
        st.subheader("📊 Financial Analysis Results")
        
        results = st.session_state.analysis_results
        
        # Display metrics table
        if "metrics" in results:
            metrics_df = pd.DataFrame(list(results["metrics"].items()), 
                                    columns=["Metric", "Value"])
            st.dataframe(metrics_df, use_container_width=True)
        
        # Display AI Summary
        if "ai_summary" in results:
            st.markdown("---")
            st.subheader("AI Investment Analysis")
            st.markdown(results["ai_summary"])

# ============================================================================
# TAB 2: INVESTMENT CALCULATORS
# ============================================================================
with tab2:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h2>Investment Calculators</h2>
        <p style="color: #cccccc; font-size: 1.2rem; font-weight: 300;">Essential financial calculations for smart investment planning</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Future Value Calculator
    with col1:
        st.subheader("Future Value Calculator")
        with st.form("future_value_form"):
            fv_present_value = st.number_input("Present Value ($)", min_value=0.0, value=1000.0, format="%.2f")
            fv_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=7.0, format="%.2f") / 100
            fv_periods = st.number_input("Number of Years", min_value=1, value=10)
            
            fv_calculate = st.form_submit_button("Calculate Future Value")
            
            if fv_calculate:
                try:
                    response = requests.post(f"{BACKEND_URL}/calculate-future-value", 
                                           json={
                                               "present_value": fv_present_value,
                                               "rate": fv_rate,
                                               "periods": fv_periods
                                           })
                    if response.status_code == 200:
                        result = response.json()
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success(f"**Future Value: ${result['future_value']:,.2f}**")
                    else:
                        st.error("Calculation failed.")
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the backend server.")
    
    # Compound Interest Calculator
    with col2:
        st.subheader("Compound Interest Calculator")
        with st.form("compound_interest_form"):
            ci_principal = st.number_input("Principal Amount ($)", min_value=0.0, value=1000.0, format="%.2f")
            ci_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=7.0, format="%.2f", key="ci_rate") / 100
            ci_periods = st.number_input("Number of Years", min_value=1, value=10, key="ci_periods")
            ci_compounds = st.selectbox("Compounding Frequency", 
                                      options=[1, 2, 4, 12, 365], 
                                      format_func=lambda x: {1: "Annually", 2: "Semi-annually", 
                                                           4: "Quarterly", 12: "Monthly", 365: "Daily"}[x])
            
            ci_calculate = st.form_submit_button("Calculate Compound Interest")
            
            if ci_calculate:
                try:
                    response = requests.post(f"{BACKEND_URL}/calculate-compound-interest", 
                                           json={
                                               "principal": ci_principal,
                                               "rate": ci_rate,
                                               "periods": ci_periods,
                                               "compounds_per_period": ci_compounds
                                           })
                    if response.status_code == 200:
                        result = response.json()
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success(f"**Final Amount: ${result['final_amount']:,.2f}**")
                            st.info(f"Interest Earned: ${result['interest_earned']:,.2f}")
                    else:
                        st.error("Calculation failed.")
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the backend server.")

# ============================================================================
# TAB 3: BUSINESS & PROJECT TOOLS
# ============================================================================
with tab3:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h2>Business Tools</h2>
        <p style="color: #cccccc; font-size: 1.2rem; font-weight: 300;">Project evaluation and business planning for strategic decisions</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # NPV Calculator
    with col1:
        st.subheader("Net Present Value (NPV)")
        with st.form("npv_form"):
            npv_initial = st.number_input("Initial Investment ($)", min_value=0.0, value=100000.0, format="%.2f")
            npv_discount = st.number_input("Discount Rate (%)", min_value=0.0, value=10.0, format="%.2f") / 100
            
            st.write("**Cash Flows by Year:**")
            cash_flows = []
            for i in range(5):
                cf = st.number_input(f"Year {i+1} Cash Flow ($)", value=25000.0, format="%.2f", key=f"cf_{i}")
                cash_flows.append(cf)
            
            npv_calculate = st.form_submit_button("Calculate NPV")
            
            if npv_calculate:
                try:
                    response = requests.post(f"{BACKEND_URL}/calculate-npv", 
                                           json={
                                               "initial_investment": npv_initial,
                                               "cash_flows": cash_flows,
                                               "discount_rate": npv_discount
                                           })
                    if response.status_code == 200:
                        result = response.json()
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            npv_value = result['npv']
                            if npv_value > 0:
                                st.success(f"**NPV: ${npv_value:,.2f}** ✅ (Positive - Good Investment)")
                            else:
                                st.error(f"**NPV: ${npv_value:,.2f}** ❌ (Negative - Poor Investment)")
                    else:
                        st.error("Calculation failed.")
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the backend server.")
    
    # Break-Even Calculator
    with col2:
        st.subheader("Break-Even Analysis")
        with st.form("break_even_form"):
            be_fixed_costs = st.number_input("Fixed Costs ($)", min_value=0.0, value=50000.0, format="%.2f")
            be_variable_cost = st.number_input("Variable Cost per Unit ($)", min_value=0.0, value=20.0, format="%.2f")
            be_price = st.number_input("Price per Unit ($)", min_value=0.0, value=50.0, format="%.2f")
            
            be_calculate = st.form_submit_button("Calculate Break-Even")
            
            if be_calculate:
                try:
                    response = requests.post(f"{BACKEND_URL}/calculate-break-even", 
                                           json={
                                               "fixed_costs": be_fixed_costs,
                                               "variable_cost_per_unit": be_variable_cost,
                                               "price_per_unit": be_price
                                           })
                    if response.status_code == 200:
                        result = response.json()
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success(f"**Break-Even Units: {result['break_even_units']:,.0f}**")
                            st.info(f"Break-Even Revenue: ${result['break_even_revenue']:,.2f}")
                            st.info(f"Contribution Margin: ${result['contribution_margin']:,.2f} per unit")
                    else:
                        st.error("Calculation failed.")
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the backend server.")

# ============================================================================
# TAB 4: NOTES & CHAT
# ============================================================================
with tab4:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h2>Notes & Chat</h2>
        <p style="color: #cccccc; font-size: 1.2rem; font-weight: 300;">AI-powered research assistant with smart note-taking and analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for notes
    if "notes" not in st.session_state:
        st.session_state.notes = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Research Notes")
        
        # Add manual note section
        with st.form("add_note_form"):
            new_note = st.text_area("Add a research note:", placeholder="Enter your research findings, insights, or observations here...", height=100)
            add_note_button = st.form_submit_button("Add Note")
            
            if add_note_button and new_note.strip():
                try:
                    response = requests.post(f"{BACKEND_URL}/add-manual-note", 
                                           json={"text": new_note})
                    if response.status_code == 200:
                        st.success("Note added successfully!")
                        # Refresh notes
                        notes_response = requests.get(f"{BACKEND_URL}/notes")
                        if notes_response.status_code == 200:
                            st.session_state.notes = notes_response.json()["notes"]
                    else:
                        st.error("Failed to add note.")
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the backend server.")
        
        # URL Summarization section
        st.markdown("---")
        st.subheader("Smart URL Summarizer")
        with st.form("url_summary_form"):
            url_input = st.text_input("Enter URL to summarize:", placeholder="https://example.com/article")
            summarize_button = st.form_submit_button("Get Contextual Summary")
            
            if summarize_button and url_input.strip():
                with st.spinner("Analyzing URL and generating contextual summary..."):
                    try:
                        response = requests.post(f"{BACKEND_URL}/summarize-url", 
                                               json={"url": url_input})
                        if response.status_code == 200:
                            summary = response.json()["summary"]
                            st.success("Summary generated!")
                            st.markdown("**Contextual Summary:**")
                            st.markdown(summary)
                            
                            # Refresh notes after summary is added
                            notes_response = requests.get(f"{BACKEND_URL}/notes")
                            if notes_response.status_code == 200:
                                st.session_state.notes = notes_response.json()["notes"]
                        else:
                            st.error("Failed to generate summary.")
                    except requests.exceptions.RequestException:
                        st.error("Could not connect to the backend server.")
        
        # Contradiction Check section
        st.markdown("---")
        st.subheader("Contradiction Analysis")
        if st.button("Check for Contradictions", type="secondary"):
            with st.spinner("Analyzing notes for contradictions..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/check-contradictions")
                    if response.status_code == 200:
                        result = response.json()["result"]
                        if "No contradictions" in result:
                            st.success(result)
                        else:
                            st.warning("**Potential Contradiction Found:**")
                            st.markdown(result)
                    else:
                        st.error("Failed to check contradictions.")
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the backend server.")
        
        # Display current notes
        st.markdown("---")
        st.subheader("Current Notes")
        try:
            notes_response = requests.get(f"{BACKEND_URL}/notes")
            if notes_response.status_code == 200:
                notes = notes_response.json()["notes"]
                if notes:
                    for i, note in enumerate(notes[-5:], 1):  # Show last 5 notes
                        with st.expander(f"Note {len(notes) - 5 + i}", expanded=False):
                            st.markdown(note)
                else:
                    st.info("No notes yet. Add some research notes to get started!")
            else:
                st.error("Could not fetch notes.")
        except requests.exceptions.RequestException:
            st.error("Could not connect to the backend server.")
    
    with col2:
        st.subheader("AI Research Assistant")
        
        # Chat interface
        st.markdown("Ask questions about your research notes:")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("**Chat History:**")
            for i, (question, answer) in enumerate(st.session_state.chat_history[-3:]):  # Show last 3 exchanges
                st.markdown(f"**Q{len(st.session_state.chat_history) - 2 + i}:** {question}")
                st.markdown(f"**A:** {answer}")
                st.markdown("---")
        
        # Question input
        with st.form("chat_form"):
            user_question = st.text_area("Ask a question about your research:", 
                                       placeholder="What are the key themes in my notes? Are there any conflicting viewpoints?", 
                                       height=100)
            ask_button = st.form_submit_button("Ask Question")
            
            if ask_button and user_question.strip():
                with st.spinner("Analyzing your notes and generating response..."):
                    try:
                        response = requests.post(f"{BACKEND_URL}/ask", 
                                               json={"question": user_question})
                        if response.status_code == 200:
                            answer = response.json()["answer"]
                            
                            # Add to chat history
                            st.session_state.chat_history.append((user_question, answer))
                            
                            # Display the latest response
                            st.success("Response generated!")
                            st.markdown("**Answer:**")
                            st.markdown(answer)
                        else:
                            st.error("Failed to get response.")
                    except requests.exceptions.RequestException:
                        st.error("Could not connect to the backend server.")
        
        # Clear chat history button
        if st.session_state.chat_history:
            if st.button("Clear Chat History", type="secondary"):
                st.session_state.chat_history = []
                st.success("Chat history cleared!")
        
        # Additional AI features
        st.markdown("---")
        st.subheader("Advanced Analysis")
        
        # Research guidance
        if st.button("Get Research Guidance", type="secondary"):
            with st.spinner("Generating research guidance..."):
                try:
                    # Get current notes first
                    notes_response = requests.get(f"{BACKEND_URL}/notes")
                    if notes_response.status_code == 200:
                        notes = notes_response.json()["notes"]
                        if notes:
                            # Use the latest notes as financial data context
                            latest_notes = " ".join(notes[-3:])  # Last 3 notes
                            response = requests.post(f"{BACKEND_URL}/guide-research", 
                                                   json={"financial_data": latest_notes})
                            if response.status_code == 200:
                                guidance = response.json()["guidance"]
                                st.success("Research guidance generated!")
                                st.markdown("**Research Guidance:**")
                                st.markdown(guidance)
                            else:
                                st.error("Failed to get research guidance.")
                        else:
                            st.info("Add some notes first to get research guidance.")
                    else:
                        st.error("Could not fetch notes.")
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the backend server.")

# --- Footer ---
st.markdown("""
<div class="footer">
    <h3 style="font-family: 'Playfair Display', serif; color: #2d3748; margin-bottom: 1rem;">Fintwin</h3>
    <p style="margin-bottom: 0.5rem;">See the Numbers. Understand the Story.</p>
    <p style="font-size: 0.9rem; color: #a0aec0;">Privacy-first • Local AI • Professional Grade Financial Analysis</p>
</div>
""", unsafe_allow_html=True)

