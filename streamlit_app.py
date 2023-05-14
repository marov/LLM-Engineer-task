import json
import pandas as pd
import streamlit as st
from langchain.llms import OpenAI
from langchain.agents import create_csv_agent, create_pandas_dataframe_agent

"""
# Employee health insurance :hospital: :factory:
"""


TRANSFORM_CODE_TEMPLATE = """
import pandas as pd
import json
def transform(df):
    # apply mapping_code and col_transform_code to `TABLE_NAME`
    df = pd.read_csv("TABLE_NAME")
    _columns = json.loads('MAPPING_JSON')
    df.rename(columns=_columns, inplace=True)
    df = df[pd.read_csv("template.csv").columns]
    # Keep the first occurrence of each duplicated column
    df = df.loc[:, ~df.columns.duplicated(keep='first')]
    df['Date'] = pd.to_datetime(df['Date'])
    COL_TRANSFORM_CODE
    return df
"""


@st.cache_data()
def map_columns(pswd, table_name):
    agent = create_csv_agent(OpenAI(temperature=0, openai_api_key=pswd, model_name="text-davinci-003"), table_name, verbose=True)
    mapping_to_template = agent.run(f"Load template_df with template_df = pd.read_csv('template.csv'). \
            Compute sequence similarity between all possible pairs of columns from two dataframes. \
            Pair columns when ratios when ratio is positive.")
    mapping_json = agent.run(f"{mapping_to_template}. Use this info to create JSON with column mapping. Print this JSON").replace('\'','"')
    not_matched = list(template_df.columns.difference(json.loads(mapping_json).values()))
    matched_to = agent.run(f"Find columns in df best matching to {not_matched}. Print as a list").replace('\'','"')
    mapping_missing = dict(zip(json.loads(matched_to), not_matched))
    _columns = json.loads(mapping_json)
    _columns.update(mapping_missing)
    return _columns

@st.cache_data()
def format_columns(pswd, df):
    df.rename(columns=_columns, inplace=True)
    df = df[pd.read_csv("template.csv").columns]
    # Keep the first occurrence of each duplicated column
    df = df.loc[:, ~df.columns.duplicated(keep='first')]
    df['Date'] = pd.to_datetime(df['Date'])
    agent = create_pandas_dataframe_agent(OpenAI(temperature=0, openai_api_key=pswd, model_name="text-davinci-003"), df, verbose=True)
    col_transform_code = agent.run(f"Make the formatting of every columns match the correcponding column in {template_df}. Output the code")
    return col_transform_code.replace('\n', '\n    ') # indent

@st.cache_data()
def gen_transform_code(pswd, table_name, col_transform_code):
    transform_code = TRANSFORM_CODE_TEMPLATE.replace("MAPPING_JSON",
        json.dumps(_columns)).replace("COL_TRANSFORM_CODE", col_transform_code).replace("TABLE_NAME", table_name)
    return transform_code

pswd = st.text_input("OpenAI API key:", type="password")

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
    st.markdown("<h3 style='color: brown;'>Mapping of the columns:</h3>", unsafe_allow_html=True)
    _columns = map_columns(pswd, table.name)
    st.json(_columns)
    if st.button("Generate transformation code"):
        col_transform_code = format_columns(pswd, table_df)
        transform_code = gen_transform_code(pswd, table.name, col_transform_code)
        st.code(transform_code, language="python")
        st.session_state["code_gen"] = True
    if st.session_state.get("code_gen", False):
        if st.button("Apply transformation"):
            st.write("Applying transformation...")
            col_transform_code = format_columns(pswd, table_df)
            transform_code = gen_transform_code(pswd, table.name, col_transform_code)
            exec(transform_code)
            table_df = transform(table_df)
            st.dataframe(table_df)
            st.markdown("<h3 style='color: green;'>Success!</h3>", unsafe_allow_html=True)
