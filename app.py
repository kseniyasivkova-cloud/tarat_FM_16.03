# app.py
import pandas as pd
import streamlit as st

from model import simulate_excel_model
from charts import (
    apply_plotly_theme,
    revenue_profit_chart_v4,
    cashflow_chart_v4,
    expense_pie_v4,
)
from utils import rub, pct, to_csv_bytes


st.set_page_config(
    page_title="Online School P&L Pro v4",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_plotly_theme()

st.title("Online School P&L Pro")
st.caption("v4 — модель приведена к Excel-логике Taratorkina")

with st.sidebar:
    st.header("Управляющие параметры")

    st.subheader("1. Воронка продаж")
    start_students = st.slider("База на начало периода, учеников", 0, 300, 90, 1)

    growth_new_sales_pct = st.slider(
        "Ежемесячный рост новых продаж, %",
        min_value=0,
        max_value=30,
        value=20,
        step=1,
    )

    ad_budget_m1 = st.slider("Рекламный бюджет M1, ₽", 0, 500_000, 130_000, 5_000)
    cpl = st.slider("Стоимость лида (CPL), ₽", 500, 10_000, 2_500, 100)

    trial_conv_pct = st.slider(
        "Конверсия лид -> пробный, %",
        min_value=10,
        max_value=100,
        value=50,
        step=1,
    )

    sale_conv_pct = st.slider(
        "Конверсия пробный -> продажа, %",
        min_value=10,
        max_value=100,
        value=50,
        step=1,
    )

    st.subheader("2. База и удержание")
    ltv_months = st.slider("Срок жизни ученика / LTV, мес", 1, 12, 7, 1)
    churn = 1 / ltv_months if ltv_months > 0 else 0.0
    st.metric("Расчетный Churn в месяц", churn, format="percent")

    st.subheader("3. Продукт и формат")
    group_share_pct = st.slider(
        "Доля учеников в мини-группах, %",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
    )

    indiv_price_month = st.slider("Средний чек индивид, ₽/мес", 5_000, 60_000, 28_000, 500)
    indiv_lesson_price = st.slider("Стоимость 1 занятия для клиента (индив), ₽", 500, 10_000, 3_500, 100)
    indiv_tutor_lesson_cost = st.slider("Ставка препода за 1 занятие (индив), ₽", 500, 5_000, 2_000, 100)

    group_price_month = st.slider("Средний чек мини-группы, ₽/мес", 5_000, 60_000, 16_000, 500)
    group_lessons_month = st.slider("Кол-во занятий в мес (группа)", 1, 16, 8, 1)
    group_lesson_price = st.slider("Стоимость 1 занятия для клиента (группа), ₽", 500, 10_000, 2_000, 100)
    group_monthly_cost = st.slider("Ставка препода за месяц с 1 группы, ₽", 5_000, 50_000, 16_000, 500)
    group_limit = st.slider("Лимит учеников в группе", 3, 8, 4, 1)

    st.subheader("4. Кросс-сейл")
    upsell_conv_pct = st.slider(
        "Конверсия в покупку доп. услуги, %",
        min_value=0,
        max_value=50,
        value=20,
        step=1,
    )

    upsell_price = st.slider("Средний чек доп. услуги, ₽", 500, 20_000, 3_500, 100)
    upsell_cost = st.slider("Себестоимость / ФОТ доп. услуги на 1 чел, ₽", 0, 10_000, 2_000, 100)

    st.subheader("5. Налоги и постоянные")
    tax_rate_pct = st.slider(
        "Налог УСН, %",
        min_value=0.0,
        max_value=20.0,
        value=7.0,
        step=0.5,
    )

    acquiring_rate_pct = st.slider(
        "Эквайринг, %",
        min_value=0.0,
        max_value=5.0,
        value=2.5,
        step=0.1,
    )

    fixed_opex = st.slider("Постоянные расходы, ₽/мес", 0, 300_000, 40_000, 5_000)
    capex = st.slider("CAPEX в 1-й месяц, ₽", 0, 500_000, 70_000, 5_000)

    st.subheader("6. Агентская комиссия")
    active_scenario = st.selectbox("Активный сценарий", ["Разовый %", "RevShare", "CPA"])

    agency_new_pct_ui = st.slider(
        "Сценарий 1: % от новых привлеченных, %",
        min_value=40,
        max_value=60,
        value=50,
        step=1,
    )

    agency_revshare_ui = st.slider(
        "Сценарий 2: RevShare от выручки, %",
        min_value=10,
        max_value=25,
        value=15,
        step=1,
    )

    agency_cpa = st.slider("Сценарий 3: CPA за нового ученика, ₽", 1_000, 20_000, 9_000, 500)

params = {
    "start_students": start_students,
    "growth_new_sales": growth_new_sales_pct / 100,
    "ad_budget_m1": ad_budget_m1,
    "cpl": cpl,
    "trial_conv": trial_conv_pct / 100,
    "sale_conv": sale_conv_pct / 100,
    "ltv_months": ltv_months,
    "churn": churn,
    "group_share": group_share_pct / 100,
    "indiv_price_month": indiv_price_month,
    "indiv_lesson_price": indiv_lesson_price,
    "indiv_tutor_lesson_cost": indiv_tutor_lesson_cost,
    "group_price_month": group_price_month,
    "group_lessons_month": group_lessons_month,
    "group_lesson_price": group_lesson_price,
    "group_monthly_cost": group_monthly_cost,
    "group_limit": group_limit,
    "upsell_conv": upsell_conv_pct / 100,
    "upsell_price": upsell_price,
    "upsell_cost": upsell_cost,
    "tax_rate": tax_rate_pct / 100,
    "acquiring_rate": acquiring_rate_pct / 100,
    "fixed_opex": fixed_opex,
    "capex": capex,
    "agency_new_pct": agency_new_pct_ui / 100,
    "agency_revshare": agency_revshare_ui / 100,
    "agency_cpa": agency_cpa,
}

results = simulate_excel_model(params)
active = results[active_scenario]
active_df = active["monthly"]
active_summary = active["summary"]
active_pie = active["expense_mix"]

if growth_new_sales_pct == 0:
    st.info("Сценарий близок к стагнации: рост новых продаж = 0%, поэтому база ограничивается оттоком [file:133].")

if group_share_pct == 100:
    st.success("При 100% групп валовая маржа по групповому продукту стремится к уровню около 75%, как в Excel [file:133].")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Выручка M12", rub(active_summary["revenue_m12"]))
k2.metric("Чистая прибыль M12", rub(active_summary["net_profit_m12"]))
k3.metric("Валовая маржа M12", active_summary["gross_margin_m12"], format="percent")
k4.metric("Окупаемость", f'M{active_summary["payback_month"]}' if active_summary["payback_month"] else "Не достигнута")

k5, k6, k7, k8 = st.columns(4)
k5.metric("Активные ученики M12", f'{active_summary["active_students_m12"]:.0f}')
k6.metric("Новых учеников за год", f'{active_summary["new_students_year"]:.0f}')
k7.metric("Маржинальность M12", active_summary["margin_rate_m12"], format="percent")
k8.metric("Рентабельность по ЧП M12", active_summary["net_margin_m12"], format="percent")

tabs = st.tabs(["Дашборд", "Сценарии", "Модель", "Экспорт"])

with tabs[0]:
    st.plotly_chart(
        revenue_profit_chart_v4(results),
        width="stretch",
        config={"displaylogo": False},
    )

    st.plotly_chart(
        expense_pie_v4(active_pie),
        width="stretch",
        config={"displaylogo": False},
    )

    st.plotly_chart(
        cashflow_chart_v4(active_df, f"Окупаемость / Cash Flow — {active_scenario}"),
        width="stretch",
        config={"displaylogo": False},
    )

with tabs[1]:
    summary_rows = []
    for name, pack in results.items():
        s = pack["summary"]
        summary_rows.append({
            "Сценарий": name,
            "Выручка M12": rub(s["revenue_m12"]),
            "Чистая прибыль M12": rub(s["net_profit_m12"]),
            "Валовая маржа M12": pct(s["gross_margin_m12"]),
            "Маржинальность M12": pct(s["margin_rate_m12"]),
            "Net Margin M12": pct(s["net_margin_m12"]),
            "Окупаемость": f'M{s["payback_month"]}' if s["payback_month"] else "Нет",
        })

    st.dataframe(
        pd.DataFrame(summary_rows),
        width="stretch",
        hide_index=True,
    )

with tabs[2]:
    show_cols = [
        "label",
        "ad_budget",
        "leads",
        "trials",
        "new_students",
        "start_base",
        "churned_students",
        "active_students",
        "indiv_students",
        "group_students",
        "groups_count",
        "revenue_total",
        "gross_profit_total",
        "margin_profit_before_marketing",
        "marketing_cost",
        "agency_fee",
        "operating_profit",
        "cross_sell_profit",
        "net_profit",
        "cumulative_cash",
    ]

    detail = active_df[show_cols].copy()
    detail.columns = [
        "Месяц",
        "Рекламный бюджет",
        "Лиды",
        "Пробные",
        "Новые",
        "База на начало",
        "Ушло",
        "Активные ученики",
        "Индивид",
        "Группы",
        "Кол-во групп",
        "Выручка",
        "Валовая прибыль",
        "Марж. прибыль до маркетинга",
        "Маркетинг",
        "Комиссия агентства",
        "Опер. прибыль",
        "Прибыль cross-sell",
        "Чистая прибыль",
        "Накопленный cash flow",
    ]

    st.dataframe(
        detail,
        width="stretch",
        hide_index=True,
        height=520,
    )

with tabs[3]:
    st.download_button(
        "Скачать monthly CSV",
        data=to_csv_bytes(active_df),
        file_name=f"pnl_v4_{active_scenario.lower()}_monthly.csv",
        mime="text/csv",
        type="primary",
    )

    scenario_export = []
    for name, pack in results.items():
        s = pack["summary"]
        scenario_export.append({
            "scenario": name,
            "revenue_m12": s["revenue_m12"],
            "net_profit_m12": s["net_profit_m12"],
            "gross_margin_m12": s["gross_margin_m12"],
            "margin_rate_m12": s["margin_rate_m12"],
            "net_margin_m12": s["net_margin_m12"],
            "payback_month": s["payback_month"],
        })

    st.download_button(
        "Скачать summary CSV",
        data=to_csv_bytes(pd.DataFrame(scenario_export)),
        file_name="pnl_v4_summary.csv",
        mime="text/csv",
    )

st.caption(
    "Логика v4 основана на листе Excel 'Динамика_инд+гр (12 мес)+кросс-': LTV и Churn взаимосвязаны, "
    "база учеников считается помесячно, а агентская комиссия вычитается до расчета чистой прибыли [file:133]."
)
