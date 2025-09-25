from kpi_fetch_doc_items import fetch_bs_items, fetch_pl_items ,fetch_cf_items
from get_kpi_on_doc_type import balance_sheet_kpis, profit_and_loss_kpis, cashflow_kpis, cross_statement_kpis

companies = [
    "HDFC",
    "ITC",
    "HCL",
    "ICICI Bank",
    "Infosys",
    "Larsen & Toubro",
    "Bajaj Finance",
    "Airtel",
    "Tata Motors"
]

all_missing = []

def check_missing(kpis: dict, label: str):
    missing = [k for k, v in kpis.items() if v is None]
    if missing:
        print(f"❌ {label} → Missing {len(missing)}: {missing}")
        all_missing.extend([(label, k) for k in missing])
    else:
        print(f"✅ {label} → All good")

for company in companies:
    print(f"\n================ {company} ================")

    bs_df = fetch_bs_items(company)
    bs_kpis = balance_sheet_kpis(bs_df)
    check_missing(bs_kpis, f"{company} Balance Sheet KPIs")

    pl_df = fetch_pl_items(company)
    pl_kpis = profit_and_loss_kpis(pl_df)
    check_missing(pl_kpis, f"{company} P&L KPIs")

    cf_df = fetch_cf_items(company)
    cf_kpis = cashflow_kpis(cf_df)
    check_missing(cf_kpis, f"{company} Cashflow KPIs")

    x_kpis = cross_statement_kpis(company)
    check_missing(x_kpis, f"{company} Cross Statement KPIs")

print("\n======= SUMMARY =======")
if all_missing:
    print(f"Total missing: {len(all_missing)}")
    for label, metric in all_missing:
        print(f" - {label}: {metric}")
else:
    print("🎉 All KPIs present for all companies!")
