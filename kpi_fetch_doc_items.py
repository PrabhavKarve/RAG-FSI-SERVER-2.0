import pandas as pd
from KPIs_RAF_FSI.kpi_rag_retrieval import rag_lookup

def _fetch_required(company: str, statement_type: str, items: list[str]) -> pd.DataFrame:
    rows = []
    for q in items:
        hit = rag_lookup(company, statement_type, q)
        if hit:  # keep your canonical name even if source phrasing differs
            rows.append(hit)
    if not rows:
        # Return an empty frame with expected schema so downstream doesn't crash
        return pd.DataFrame(columns=["line_item", "fy_2024", "fy_2023"]).set_index("line_item")
    return pd.DataFrame(rows).set_index("line_item")

# Balance Sheet
def fetch_bs_items(company: str) -> pd.DataFrame:
    required = [
        "Total Current Assets",
        "Total Current Liabilities",
        "Inventories",
        "Total Liabilities",
        "Total Equity",
        "Total Assets",
        # Optional extras you might want:
        # "Trade receivables", "Cash and cash equivalents"
    ]
    return _fetch_required(company, "balance_sheet", required)

# Profit & Loss
def fetch_pl_items(company: str) -> pd.DataFrame:
    required = [
        "Revenue from operations",     # fallback: "Total income"
        "Total income",
        "Total expenses",
        "Profit before tax",
        "Profit for the year",
        "Finance costs",
        "Depreciation and amortization",
    ]
    return _fetch_required(company, "profit_and_loss", required)

# Cashflow
def fetch_cf_items(company: str) -> pd.DataFrame:
    required = [
        "Net cash from operating activities",
        "Net cash from investing activities",
        "Net cash from financing activities",
        "Purchase of property, plant and equipment",   # Capex proxy (usually negative)
        "Dividends paid",
    ]
    return _fetch_required(company, "cash_flows", required)
