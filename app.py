# app.py
import streamlit as st
import pandas as pd

from model import simulate_all_scenarios
from charts import (
    apply_plotly_theme,
    revenue_profit_chart,
    cashflow_waterfall,
    expense_pie,
)
from utils import rub, pct, to_csv_bytes, init_state, scenario_summary_table

st.set_page_config(
    page_title="Online School P&L Pro",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_plotly_theme()
init_state()

st.title("Online School P&L Pro")
st.caption("12-месячный P&L и unit-экономика онлайн-школы")

with st.sidebar:
    st.header("Управляющие параметры")

    st.subheader("1. Трафик и воронка")
    ad_budget = st.slider("Рекламный бюджет, ₽/мес", 0, 300_000, st.session_state.get("ad_budget", 130_000), 5_000, key="ad_budget")
    cpl = st.slider("CPC / CPL, ₽", 100, 10_000, st.session_state.get("cpl", 2_500), 100, key="cpl")
    growth = st.slider("Рост бюджета / показов, MoM", 0.00, 0.20, st.session_state.get("growth", 0.05), 0.01, key="growth")
    sale_conv = st.slider("Конверсия заявки в продажу", 0.10, 0.80, st.session_state.get("sale_conv", 0.50), 0.01, key="sale_conv")

    st.subheader("2. База и удержание")
    ltv_months = st.slider("Срок жизни клиента, мес", 1, 12, st.session_state.get("ltv_months", 7), 1, key="ltv_months")
    churn = st.slider("Churn в месяц", 0.05, 0.20, st.session_state.get("churn", 0.14), 0.01, key="churn")

    st.subheader("3. Продукт и расходы")
    group_share = st.slider("Доля учеников в мини-группах", 0.00, 1.00, st.session_state.get("group_share", 0.50), 0.05, key="group_share")
    indiv_price = st.slider("Чек индивидуально, ₽/занятие", 1_000, 10_000, st.session_state.get("indiv_price", 3_500), 100, key="indiv_price")
    group_price = st.slider("Чек в группе, ₽/занятие", 500, 10_000, st.session_state.get("group_price", 2_000), 100, key="group_price")
    indiv_tutor_cost = st.slider("ФОТ преподавателя индивидуально, ₽/занятие", 500, 5_000, st.session_state.get("indiv_tutor_cost", 2_000), 100, key="indiv_tutor_cost")
    group_monthly_cost = st.slider("ФОТ преподавателя за группу, ₽/мес", 5_000, 50_000, st.session_state.get("group_monthly_cost", 16_000), 500, key="group_monthly_cost")
    group_limit = st.slider("Лимит учеников в группе", 3, 8, st.session_state.get("group_limit", 4), 1, key="group_limit")
    lessons_per_month = st.slider("Занятий на ученика в месяц", 1, 16, st.session_state.get("lessons_per_month", 4), 1, key="lessons_per_month")

    st.subheader("4. Кросс-продажи")
    upsell_conv = st.slider("Конверсия в доп. услугу", 0.00, 0.50, st.session_state.get("upsell_conv", 0.20), 0.01, key="upsell_conv")
    upsell_price = st.slider("Чек доп. услуги, ₽", 500, 20_000, st.session_state.get("upsell_price", 3_500), 100, key="upsell_price")
    upsell_cost = st.slider("ФОТ доп. услуги, ₽", 0, 10_000, st.session_state.get("upsell_cost", 2_000), 100, key="upsell_cost")

    st.subheader("5. Налоги и fixed cost")
    tax_rate = st.slider("УСН", 0.00, 0.20, st.session_state.get("tax_rate", 0.07), 0.005, key="tax_rate")
    acquiring_rate = st.slider("Эквайринг", 0.00, 0.05, st.session_state.get("acquiring_rate", 0.025), 0.001, key="acquiring_rate")
    opex = st.slider("OPEX, ₽/мес", 0, 300_000, st.session_state.get("opex", 40_000), 5_000, key="opex")
    capex = st.slider("CAPEX в 1-й месяц, ₽", 0, 500_000, st.session_state.get("capex", 70_000), 5_000, key="capex")

    st.subheader("6. Комиссия агентства")
    active_scenario = st.selectbox("Сценарий для детального просмотра", ["Разовый %", "RevShare", "CPA"], key="active_scenario")
    agency_pct_new = st.slider("Разовый % от выручки новых", 0.40, 0.50, st.session_state.get("agency_pct_new", 0.45), 0.01, key="agency_pct_new")
    agency_revshare = st.slider("RevShare от всей выручки", 0.10, 0.25, st.session_state.get("agency_revshare", 0.15), 0.01, key="agency_revshare")
    agency_cpa = st.slider("CPA за нового клиента, ₽", 1_000, 20_000, st.session_state.get("agency_cpa", 9_000), 500, key="agency_cpa")

params = {
    "ad_budget": ad_budget,
    "cpl": cpl,
    "growth": growth,
    "sale_conv": sale_conv,
    "ltv_months": ltv_months,
    "churn": churn,
    "group_share": group_share,
    "indiv_price": indiv_price,
    "group_price": group_price,
    "indiv_tutor_cost": indiv_tutor_cost,
    "group_monthly_cost": group_monthly_cost,
    "group_limit": group_limit,
    "lessons_per_month": lessons_per_month,
    "upsell_conv": upsell_conv,
    "upsell_price": upsell_price,
    "upsell_cost": upsell_cost,
    "tax_rate": tax_rate,
    "acquiring_rate": acquiring_rate,
    "opex": opex,
    "capex": capex,
    "agency_pct_new": agency_pct_new,
    "agency_revshare": agency_revshare,
    "agency_cpa": agency_cpa,
}

results = simulate_all_scenarios(params)
active = results[active_scenario]
active_df = active["monthly"]
active_summary = active["summary"]
active_pie = active["expense_mix"]

if ad_budget == 0:
    st.warning("Стагнация: рекламный бюджет равен 0, база постепенно сжимается из-за churn.")
elif growth == 0:
    st.info("Стагнация: рост бюджета 0%, привлечение не масштабируется, churn ограничивает рост выручки.")

if group_share == 1.0:
    if active_summary["gross_margin_m12"] >= 0.75:
        st.success("При 100% групп валовая маржа в 12-м месяце выше 75%.")
    else:
        st.info("При 100% групп маржа резко растет; итог зависит от наполнения группы, чека и ФОТ.")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Выручка M12", rub(active_summary["revenue_m12"]), delta=rub(active_summary["revenue_m12"] - active_df.iloc[0]["revenue"]), border=True)
k2.metric("Чистая прибыль M12", rub(active_summary["net_profit_m12"]), delta=rub(active_summary["net_profit_m12"] - active_df.iloc[0]["net_profit"]), border=True)
k3.metric("Валовая маржа M12", pct(active_summary["gross_margin_m12"]), border=True)
k4.metric("Окупаемость", f'M{active_summary["payback_month"]}' if active_summary["payback_month"] else "Не достигнута", border=True)

tab1, tab2, tab3, tab4 = st.tabs(["Дашборд", "Сценарии", "Модель", "Экспорт"])

with tab1:
    st.plotly_chart(
        revenue_profit_chart(results),
        width="stretch",
        config={"displaylogo": False}
    )

    st.plotly_chart(
        expense_pie(active_pie, "Структура расходов"),
        width="stretch",
        config={"displaylogo": False}
    )

    st.plotly_chart(
        cashflow_waterfall(active_df, f"Cash Flow / Окупаемость — {active_scenario}"),
        width="stretch",
        config={"displaylogo": False}
    )


with tab2:
    summary_df = scenario_summary_table(results)
    show_df = summary_df.copy()
    show_df["Выручка M12"] = show_df["Выручка M12"].map(rub)
    show_df["Чистая прибыль M12"] = show_df["Чистая прибыль M12"].map(rub)
    show_df["Валовая маржа M12"] = show_df["Валовая маржа M12"].map(pct)
    show_df["Маржинальная прибыль M12"] = show_df["Маржинальная прибыль M12"].map(pct)
    show_df["Net Margin M12"] = show_df["Net Margin M12"].map(pct)
    show_df["Cash M12"] = show_df["Cash M12"].map(rub)
    show_df["Окупаемость"] = show_df["Окупаемость"].map(lambda x: "Нет" if pd.isna(x) else f"M{int(x)}")
    st.dataframe(show_df, width="stretch", hide_index=True)

with tab3:
    detail = active_df.copy()
    st.dataframe(detail, width="stretch", hide_index=True)

with tab4:
    st.download_button(
        "Скачать monthly CSV",
        data=to_csv_bytes(active_df),
        file_name=f"online_school_pnl_{active_scenario.lower()}_monthly.csv",
        mime="text/csv",
        type="primary",
    )
    st.download_button(
        "Скачать scenario summary CSV",
        data=to_csv_bytes(scenario_summary_table(results)),
        file_name="online_school_pnl_summary.csv",
        mime="text/csv",
    )
