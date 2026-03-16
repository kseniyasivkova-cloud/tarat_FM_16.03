# utils.py
import pandas as pd
import streamlit as st


def rub(x):
    return f"{x:,.0f} ₽".replace(",", " ")


def pct(x):
    return f"{x:.1%}"


@st.cache_data
def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def init_state():
    defaults = {
        "ad_budget": 130_000,
        "cpl": 2_500,
        "growth": 0.05,
        "sale_conv": 0.50,
        "ltv_months": 7,
        "churn": 0.14,
        "group_share": 0.50,
        "indiv_price": 3_500,
        "group_price": 2_000,
        "indiv_tutor_cost": 2_000,
        "group_monthly_cost": 16_000,
        "group_limit": 4,
        "lessons_per_month": 4,
        "upsell_conv": 0.20,
        "upsell_price": 3_500,
        "upsell_cost": 2_000,
        "tax_rate": 0.07,
        "acquiring_rate": 0.025,
        "opex": 40_000,
        "capex": 70_000,
        "agency_pct_new": 0.45,
        "agency_revshare": 0.15,
        "agency_cpa": 9_000,
        "active_scenario": "Разовый %",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def scenario_summary_table(results):
    rows = []
    for name, pack in results.items():
        s = pack["summary"]
        rows.append({
            "Сценарий": name,
            "Выручка M12": s["revenue_m12"],
            "Чистая прибыль M12": s["net_profit_m12"],
            "Валовая маржа M12": s["gross_margin_m12"],
            "Маржинальная прибыль M12": s["margin_rate_m12"],
            "Net Margin M12": s["net_margin_m12"],
            "Cash M12": s["cash_m12"],
            "Окупаемость": s["payback_month"],
        })
    return pd.DataFrame(rows)
