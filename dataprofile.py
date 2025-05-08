import streamlit as st
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import openai
import base64
import warnings
warnings.filterwarnings("ignore")

# Load API Key
load_dotenv()
openai.api_key = ''

# Streamlit UI
st.title("Prompt-driven Data Profiling")
uploaded_file = st.file_uploader("Upload a CSV file for analysis", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("**Preview of Uploaded Data**")
    st.dataframe(df.head(3))

    filename = "data_profile_" + uploaded_file.name.split('.')[0] + ".xlsx"

    # Column classification
    num_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    cat_columns = df.select_dtypes(include=['object']).columns.tolist()
    date_columns = df.select_dtypes(include=['datetime', 'datetime64']).columns.tolist()

    # Exclude likely ID cols
    likely_id_cols = [col for col in df.columns if df[col].nunique() == df.shape[0]]
    for col in likely_id_cols:
        if col in num_columns:
            num_columns.remove(col)

    # Write Excel with Pandas summary
    with pd.ExcelWriter(filename) as writer:
        df.describe().to_excel(writer, sheet_name="Statistics")

        summary_df = pd.DataFrame({
            'Feature': df.columns,
            'Data Type': [df[col].dtype for col in df.columns],
            'Number of Unique Values': [df[col].nunique() for col in df.columns],
            'Sample Value': [df[col].iloc[0] for col in df.columns],
            'Contains Nulls': [df[col].isnull().any() for col in df.columns]
        })
        summary_df.to_excel(writer, sheet_name="Summary")

        missing_counts = df.isnull().sum()
        not_missing_counts = df.shape[0] - missing_counts
        missing_percentage = (missing_counts / df.shape[0]) * 100
        missing_df = pd.DataFrame({
            'Column': df.columns,
            'Missing Values': missing_counts.values,
            'Not Missing Values': not_missing_counts.values,
            'Percentage Missing': missing_percentage.values
        })
        missing_df.to_excel(writer, sheet_name="Null Values")

    with open(filename, "rb") as f:
        st.download_button(
            label="Download Data Profile as Excel",
            data=f.read(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Tabs
    tab_prompt, tab_eda, tab_stats, tab_summary, tab_null = st.tabs(["Prompt Analysis", "EDA", "Statistics", "Summary", "Null Values"])

    # Prompt Analysis with GPT
    with tab_prompt:
        prompt = st.text_area("Enter your prompt")
        if st.button("Generate"):
            if prompt:
                with st.spinner("Generating response..."):
                    sample_data = df.head(5).to_string()
                    messages = [
                        {"role": "system", "content": "You are a data profiling assistant."},
                        {"role": "user", "content": f"Here is a sample of the dataset:\n{sample_data}\n\n{prompt}"}
                    ]
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1200
                    )
                    result = response['choices'][0]['message']['content']
                    st.markdown("### Response")
                    st.markdown(result)
            else:
                st.warning("Please enter a prompt.")

    # EDA tab
    with tab_eda:
        st.subheader("Visual EDA")
        for col in num_columns:
            fig, ax = plt.subplots()
            sns.histplot(df[col], kde=True, ax=ax)
            st.pyplot(fig)

        for col in cat_columns:
            if df[col].nunique() <= 20:
                fig, ax = plt.subplots()
                sns.countplot(y=df[col], ax=ax)
                st.pyplot(fig)

        if len(num_columns) >= 2 and len(cat_columns) >= 1:
            fig, ax = plt.subplots()
            sns.scatterplot(x=df[num_columns[0]], y=df[num_columns[1]], hue=df[cat_columns[0]], ax=ax)
            st.pyplot(fig)

        for date_col in date_columns:
            for num_col in num_columns:
                fig, ax = plt.subplots()
                sns.lineplot(x=df[date_col], y=df[num_col], ax=ax)
                st.pyplot(fig)

        if len(num_columns) >= 2:
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(df[num_columns].corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)

    # Statistics tab
    with tab_stats:
        st.dataframe(df.describe())

    # Summary tab
    with tab_summary:
        st.dataframe(summary_df)

    # Null Values tab
    with tab_null:
        st.dataframe(missing_df)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(missing_df['Column'], missing_df['Not Missing Values'], label='Not Missing', color='blue')
        ax.bar(missing_df['Column'], missing_df['Missing Values'], bottom=missing_df['Not Missing Values'], label='Missing', color='red')
        ax.set_xticklabels(missing_df['Column'], rotation=45, ha='right')
        ax.set_ylabel("Count")
        ax.set_title("Proportion of Missing Values in Each Column")
        ax.legend()
        st.pyplot(fig)
