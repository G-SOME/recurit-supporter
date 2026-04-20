import streamlit as st


def render_evidence(lines: list[str]):
    for line in lines:
        st.write(f"- {line}")
