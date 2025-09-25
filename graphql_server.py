import typing
from typing import List
from kpi_fetch_doc_items import fetch_bs_items, fetch_pl_items, fetch_cf_items
from get_kpi_on_doc_type import (
    balance_sheet_kpis,
    profit_and_loss_kpis,
    cashflow_kpis,
    cross_statement_kpis,
)

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from fastapi.middleware.cors import CORSMiddleware

# --- Your existing utils ---
from db_utils import get_financial_data
from rag_query import run_rag_question
# ---------- GraphQL Types ----------

all_missing = []

def check_missing(kpis: dict, label: str):
    missing = [k for k, v in kpis.items() if v is None]
    if missing:
        print(f"❌ {label} → Missing {len(missing)}: {missing}")
        all_missing.extend([(label, k) for k in missing])
    else:
        print(f"✅ {label} → All good")

@strawberry.type
class FinancialItem:
    line_item: typing.Optional[str] = strawberry.field(name="line_item")
    fy_2024: typing.Optional[float] = strawberry.field(name="fy_2024")
    fy_2023: typing.Optional[float] = strawberry.field(name="fy_2023")


@strawberry.type
class KPI:
    name: str
    value: typing.Optional[str]
    status: typing.Optional[str]  # e.g. "ok" | "missing"
    description: str


@strawberry.type
class CompanyMetrics:
    balance_sheet: List[KPI]
    pnl: List[KPI]
    cashflow: List[KPI]
    cross_statement: List[KPI]


# ---------- Root Query ----------

@strawberry.type
class Query:
    @strawberry.field
    def ask_question(self, question: str) -> str:
        return run_rag_question(question)

    @strawberry.field
    def get_financials(self, company: str, statementType: str) -> List[FinancialItem]:
        data = get_financial_data(company, statementType)
        return [FinancialItem(**item) for item in data]

    @strawberry.field
    def company_metrics(self, company: str) -> CompanyMetrics:
        print(company)

        # --- Balance Sheet ---
        bs_df = fetch_bs_items(company)
        bs_kpis = balance_sheet_kpis(bs_df)  # dict: {name: value}
        check_missing(bs_kpis, f"{company} Balance Sheet KPIs")

        # --- P&L ---
        pl_df = fetch_pl_items(company)
        pl_kpis = profit_and_loss_kpis(pl_df)
        check_missing(pl_kpis, f"{company} P&L KPIs")

        # --- Cashflow ---
        cf_df = fetch_cf_items(company)
        cf_kpis = cashflow_kpis(cf_df)
        check_missing(cf_kpis, f"{company} Cashflow KPIs")

        # --- Cross Statement ---
        x_kpis = cross_statement_kpis(bs_df, pl_df, cf_df)
        check_missing(x_kpis, f"{company} Cross Statement KPIs")

        if all_missing:
            print(f"Total missing: {len(all_missing)}")
            for label, metric in all_missing:
                print(f" - {label}: {metric}")
        else:
            print("🎉 All KPIs present for all companies!")

        # ✅ Convert dicts into list of KPI objects
        def dict_to_kpi_list(kpis: dict) -> List[KPI]:
            return [
                KPI(
                    name=k,
                    value=(str(v[0]) if v is not None else None),
                    status=("ok" if v is not None else "missing"),
                    description=(str(v[1]) if v is not None else None)
                )
                for k, v in kpis.items()
            ]

        return CompanyMetrics(
            balance_sheet=dict_to_kpi_list(bs_kpis),
            pnl=dict_to_kpi_list(pl_kpis),
            cashflow=dict_to_kpi_list(cf_kpis),
            cross_statement=dict_to_kpi_list(x_kpis),
        )


# ---------- FastAPI Setup ----------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to RAG-FSI GraphQL API. Go to /graphql"}

schema = strawberry.Schema(query=Query)
graphql_router = GraphQLRouter(schema, graphiql=True)
app.include_router(graphql_router, prefix="/graphql")
