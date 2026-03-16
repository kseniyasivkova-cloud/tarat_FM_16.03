# utils.py
import pandas as pd
import streamlit as st


def rub(x):
    try:
        return f"{float(x):,.0f} ₽".replace(",", " ")
    except Exception:
        return "—"


def pct(x):
    try:
        return f"{float(x):.1%}"
    except Exception:
        return "—"


@st.cache_data
def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")
