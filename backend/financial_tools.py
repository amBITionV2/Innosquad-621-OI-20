import yfinance as yf
import pandas as pd
from typing import Dict, Optional, Any
import math

# ============================================================================
# MANUAL CALCULATOR FUNCTIONS
# ============================================================================

def calculate_future_value(present_value: float, rate: float, periods: int) -> float:
    """
    Calculate Future Value using compound interest formula.
    FV = PV * (1 + r)^n
    """
    return present_value * (1 + rate) ** periods

def calculate_compound_interest(principal: float, rate: float, periods: int, compounds_per_period: int = 1) -> Dict[str, float]:
    """
    Calculate compound interest with different compounding frequencies.
    A = P(1 + r/n)^(nt)
    """
    amount = principal * (1 + rate / compounds_per_period) ** (compounds_per_period * periods)
    interest_earned = amount - principal
    
    return {
        "final_amount": round(amount, 2),
        "interest_earned": round(interest_earned, 2),
        "principal": principal
    }

def calculate_npv(initial_investment: float, cash_flows: list, discount_rate: float) -> Dict[str, float]:
    """
    Calculate Net Present Value (NPV).
    NPV = -Initial Investment + Σ(Cash Flow / (1 + r)^t)
    """
    npv = -initial_investment
    
    for i, cash_flow in enumerate(cash_flows, 1):
        npv += cash_flow / (1 + discount_rate) ** i
    
    return {
        "npv": round(npv, 2),
        "initial_investment": initial_investment,
        "total_cash_flows": sum(cash_flows),
        "discount_rate": discount_rate
    }

def calculate_break_even(fixed_costs: float, variable_cost_per_unit: float, price_per_unit: float) -> Dict[str, float]:
    """
    Calculate Break-Even Point.
    Break-Even = Fixed Costs / (Price per Unit - Variable Cost per Unit)
    """
    if price_per_unit <= variable_cost_per_unit:
        return {
            "break_even_units": None,
            "break_even_revenue": None,
            "error": "Price per unit must be greater than variable cost per unit"
        }
    
    break_even_units = fixed_costs / (price_per_unit - variable_cost_per_unit)
    break_even_revenue = break_even_units * price_per_unit
    
    return {
        "break_even_units": round(break_even_units, 2),
        "break_even_revenue": round(break_even_revenue, 2),
        "contribution_margin": round(price_per_unit - variable_cost_per_unit, 2)
    }

# ============================================================================
# COMPANY ANALYSIS FUNCTIONS
# ============================================================================

