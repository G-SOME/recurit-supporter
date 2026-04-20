import streamlit as st


def render_score_card(title: str, score: float):
    st.metric(title, f"{score:.1f}")
