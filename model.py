# model.py
import math
import pandas as pd


MONTHS = list(range(1, 13))


def safe_div(a, b):
    return a / b if b else 0.0


def get_payback_month(cumulative_cash):
    for i, v in enumerate(cumulative_cash, start=1):
        if v >= 0:
            return i
    return None


def simulate_scenario(params, scenario_name, agency_mode):
    budget0 = params["ad_budget"]
    cpl = params["cpl"]
    growth = params["growth"]
    sale_conv = params["sale_conv"]
    ltv_months = params["ltv_months"]
    churn = params["churn"]

    group_share = params["group_share"]
    indiv_share = 1 - group_share

    indiv_price = params["indiv_price"]
    group_price = params["group_price"]
    indiv_tutor_cost = params["indiv_tutor_cost"]
    group_monthly_cost = params["group_monthly_cost"]
    group_limit = params["group_limit"]
    lessons = params["lessons_per_month"]

    upsell_conv = params["upsell_conv"]
    upsell_price = params["upsell_price"]
    upsell_cost = params["upsell_cost"]

    tax_rate = params["tax_rate"]
    acquiring_rate = params["acquiring_rate"]
    opex = params["opex"]
    capex = params["capex"]

    agency_pct_new = params["agency_pct_new"]
    agency_revshare = params["agency_revshare"]
    agency_cpa = params["agency_cpa"]

    cohorts = []
    rows = []
    cumulative_cash = 0.0

    for m in MONTHS:
        if budget0 == 0:
            budget = 0.0
            leads = 0.0
            new_students = 0.0
        else:
            budget = budget0 * ((1 + growth) ** (m - 1))
            leads = safe_div(budget, cpl)
            new_students = leads * sale_conv

        cohorts.append({"month": m, "students0": new_students})

        active_students = 0.0
        active_indiv = 0.0
        active_group = 0.0
        new_students_this_month = 0.0

        for cohort in cohorts:
            age = m - cohort["month"]
            if age < 0 or age >= ltv_months:
                continue

            retained = cohort["students0"] * ((1 - churn) ** age)
            active_students += retained
            active_indiv += retained * indiv_share
            active_group += retained * group_share

            if age == 0:
                new_students_this_month += retained

        indiv_revenue = active_indiv * lessons * indiv_price
        group_revenue = active_group * lessons * group_price
        core_revenue = indiv_revenue + group_revenue

        upsell_buyers = active_students * upsell_conv
        upsell_revenue = upsell_buyers * upsell_price
        upsell_payroll = upsell_buyers * upsell_cost

        indiv_payroll = active_indiv * lessons * indiv_tutor_cost
        groups_count = math.ceil(active_group / group_limit) if active_group > 0 else 0
        group_payroll = groups_count * group_monthly_cost
        tutor_payroll = indiv_payroll + group_payroll

        new_indiv = new_students_this_month * indiv_share
        new_group = new_students_this_month * group_share
        new_customer_revenue = (new_indiv * lessons * indiv_price) + (new_group * lessons * group_price)

        revenue = core_revenue + upsell_revenue

        if agency_mode == "pct_new":
            agency_fee = new_customer_revenue * agency_pct_new
        elif agency_mode == "revshare":
            agency_fee = revenue * agency_revshare
        else:
            agency_fee = new_students_this_month * agency_cpa

        taxes = revenue * tax_rate
        acquiring = revenue * acquiring_rate

        gross_profit = revenue - tutor_payroll - upsell_payroll
        margin_profit = gross_profit - budget - agency_fee - taxes - acquiring
        net_profit = margin_profit - opex
        capex_month = capex if m == 1 else 0.0
        net_cash_flow = net_profit - capex_month
        cumulative_cash += net_cash_flow

        rows.append({
            "month": m,
            "label": f"M{m}",
            "scenario": scenario_name,
            "budget": budget,
            "leads": leads,
            "new_students": new_students_this_month,
            "active_students": active_students,
            "active_indiv": active_indiv,
            "active_group": active_group,
            "groups_count": groups_count,
            "indiv_revenue": indiv_revenue,
            "group_revenue": group_revenue,
            "upsell_revenue": upsell_revenue,
            "revenue": revenue,
            "tutor_payroll": tutor_payroll,
            "upsell_payroll": upsell_payroll,
            "agency_fee": agency_fee,
            "taxes": taxes,
            "acquiring": acquiring,
            "opex": opex,
            "gross_profit": gross_profit,
            "margin_profit": margin_profit,
            "net_profit": net_profit,
            "capex": capex_month,
            "net_cash_flow": net_cash_flow,
            "cumulative_cash": cumulative_cash,
            "gross_margin": safe_div(gross_profit, revenue),
            "margin_rate": safe_div(margin_profit, revenue),
            "net_margin": safe_div(net_profit, revenue),
        })

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
            df["tutor_payroll"].sum() + df["upsell_payroll"].sum(),
            df["agency_fee"].sum(),
            df["budget"].sum(),
            df["taxes"].sum() + df["acquiring"].sum(),
            df["opex"].sum(),
            max(df["net_profit"].sum(), 0),
        ],
    })

    summary = {
        "scenario": scenario_name,
        "revenue_m12": df.iloc[-1]["revenue"],
        "net_profit_m12": df.iloc[-1]["net_profit"],
        "gross_margin_m12": df.iloc[-1]["gross_margin"],
        "margin_rate_m12": df.iloc[-1]["margin_rate"],
        "net_margin_m12": df.iloc[-1]["net_margin"],
        "cash_m12": df.iloc[-1]["cumulative_cash"],
        "payback_month": get_payback_month(df["cumulative_cash"].tolist()),
    }

    return {
        "monthly": df,
        "expense_mix": expense_mix,
        "summary": summary,
    }


def simulate_all_scenarios(params):
    return {
        "Разовый %": simulate_scenario(params, "Разовый %", "pct_new"),
        "RevShare": simulate_scenario(params, "RevShare", "revshare"),
        "CPA": simulate_scenario(params, "CPA", "cpa"),
    }
