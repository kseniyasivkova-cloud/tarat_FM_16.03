# model.py
import math
import pandas as pd


MONTHS = list(range(1, 13))


def safe_div(a, b):
    return a / b if b else 0.0


def calc_payback_month(cumulative_series):
    for i, v in enumerate(cumulative_series, start=1):
        if v >= 0:
            return i
    return None


def build_monthly_new_students(ad_budget_m1, cpl, growth_new_sales, trial_conv, sale_conv):
    rows = []
    for m in MONTHS:
        leads = round((ad_budget_m1 * ((1 + growth_new_sales) ** (m - 1))) / cpl) if cpl > 0 else 0
        trials = round(leads * trial_conv)
        sales = round(trials * sale_conv)
        budget = round(leads * cpl)
        rows.append({
            "month": m,
            "ad_budget": budget,
            "leads": leads,
            "trials": trials,
            "new_students": sales,
        })
    return pd.DataFrame(rows)


def simulate_one_scenario(params, scenario_name):
    start_students = params["start_students"]
    growth_new_sales = params["growth_new_sales"]
    ad_budget_m1 = params["ad_budget_m1"]
    cpl = params["cpl"]
    trial_conv = params["trial_conv"]
    sale_conv = params["sale_conv"]

    ltv_months = params["ltv_months"]
    churn = params["churn"]

    group_share = params["group_share"]
    indiv_share = 1 - group_share

    indiv_price_month = params["indiv_price_month"]
    indiv_lesson_price = params["indiv_lesson_price"]
    indiv_tutor_lesson_cost = params["indiv_tutor_lesson_cost"]

    group_price_month = params["group_price_month"]
    group_lessons_month = params["group_lessons_month"]
    group_lesson_price = params["group_lesson_price"]
    group_monthly_cost = params["group_monthly_cost"]
    group_limit = params["group_limit"]

    upsell_conv = params["upsell_conv"]
    upsell_price = params["upsell_price"]
    upsell_cost = params["upsell_cost"]

    tax_rate = params["tax_rate"]
    acquiring_rate = params["acquiring_rate"]
    fixed_opex = params["fixed_opex"]
    capex = params["capex"]

    agency_new_pct = params["agency_new_pct"]
    agency_revshare = params["agency_revshare"]
    agency_cpa = params["agency_cpa"]

    funnel_df = build_monthly_new_students(
        ad_budget_m1=ad_budget_m1,
        cpl=cpl,
        growth_new_sales=growth_new_sales,
        trial_conv=trial_conv,
        sale_conv=sale_conv,
    )

    rows = []
    start_base = start_students
    cumulative_cash = -capex

    cumulative_new = 0
    cumulative_new_retained = 0
    retained_new_cohorts = []

    for m in MONTHS:
        r = funnel_df.iloc[m - 1]
        ad_budget = float(r["ad_budget"])
        leads = float(r["leads"])
        trials = float(r["trials"])
        new_students = float(r["new_students"])

        churned_students = round(start_base * churn)
        active_students = start_base + new_students - churned_students

        cumulative_new += new_students

        retained_value = new_students
        retained_new_cohorts.append(retained_value)

        retained_sum = 0
        active_cohorts = []
        for idx, cohort_size in enumerate(retained_new_cohorts):
            age = len(retained_new_cohorts) - idx - 1
            if age < ltv_months:
                retained_after_churn = cohort_size * ((1 - churn) ** age)
                active_cohorts.append(cohort_size)
                retained_sum += retained_after_churn

        cumulative_new_retained = retained_sum

        indiv_students = round(active_students * indiv_share)
        group_students = active_students - indiv_students
        groups_count = group_students / group_limit if group_limit > 0 else 0

        revenue_indiv = indiv_students * indiv_price_month
        revenue_group = group_students * group_price_month
        revenue_total = revenue_indiv + revenue_group

        indiv_lessons_month = indiv_price_month / indiv_lesson_price if indiv_lesson_price > 0 else 0
        payroll_indiv = indiv_students * indiv_lessons_month * indiv_tutor_lesson_cost

        payroll_group = groups_count * group_monthly_cost
        gross_profit_indiv = revenue_indiv - payroll_indiv
        gross_profit_group = revenue_group - payroll_group
        gross_profit_total = gross_profit_indiv + gross_profit_group

        taxes_main = revenue_total * tax_rate
        acquiring_main = revenue_total * acquiring_rate
        margin_profit_before_marketing = gross_profit_total - taxes_main - acquiring_main

        upsell_buyers = round(active_students * upsell_conv)
        upsell_revenue = upsell_buyers * upsell_price
        upsell_payroll = upsell_buyers * upsell_cost
        upsell_gross_profit = upsell_revenue - upsell_payroll
        upsell_taxes = upsell_revenue * tax_rate
        upsell_acquiring = upsell_revenue * acquiring_rate
        cross_sell_profit = upsell_gross_profit - upsell_taxes - upsell_acquiring

        new_indiv = round(new_students * indiv_share)
        new_group = new_students - new_indiv
        new_revenue = (new_indiv * indiv_price_month) + (new_group * group_price_month)

        if scenario_name == "Разовый %":
            agency_fee = new_revenue * agency_new_pct
        elif scenario_name == "RevShare":
            agency_fee = revenue_total * agency_revshare
        else:
            agency_fee = new_students * agency_cpa

        operating_profit = margin_profit_before_marketing - ad_budget - agency_fee
        total_oper_profit = operating_profit + cross_sell_profit
        net_profit = total_oper_profit - fixed_opex
        net_cash_flow = net_profit - (capex if m == 1 else 0)
        cumulative_cash += net_profit if m > 1 else net_cash_flow

        rows.append({
            "month": m,
            "label": f"M{m}",
            "scenario": scenario_name,
            "ad_budget": ad_budget,
            "leads": leads,
            "trials": trials,
            "new_students": new_students,
            "start_base": start_base,
            "churned_students": churned_students,
            "active_students": active_students,
            "cumulative_new_students": cumulative_new,
            "cumulative_new_retained": cumulative_new_retained,
            "indiv_students": indiv_students,
            "group_students": group_students,
            "groups_count": groups_count,
            "revenue_indiv": revenue_indiv,
            "revenue_group": revenue_group,
            "revenue_total": revenue_total,
            "payroll_indiv": payroll_indiv,
            "payroll_group": payroll_group,
            "gross_profit_indiv": gross_profit_indiv,
            "gross_profit_group": gross_profit_group,
            "gross_profit_total": gross_profit_total,
            "taxes_main": taxes_main,
            "acquiring_main": acquiring_main,
            "margin_profit_before_marketing": margin_profit_before_marketing,
            "marketing_cost": ad_budget,
            "agency_fee": agency_fee,
            "operating_profit": operating_profit,
            "upsell_buyers": upsell_buyers,
            "upsell_revenue": upsell_revenue,
            "upsell_payroll": upsell_payroll,
            "cross_sell_profit": cross_sell_profit,
            "total_oper_profit": total_oper_profit,
            "fixed_opex": fixed_opex,
            "net_profit": net_profit,
            "net_cash_flow": net_cash_flow,
            "cumulative_cash": cumulative_cash,
            "gross_margin": safe_div(gross_profit_total, revenue_total),
            "margin_rate": safe_div(total_oper_profit, revenue_total + upsell_revenue),
            "net_margin": safe_div(net_profit, revenue_total + upsell_revenue),
        })

        start_base = active_students

    df = pd.DataFrame(rows)

    expense_mix = pd.DataFrame({
        "category": [
            "ФОТ",
            "Комиссия агентства",
            "Маркетинг",
            "Налоги и эквайринг",
            "Постоянные расходы",
            "Чистая прибыль",
        ],
        "value": [
            df["payroll_indiv"].sum() + df["payroll_group"].sum() + df["upsell_payroll"].sum(),
            df["agency_fee"].sum(),
            df["marketing_cost"].sum(),
            df["taxes_main"].sum() + df["acquiring_main"].sum(),
            df["fixed_opex"].sum(),
            max(df["net_profit"].sum(), 0),
        ],
    })

    summary = {
        "revenue_m12": df.iloc[-1]["revenue_total"] + df.iloc[-1]["upsell_revenue"],
        "net_profit_m12": df.iloc[-1]["net_profit"],
        "gross_margin_m12": df.iloc[-1]["gross_margin"],
        "margin_rate_m12": df.iloc[-1]["margin_rate"],
        "net_margin_m12": df.iloc[-1]["net_margin"],
        "active_students_m12": df.iloc[-1]["active_students"],
        "new_students_year": df["new_students"].sum(),
        "payback_month": calc_payback_month(df["cumulative_cash"].tolist()),
    }

    return {
        "monthly": df,
        "summary": summary,
        "expense_mix": expense_mix,
    }


def simulate_excel_model(params):
    return {
        "Разовый %": simulate_one_scenario(params, "Разовый %"),
        "RevShare": simulate_one_scenario(params, "RevShare"),
        "CPA": simulate_one_scenario(params, "CPA"),
    }
