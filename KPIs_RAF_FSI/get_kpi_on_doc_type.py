import pandas as pd
from helper import _need, _opt
from kpi_fetch_doc_items import fetch_bs_items, fetch_pl_items, fetch_cf_items


def _fmt(val):
    if val is None:
        return None
    try:
        return round(val, 3)  # keep as float, rounded to 3 decimals
    except Exception:
        return val


# ---------------- Balance Sheet ----------------
def balance_sheet_kpis(df: pd.DataFrame):
    ca24 = _need(df, "Total Current Assets", "fy_2024")
    ca23 = _need(df, "Total Current Assets", "fy_2023")
    cl24 = _need(df, "Total Current Liabilities", "fy_2024")
    cl23 = _need(df, "Total Current Liabilities", "fy_2023")
    inv24 = _opt(df, "Inventories", "fy_2024", 0.0)
    inv23 = _opt(df, "Inventories", "fy_2023", 0.0)
    tl24 = _need(df, "Total Liabilities", "fy_2024")
    tl23 = _need(df, "Total Liabilities", "fy_2023")
    te24 = _need(df, "Total Equity", "fy_2024")
    te23 = _need(df, "Total Equity", "fy_2023")
    ta24 = _need(df, "Total Assets", "fy_2024")
    ta23 = _need(df, "Total Assets", "fy_2023")

    return {
        "current_ratio_2024": (_fmt(ca24 / cl24 if cl24 else None),
            "Liquidity ratio: current assets ÷ current liabilities (FY2024)."),
        "current_ratio_2023": (_fmt(ca23 / cl23 if cl23 else None),
            "Liquidity ratio: current assets ÷ current liabilities (FY2023)."),
        "quick_ratio_2024": (_fmt((ca24 - inv24) / cl24 if cl24 else None),
            "Acid-test: (current assets – inventories) ÷ current liabilities (FY2024)."),
        "quick_ratio_2023": (_fmt((ca23 - inv23) / cl23 if cl23 else None),
            "Acid-test: (current assets – inventories) ÷ current liabilities (FY2023)."),
        "debt_to_equity_2024": (_fmt(tl24 / te24 if te24 else None),
            "Leverage: total liabilities ÷ equity (FY2024)."),
        "debt_to_equity_2023": (_fmt(tl23 / te23 if te23 else None),
            "Leverage: total liabilities ÷ equity (FY2023)."),
        "assets_vs_equity_liab_2024": ((_fmt(ta24), _fmt(te24 + tl24)),
            "Check: assets should equal liabilities + equity (FY2024)."),
        "assets_vs_equity_liab_2023": ((_fmt(ta23), _fmt(te23 + tl23)),
            "Check: assets should equal liabilities + equity (FY2023)."),
    }


# ---------------- Profit & Loss ----------------
def profit_and_loss_kpis(df: pd.DataFrame):
    rev24 = _opt(df, "Revenue from operations", "fy_2024", None)
    rev23 = _opt(df, "Revenue from operations", "fy_2023", None)
    tin24 = _opt(df, "Total income", "fy_2024", None)
    tin23 = _opt(df, "Total income", "fy_2023", None)

    base24 = rev24 if rev24 is not None else tin24
    base23 = rev23 if rev23 is not None else tin23
    if base24 is None or base23 is None:
        raise ValueError("Neither 'Revenue from operations' nor 'Total income' found.")

    tex24 = _need(df, "Total expenses", "fy_2024")
    tex23 = _need(df, "Total expenses", "fy_2023")
    pbt24 = _need(df, "Profit before tax", "fy_2024")
    pbt23 = _need(df, "Profit before tax", "fy_2023")
    pat24 = _need(df, "Profit for the year", "fy_2024")
    pat23 = _need(df, "Profit for the year", "fy_2023")
    fin24 = _opt(df, "Finance costs", "fy_2024", 0.0)
    fin23 = _opt(df, "Finance costs", "fy_2023", 0.0)
    dep24 = _opt(df, "Depreciation and amortization", "fy_2024", 0.0)
    dep23 = _opt(df, "Depreciation and amortization", "fy_2023", 0.0)

    return {
        "net_profit_margin_2024": (_fmt(pat24 / base24 if base24 else None),
            "Net margin: profit after tax ÷ revenue (FY2024)."),
        "net_profit_margin_2023": (_fmt(pat23 / base23 if base23 else None),
            "Net margin: profit after tax ÷ revenue (FY2023)."),
        "pbt_margin_2024": (_fmt(pbt24 / base24 if base24 else None),
            "Profit before tax ÷ revenue (FY2024)."),
        "pbt_margin_2023": (_fmt(pbt23 / base23 if base23 else None),
            "Profit before tax ÷ revenue (FY2023)."),
        "revenue_yoy_growth": (_fmt((base24 - base23) / base23 if base23 else None),
            "Year-over-year growth in revenue."),
        "net_profit_yoy_growth": (_fmt((pat24 - pat23) / pat23 if pat23 else None),
            "Year-over-year growth in net profit."),
        "finance_cost_2024": (_fmt(fin24),
            "Finance costs (interest and related expenses, FY2024)."),
        "finance_cost_2023": (_fmt(fin23),
            "Finance costs (interest and related expenses, FY2023)."),
        "depreciation_2024": (_fmt(dep24),
            "Depreciation and amortization expense (FY2024)."),
        "depreciation_2023": (_fmt(dep23),
            "Depreciation and amortization expense (FY2023)."),
    }