def get_initial_data(company_symbol: str) -> Dict[str, Any]:
    """
    Fetch all possible financial data for a company using yfinance.
    Returns None for unavailable data points without crashing.
    """
    try:
        ticker = yf.Ticker(company_symbol)
        info = ticker.info
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
        cash_flow = ticker.cashflow
        
        # Helper function to safely get data
        def safe_get(source, key, default=None):
            try:
                return source.get(key, default) if source else default
            except:
                return default
        
        # Basic company info
        company_data = {
            "symbol": company_symbol.upper(),
            "company_name": safe_get(info, 'longName'),
            "sector": safe_get(info, 'sector'),
            "industry": safe_get(info, 'industry'),
            
            # Market data
            "market_cap": safe_get(info, 'marketCap'),
            "current_price": safe_get(info, 'currentPrice'),
            "shares_outstanding": safe_get(info, 'sharesOutstanding'),
            
            # Financial statement data
            "total_revenue": None,
            "net_income": None,
            "total_debt": None,
            "cash_and_equivalents": None,
            "total_assets": None,
            "total_equity": None,
            "free_cash_flow": None,
            
            # Ratios and metrics
            "pe_ratio": safe_get(info, 'trailingPE'),
            "pb_ratio": safe_get(info, 'priceToBook'),
            "debt_to_equity": safe_get(info, 'debtToEquity'),
            "roe": safe_get(info, 'returnOnEquity'),
            "roa": safe_get(info, 'returnOnAssets'),
            "profit_margin": safe_get(info, 'profitMargins'),
            
            # WACC components
            "beta": safe_get(info, 'beta'),
            "risk_free_rate": None,  # User input required
            "market_risk_premium": None,  # User input required
            "tax_rate": safe_get(info, 'effectiveTaxRate'),
            
            # DCF components
            "revenue_growth_rate": None,  # User input required
            "terminal_growth_rate": None,  # User input required
            "projection_years": 5  # Default
        }
        
        # Try to get financial statement data from the most recent year
        try:
            if not financials.empty:
                latest_financials = financials.iloc[:, 0]
                company_data["total_revenue"] = latest_financials.get('Total Revenue')
                company_data["net_income"] = latest_financials.get('Net Income')
        except:
            pass
            
        try:
            if not balance_sheet.empty:
                latest_balance = balance_sheet.iloc[:, 0]
                company_data["total_debt"] = latest_balance.get('Total Debt')
                company_data["cash_and_equivalents"] = latest_balance.get('Cash And Cash Equivalents')
                company_data["total_assets"] = latest_balance.get('Total Assets')
                company_data["total_equity"] = latest_balance.get('Total Equity')
        except:
            pass
            
        try:
            if not cash_flow.empty:
                latest_cashflow = cash_flow.iloc[:, 0]
                company_data["free_cash_flow"] = latest_cashflow.get('Free Cash Flow')
        except:
            pass
        
        return company_data
        
    except Exception as e:
        return {
            "error": f"Failed to fetch data for {company_symbol}: {str(e)}",
            "symbol": company_symbol.upper()
        }

def calculate_wacc(market_value_equity: float, market_value_debt: float, 
                  cost_of_equity: float, cost_of_debt: float, tax_rate: float) -> float:
    """Calculate Weighted Average Cost of Capital (WACC)"""
    total_value = market_value_equity + market_value_debt
    
    if total_value == 0:
        return None
        
    equity_weight = market_value_equity / total_value
    debt_weight = market_value_debt / total_value
    
    wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
    return round(wacc * 100, 2)  # Return as percentage

def calculate_cost_of_equity(risk_free_rate: float, beta: float, market_risk_premium: float) -> float:
    """Calculate Cost of Equity using CAPM"""
    return risk_free_rate + (beta * market_risk_premium)

def calculate_dcf_valuation(free_cash_flow: float, growth_rate: float, 
                           terminal_growth: float, wacc: float, years: int) -> Dict[str, float]:
    """Calculate DCF valuation"""
    if not all([free_cash_flow, wacc]) or wacc <= 0:
        return {"error": "Invalid inputs for DCF calculation"}
    
    # Project future cash flows
    projected_fcf = []
    current_fcf = free_cash_flow
    
    for year in range(1, years + 1):
        current_fcf *= (1 + growth_rate)
        projected_fcf.append(current_fcf)
    
    # Calculate terminal value
    terminal_fcf = projected_fcf[-1] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (wacc - terminal_growth)
    
    # Discount all cash flows to present value
    pv_fcf = sum([fcf / (1 + wacc) ** (i + 1) for i, fcf in enumerate(projected_fcf)])
    pv_terminal = terminal_value / (1 + wacc) ** years
    
    enterprise_value = pv_fcf + pv_terminal
    
    return {
        "enterprise_value": round(enterprise_value, 0),
        "pv_projected_fcf": round(pv_fcf, 0),
        "pv_terminal_value": round(pv_terminal, 0),
        "terminal_value": round(terminal_value, 0)
    }

