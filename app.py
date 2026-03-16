# app.py
import math
import pandas as pd
import streamlit as st

from model import simulate_excel_model
from charts import apply_plotly_theme, revenue_profit_chart_v4, cashflow_chart_v4, expense_pie_v4
from utils import rub, pct, to_csv_bytes

st.set_page_config(
    page_title="Online School P&L Pro v4",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_plotly_theme()

st.title("Online School P&L Pro")
st.caption("Версия v4 — логика приведена к Excel-модели Taratorkina")

with st.sidebar:
    st.header("Управляющие параметры")

    st.subheader("1. Воронка продаж")
    start_students = st.slider("База на начало периода, учеников", 0, 300, 90, 1)
    growth_new_sales = st.slider("Ежемесячный рост новых продаж", 0.00, 0.30, 0.20, 0.01, format="%.0f%%")
    ad_budget_m1 = st.slider("Рекламный бюджет M1, ₽", 0, 500_000, 130_000, 5_000)
    cpl = st.slider("Стоимость лида (CPL), ₽", 500, 10_000, 2_500, 100)
    trial_conv = st.slider("Конверсия лид -> пробный", 0.10, 1.00, 0.50, 0.01, format="%.0f%%")
    sale_conv = st.slider("Конверсия пробный -> продажа", 0.10, 1.00, 0.50, 0.01, format="%.0f%%")

    st.subheader("2. База и удержание")
    ltv_months = st.slider("Срок жизни ученика / LTV, мес", 1, 12, 7, 1)
    churn = 1 / ltv_months if ltv_months > 0 else 0.0
    st.metric("Расчетный Churn в месяц", f"{churn:.2%}")

    st.subheader("3. Продукт и формат")
    group_share = st.slider("Доля учеников в мини-группах", 0.00, 1.00, 0.50, 0.05, format="%.0f%%")
    indiv_price_month = st.slider("Средний чек индивид, ₽/мес", 5_000, 60_000, 28_000, 500)
    indiv_lesson_price = st.slider("Стоимость 1 занятия для клиента (индив), ₽", 500, 10_000, 3_500, 100)
    indiv_tutor_lesson_cost = st.slider("Ставка препода за 1 занятие (индив), ₽", 500, 5_000, 2_000, 100)

    group_price_month = st.slider("Средний чек мини-группы, ₽/мес", 5_000, 60_000, 16_000, 500)
    group_lessons_month = st.slider("Кол-во занятий в мес (группа)", 1, 16, 8, 1)
    group_lesson_price = st.slider("Стоимость 1 занятия для клиента (группа), ₽", 500, 10_000, 2_000, 100)
    group_monthly_cost = st.slider("Ставка препода за месяц с 1 группы, ₽", 5_000, 50_000, 16_000, 500)
    group_limit = st.slider("Лимит учеников в группе", 3, 8, 4, 1)

    st.subheader("4. Кросс-сейл")
    upsell_conv = st.slider("Конверсия в покупку доп. услуги", 0.00, 0.50, 0.20, 0.01, format="%.0f%%")
    upsell_price = st.slider("Средний чек доп. услуги, ₽", 500, 20_000, 3_500, 100)
    upsell_cost = st.slider("Себестоимость / ФОТ доп. услуги на 1 чел, ₽", 0, 10_000, 2_000, 100)

    st.subheader("5. Налоги и постоянные")
    tax_rate = st.slider("Налог УСН", 0.00, 0.20, 0.07, 0.005, format="%.1f%%")
    acquiring_rate = st.slider("Эквайринг", 0.00, 0.05, 0.025, 0.001, format="%.1f%%")
    fixed_opex = st.slider("Постоянные расходы, ₽/мес", 0, 300_000, 40_000, 5_000)
    capex = st.slider("CAPEX в 1-й месяц, ₽", 0, 500_000, 70_000, 5_000)

    st.subheader("6. Агентская комиссия")
    active_scenario = st.selectbox("Активный сценарий", ["Разовый %", "RevShare", "CPA"])
    agency_new_pct = st.slider("Сценарий 1: % от новых привлеченных", 0.40, 0.60, 0.50, 0.01, format="%.0f%%")
    agency_revshare = st.slider("Сценарий 2: RevShare от выручки", 0.10, 0.25, 0.15, 0.01, format="%.0f%%")
    agency_cpa = st.slider("Сценарий 3: CPA за нового ученика, ₽", 1_000, 20_000, 9_000, 500)

params = {
    "start_students": start_students,
    "growth_new_sales": growth_new_sales,
    "ad_budget_m1": ad_budget_m1,
    "cpl": cpl,
    "trial_conv": trial_conv,
    "sale_conv": sale_conv,
    "ltv_months": ltv_months,
    "churn": churn,
    "group_share": group_share,
    "indiv_price_month": indiv_price_month,
    "indiv_lesson_price": indiv_lesson_price,
    "indiv_tutor_lesson_cost": indiv_tutor_lesson_cost,
    "group_price_month": group_price_month,
    "group_lessons_month": group_lessons_month,
    "group_lesson_price": group_lesson_price,
    "group_monthly_cost": group_monthly_cost,
    "group_l
