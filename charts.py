# charts.py
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


def apply_plotly_theme():
    pio.templates["school_v4"] = go.layout.Template(
        layout=go.Layout(
            font=dict(
                family="Inter, Arial, sans-serif",
                size=12,
                color="#111827"
            ),
            title=dict(
                font=dict(size=18, color="#111827"),
                x=0.01,
                xanchor="left"
            ),
            paper_bgcolor="white",
            plot_bgcolor="white",
            colorway=["#2563eb", "#f59e0b", "#16a34a", "#ef4444", "#8b5cf6", "#6b7280"],
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                automargin=True
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#e5e7eb",
                zeroline=False,
                automargin=True
            ),
            margin=dict(l=20, r=20, t=80, b=30),
        )
    )
    pio.templates.default = "school_v4"


def _legend_top():
    return dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        font=dict(size=11),
        entrywidth=90,
    )


def revenue_profit_chart_v4(results):
    fig = go.Figure()

    colors = {
        "Разовый %": "#2563eb",
        "RevShare": "#f59e0b",
        "CPA": "#16a34a",
    }
    short = {
        "Разовый %": "%",
        "RevShare": "Rev",
        "CPA": "CPA",
    }

    for scenario_name, pack in results.items():
        df = pack["monthly"]
        suffix = short[scenario_name]

        fig.add_trace(
            go.Bar(
                x=df["label"],
                y=df["revenue_total"] + df["upsell_revenue"],
                name=f"Выручка • {suffix}",
                marker_color=colors[scenario_name],
                opacity=0.38,
                legendgroup=scenario_name,
                hovertemplate="%{x}<br>Выручка: %{y:,.0f} ₽<extra></extra>",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df["label"],
                y=df["net_profit"],
                mode="lines+markers",
                name=f"ЧП • {suffix}",
                line=dict(color=colors[scenario_name], width=3),
                marker=dict(size=7),
                legendgroup=scenario_name,
                hovertemplate="%{x}<br>Чистая прибыль: %{y:,.0f} ₽<extra></extra>",
            )
        )

    fig.update_layout(
        title="Выручка и чистая прибыль по месяцам",
        barmode="group",
        height=540,
        xaxis_title="Месяц",
        yaxis_title="₽",
        hovermode="x unified",
        legend=_legend_top(),
        margin=dict(l=20, r=20, t=95, b=25),
    )
    return fig


def cashflow_chart_v4(df, title="Окупаемость / Cash Flow"):
    fig = go.Figure(
        go.Waterfall(
            x=df["label"].tolist() + ["Итого"],
            y=df["net_cash_flow"].tolist() + [0],
            measure=["relative"] * len(df) + ["total"],
            connector={"line": {"color": "rgba(90,90,90,0.35)"}},
            increasing={"marker": {"color": "#16a34a"}},
            decreasing={"marker": {"color": "#dc2626"}},
            totals={"marker": {"color": "#2563eb"}},
            hovertemplate="%{x}<br>Cash flow: %{y:,.0f} ₽<extra></extra>",
        )
    )

    fig.update_layout(
        title=title,
        height=500,
        xaxis_title="Месяц",
        yaxis_title="₽",
        showlegend=False,
        margin=dict(l=20, r=20, t=75, b=25),
    )
    return fig


def expense_pie_v4(expense_df):
    fig = px.pie(
        expense_df,
        names="category",
        values="value",
        hole=0.58,
        title="Структура расходов",
        color="category",
        color_discrete_map={
            "ФОТ": "#3b82f6",
            "Комиссия агентства": "#f59e0b",
            "Маркетинг": "#8b5cf6",
            "Налоги и эквайринг": "#ef4444",
            "Постоянные расходы": "#6b7280",
            "Чистая прибыль": "#10b981",
        },
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        insidetextfont=dict(size=11),
        sort=False,
        hovertemplate="%{label}<br>%{value:,.0f} ₽<br>%{percent}<extra></extra>",
    )

    fig.update_layout(
        height=520,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="left",
            x=0,
            font=dict(size=11),
            entrywidth=110,
        ),
        margin=dict(l=20, r=20, t=100, b=25),
    )
    return fig