def calculate_final_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate all financial metrics from validated user data.
    Returns 'N/A' for metrics that can't be computed due to missing data.
    """
    results = {}
    
    # Basic ratios
    try:
        if data.get('net_income') and data.get('total_revenue'):
            results['profit_margin'] = round((data['net_income'] / data['total_revenue']) * 100, 2)
        else:
            results['profit_margin'] = 'N/A'
    except:
        results['profit_margin'] = 'N/A'
    
    try:
        if data.get('net_income') and data.get('total_equity'):
            results['roe'] = round((data['net_income'] / data['total_equity']) * 100, 2)
        else:
            results['roe'] = 'N/A'
    except:
        results['roe'] = 'N/A'
    
    try:
        if data.get('net_income') and data.get('total_assets'):
            results['roa'] = round((data['net_income'] / data['total_assets']) * 100, 2)
        else:
            results['roa'] = 'N/A'
    except:
        results['roa'] = 'N/A'
    
    try:
        if data.get('total_debt') and data.get('total_equity'):
            results['debt_to_equity'] = round(data['total_debt'] / data['total_equity'], 2)
        else:
            results['debt_to_equity'] = 'N/A'
    except:
        results['debt_to_equity'] = 'N/A'
    
    # WACC Calculation
    try:
        if all([data.get('risk_free_rate'), data.get('beta'), data.get('market_risk_premium')]):
            cost_of_equity = calculate_cost_of_equity(
                data['risk_free_rate'] / 100,
                data['beta'],
                data['market_risk_premium'] / 100
            )
            results['cost_of_equity'] = round(cost_of_equity * 100, 2)
        else:
            results['cost_of_equity'] = 'N/A'
    except:
        results['cost_of_equity'] = 'N/A'
    
    try:
        market_value_equity = data.get('market_cap', 0)
        market_value_debt = data.get('total_debt', 0)
        
        if all([market_value_equity, market_value_debt, results.get('cost_of_equity') != 'N/A', 
                data.get('tax_rate')]):
            wacc = calculate_wacc(
                market_value_equity,
                market_value_debt,
                results['cost_of_equity'] / 100,
                0.05,  # Assumed cost of debt 5%
                data['tax_rate']
            )
            results['wacc'] = wacc
        else:
            results['wacc'] = 'N/A'
    except:
        results['wacc'] = 'N/A'
    
    # DCF Valuation
    try:
        if all([data.get('free_cash_flow'), data.get('revenue_growth_rate'), 
                data.get('terminal_growth_rate'), results.get('wacc') != 'N/A']):
            dcf_results = calculate_dcf_valuation(
                data['free_cash_flow'],
                data['revenue_growth_rate'] / 100,
                data['terminal_growth_rate'] / 100,
                results['wacc'] / 100,
                data.get('projection_years', 5)
            )
            results.update(dcf_results)
        else:
            results['enterprise_value'] = 'N/A'
            results['pv_projected_fcf'] = 'N/A'
            results['pv_terminal_value'] = 'N/A'
    except:
        results['enterprise_value'] = 'N/A'
        results['pv_projected_fcf'] = 'N/A'
        results['pv_terminal_value'] = 'N/A'
    
    # Equity Value and Price per Share
    try:
        if (results.get('enterprise_value') != 'N/A' and 
            data.get('total_debt') and data.get('cash_and_equivalents') and 
            data.get('shares_outstanding')):
            
            equity_value = results['enterprise_value'] - data['total_debt'] + data['cash_and_equivalents']
            price_per_share = equity_value / data['shares_outstanding']
            
            results['equity_value'] = round(equity_value, 0)
            results['intrinsic_value_per_share'] = round(price_per_share, 2)
            
            if data.get('current_price'):
                upside_downside = ((price_per_share - data['current_price']) / data['current_price']) * 100
                results['upside_downside_percent'] = round(upside_downside, 2)
            else:
                results['upside_downside_percent'] = 'N/A'
        else:
            results['equity_value'] = 'N/A'
            results['intrinsic_value_per_share'] = 'N/A'
            results['upside_downside_percent'] = 'N/A'
    except:
        results['equity_value'] = 'N/A'
        results['intrinsic_value_per_share'] = 'N/A'
        results['upside_downside_percent'] = 'N/A'
    
    return results
