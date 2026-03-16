# charts.py
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


def apply_plotly_theme():
    pio.templates["school"] = go.layout.Template(
        layout=go.Layout(
            font=dict(family="Inter, Arial, sans-serif", size=13, color="#111827"),
            title=dict(font=dict(size=20, color="#111827")),
            paper_bgcolor="white",
            plot_bgcolor="white",
            colorway=["#2563eb", "#16a34a", "#f59e0b", "#ef4444", "#8b5cf6", "#6b7280"],
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="#e5e7eb", zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=10, r=10, t=60, b=10),
        )
    )
    pio.templates.default = "school"


def revenue_profit_chart(results):
    fig = go.Figure()
    colors = {"Разовый %": "#2563eb", "RevShare": "#f59e0b", "CPA": "#16a34a"}

    for name, pack in results.items():
        df = pack["monthly"]
        fig.add_trace(go.Bar(
            x=df["label"],
            y=df["revenue"],
            name=f"Выручка — {name}",
            marker_color=colors[name],
            opacity=0.40,
            legendgroup=name,
        ))
        fig.add_trace(go.Scatter(
            x=df["label"],
            y=df["net_profit"],
            mode="lines+markers",
            name=f"Чистая прибыль — {name}",
            line=dict(color=colors[name], width=3),
            legendgroup=name,
        ))

    fig.update_layout(
        title="Выручка vs чистая прибыль по месяцам",
        barmode="group",
        height=500,
        xaxis_title="Месяц",
        yaxis_title="₽",
        hovermode="x unified",
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
        height=460,
        xaxis_title="Месяц",
        yaxis_title="₽",
    )
    return fig


def expense_pie(expense_df, title):
    fig = px.pie(
        expense_df,
        names="category",
        values="value",
        hole=0.52,
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
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=420)
    return fig
