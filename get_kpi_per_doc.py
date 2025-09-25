import pandas as pd
from KPIs_RAF_FSI.helper import _need, _opt
from KPIs_RAF_FSI.kpi_fetch_doc_items import fetch_bs_items, fetch_pl_items, fetch_cf_items


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
        "current_ratio_2024": ca24 / cl24 if cl24 else None,
        "current_ratio_2023": ca23 / cl23 if cl23 else None,
        "quick_ratio_2024": (ca24 - inv24) / cl24 if cl24 else None,
        "quick_ratio_2023": (ca23 - inv23) / cl23 if cl23 else None,
        "debt_to_equity_2024": tl24 / te24 if te24 else None,
        "debt_to_equity_2023": tl23 / te23 if te23 else None,
        "assets_vs_equity_liab_2024": (ta24, te24 + tl24),
        "assets_vs_equity_liab_2023": (ta23, te23 + tl23),
    }

def profit_and_loss_kpis(df: pd.DataFrame):
    # Prefer Revenue from operations; if missing, fall back to Total income
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
        "net_profit_margin_2024": pat24 / base24 if base24 else None,
        "net_profit_margin_2023": pat23 / base23 if base23 else None,
        "pbt_margin_2024": pbt24 / base24 if base24 else None,
        "pbt_margin_2023": pbt23 / base23 if base23 else None,
        "revenue_yoy_growth": (base24 - base23) / base23 if base23 else None,
        "net_profit_yoy_growth": (pat24 - pat23) / pat23 if pat23 else None,
        "finance_cost_2024": fin24,
        "finance_cost_2023": fin23,
        "depreciation_2024": dep24,
        "depreciation_2023": dep23,
    }

def cashflow_kpis(df: pd.DataFrame):
    cfo24 = _need(df, "Net cash from operating activities", "fy_2024")
    cfo23 = _need(df, "Net cash from operating activities", "fy_2023")
    cfi24 = _need(df, "Net cash from investing activities", "fy_2024")
    cfi23 = _need(df, "Net cash from investing activities", "fy_2023")
    cff24 = _need(df, "Net cash from financing activities", "fy_2024")
    cff23 = _need(df, "Net cash from financing activities", "fy_2023")
    cap24 = _opt(df, "Purchase of property, plant and equipment", "fy_2024", 0.0)  # usually negative
    cap23 = _opt(df, "Purchase of property, plant and equipment", "fy_2023", 0.0)
    div24 = _opt(df, "Dividends paid", "fy_2024", 0.0)
    div23 = _opt(df, "Dividends paid", "fy_2023", 0.0)

    denom24 = abs(cfo24) + abs(cfi24) + abs(cff24)
    return {
        "cfo_2024": cfo24, "cfi_2024": cfi24, "cff_2024": cff24,
        "cfo_2023": cfo23, "cfi_2023": cfi23, "cff_2023": cff23,
        "free_cash_flow_2024": cfo24 + cap24,
        "free_cash_flow_2023": cfo23 + cap23,
        "dividends_2024": div24,
        "dividends_2023": div23,
        "cfo_mix_2024": (cfo24 / denom24) if denom24 else None,
        "cfi_mix_2024": (cfi24 / denom24) if denom24 else None,
        "cff_mix_2024": (cff24 / denom24) if denom24 else None,
    }

def cross_statement_kpis(company: str):
    bs = fetch_bs_items(company)
    pl = fetch_pl_items(company)
    cf = fetch_cf_items(company)

    # Needed:
    te24 = _need(bs, "Total Equity", "fy_2024")
    ta24 = _need(bs, "Total Assets", "fy_2024")
    rec24 = _opt(bs, "Trade receivables", "fy_2024", None)  # might be missing for banks etc.
    rec23 = _opt(bs, "Trade receivables", "fy_2023", None)

    # PL base (rev or total income)
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
        "roe_2024": pat24 / te24 if te24 else None,
        "roa_2024": pat24 / ta24 if ta24 else None,
        "cash_conversion_2024": cfo24 / pat24 if pat24 else None,
        "receivables_as_pct_of_revenue_2024": (rec24 / base24) if (rec24 is not None and base24) else None,
        "receivables_yoy_growth": ((rec24 - rec23) / rec23) if (rec24 is not None and rec23 not in (None, 0)) else None,
        "revenue_yoy_growth": (base24 - base23) / base23 if base23 else None,
    }
