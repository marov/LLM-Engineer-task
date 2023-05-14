import pandas as pd
import streamlit as st
from langchain.llms import OpenAI
from langchain.agents import create_csv_agent, create_pandas_dataframe_agent

"""
# Employee health insurance :hospital: :factory:
"""

st.markdown("<h3 style='color: blue;'>Upload teplate file</h3>", unsafe_allow_html=True)
template = st.file_uploader("1", type=["csv"])
if template is not None:
    template_df = pd.read_csv(template)
    st.dataframe(template_df)

st.markdown("<h3 style='color: blue;'>Upload table file</h3>", unsafe_allow_html=True)
table = st.file_uploader("2", type=["csv"])
if table is not None:
    table_df = pd.read_csv(table)
    st.dataframe(table_df)
    st.markdown("<h3 style='color: brown;'>Mapping:</h3>", unsafe_allow_html=True)

# template_df = pd.read_csv(template)
# tabel_agent = create_csv_agent(tabel)
