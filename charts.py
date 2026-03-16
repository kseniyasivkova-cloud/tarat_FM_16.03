# charts.py
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


def apply_plotly_theme():
    pio.templates["school"] = go.layout.Template(
        layout=go.Layout(
            font=dict(family="Inter, Arial, sans-serif", size=12, color="#111827"),
            title=dict(font=dict(size=18, color="#111827")),
            paper_bgcolor="white",
            plot_bgcolor="white",
            colorway=["#2563eb", "#16a34a", "#f59e0b", "#ef4444", "#8b5cf6", "#6b7280"],
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="#e5e7eb", zeroline=False),
            margin=dict(l=20, r=20, t=70, b=20),
        )
    )
    pio.templates.default = "school"


def revenue_profit_chart(results):
    fig = go.Figure()
    colors = {"Разовый %": "#2563eb", "RevShare": "#f59e0b", "CPA": "#16a34a"}
    short = {"Разовый %": "%", "RevShare": "Rev", "CPA": "CPA"}

    for name, pack in results.items():
        df = pack["monthly"]
        s = short[name]

        fig.add_trace(go.Bar(
            x=df["label"],
            y=df["revenue"],
            name=f"Выручка • {s}",
            marker_color=colors[name],
            opacity=0.38,
            legendgroup=name,
        ))
        fig.add_trace(go.Scatter(
            x=df["label"],
            y=df["net_profit"],
            mode="lines+markers",
            name=f"ЧП • {s}",
            line=dict(color=colors[name], width=3),
            legendgroup=name,
        ))

    fig.update_layout(
        title="Выручка и чистая прибыль по месяцам",
        barmode="group",
        height=520,
        xaxis_title="Месяц",
        yaxis_title="₽",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11)
        ),
        margin=dict(l=20, r=20, t=90, b=20),
    )
    return fig


def cashflow_waterfall(df, title):
    fig = go.Figure(go.Waterfall(
        x=df["label"].tolist() + ["Итого"],
        y=df["net_cash_flow"].tolist() + [0],
        measure=["relative"] * len(df) + ["total"],
        connector={"line": {"color": "rgba(80,80,80,0.35)"}},
        increasing={"marker": {"color": "#16a34a"}},
        decreasing={"marker": {"color": "#dc2626"}},
        totals={"marker": {"color": "#2563eb"}},
    ))
    fig.update_layout(
        title=title,
        height=500,
        xaxis_title="Месяц",
        yaxis_title="₽",
        margin=dict(l=20, r=20, t=70, b=20),
    )
    return fig


def expense_pie(expense_df, title):
    fig = px.pie(
        expense_df,
        names="category",
        values="value",
        hole=0.58,
        title=title,
        color="category",
        color_discrete_map={
            "ФОТ": "#3b82f6",
            "Комиссия агентства": "#f59e0b",
            "Маркетинг": "#8b5cf6",
            "Налоги и эквайринг": "#ef4444",
            "Постоянные расходы": "#6b7280",
            "Чистая прибыль": "#10b981",
        }
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        insidetextfont=dict(size=11),
        sort=False
    )

    fig.update_layout(
        height=460,
        title="Структура расходов",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11)
        ),
        margin=dict(l=20, r=20, t=90, b=20),
    )
    return fig