# ---------------- Cash Flow ----------------
def cashflow_kpis(df: pd.DataFrame):
    cfo24 = _need(df, "Net cash from operating activities", "fy_2024")
    cfo23 = _need(df, "Net cash from operating activities", "fy_2023")
    cfi24 = _need(df, "Net cash from investing activities", "fy_2024")
    cfi23 = _need(df, "Net cash from investing activities", "fy_2023")
    cff24 = _need(df, "Net cash from financing activities", "fy_2024")
    cff23 = _need(df, "Net cash from financing activities", "fy_2023")
    cap24 = _opt(df, "Purchase of property, plant and equipment", "fy_2024", 0.0)
    cap23 = _opt(df, "Purchase of property, plant and equipment", "fy_2023", 0.0)
    div24 = _opt(df, "Dividends paid", "fy_2024", 0.0)
    div23 = _opt(df, "Dividends paid", "fy_2023", 0.0)

    denom24 = abs(cfo24) + abs(cfi24) + abs(cff24)
    return {
        "cfo_2024": (_fmt(cfo24), "Operating cash flow (cash from core operations, FY2024)."),
        "cfo_2023": (_fmt(cfo23), "Operating cash flow (cash from core operations, FY2023)."),
        "cfi_2024": (_fmt(cfi24), "Investing cash flow (capital expenditure, acquisitions, FY2024)."),
        "cfi_2023": (_fmt(cfi23), "Investing cash flow (capital expenditure, acquisitions, FY2023)."),
        "cff_2024": (_fmt(cff24), "Financing cash flow (debt, equity, dividends, FY2024)."),
        "cff_2023": (_fmt(cff23), "Financing cash flow (debt, equity, dividends, FY2023)."),
        "free_cash_flow_2024": (_fmt(cfo24 + cap24),
            "Free cash flow: operating cash – capital expenditure (FY2024)."),
        "free_cash_flow_2023": (_fmt(cfo23 + cap23),
            "Free cash flow: operating cash – capital expenditure (FY2023)."),
        "dividends_2024": (_fmt(div24),
            "Dividends paid to shareholders (FY2024)."),
        "dividends_2023": (_fmt(div23),
            "Dividends paid to shareholders (FY2023)."),
        "cfo_mix_2024": (_fmt(cfo24 / denom24 if denom24 else None),
            "Share of operating cash in total cash flow mix (FY2024)."),
        "cfi_mix_2024": (_fmt(cfi24 / denom24 if denom24 else None),
            "Share of investing cash in total cash flow mix (FY2024)."),
        "cff_mix_2024": (_fmt(cff24 / denom24 if denom24 else None),
            "Share of financing cash in total cash flow mix (FY2024)."),
    }


# ---------------- Cross-Statement ----------------
def cross_statement_kpis( bs, pl, cf):

    te24 = _need(bs, "Total Equity", "fy_2024")
    ta24 = _need(bs, "Total Assets", "fy_2024")
    rec24 = _opt(bs, "Trade receivables", "fy_2024", None)
    rec23 = _opt(bs, "Trade receivables", "fy_2023", None)

    rev24 = _opt(pl, "Revenue from operations", "fy_2024", None)
    rev23 = _opt(pl, "Revenue from operations", "fy_2023", None)
    tin24 = _opt(pl, "Total income", "fy_2024", None)
    tin23 = _opt(pl, "Total income", "fy_2023", None)
    base24 = rev24 if rev24 is not None else tin24
    base23 = rev23 if rev23 is not None else tin23
    if base24 is None or base23 is None:
        raise ValueError("Cross KPIs need Revenue or Total income from P&L.")

    pat24 = _need(pl, "Profit for the year", "fy_2024")
    cfo24 = _need(cf, "Net cash from operating activities", "fy_2024")

    return {
        "roe_2024": (_fmt(pat24 / te24 if te24 else None),
            "Return on equity: net profit ÷ equity (FY2024)."),
        "roa_2024": (_fmt(pat24 / ta24 if ta24 else None),
            "Return on assets: net profit ÷ assets (FY2024)."),
        "cash_conversion_2024": (_fmt(cfo24 / pat24 if pat24 else None),
            "Cash conversion: operating cash ÷ net profit (FY2024)."),
        "receivables_as_pct_of_revenue_2024": (_fmt(rec24 / base24 if (rec24 is not None and base24) else None),
            "Receivables as % of revenue (working capital efficiency, FY2024)."),
        "receivables_yoy_growth": (_fmt((rec24 - rec23) / rec23 if (rec24 is not None and rec23 not in (None, 0)) else None),
            "Year-over-year growth in trade receivables."),
        "revenue_yoy_growth": (_fmt((base24 - base23) / base23 if base23 else None),
            "Year-over-year growth in revenue."),
    }
