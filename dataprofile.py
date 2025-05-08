import streamlit as st
import os
import pandas as pd
import base64
from dotenv import load_dotenv
import openai

# Load OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Streamlit UI ---
st.title("Prompt-driven Data Profiling")

uploaded_file = st.file_uploader("Upload a CSV file for analysis", type=['csv'])

# Read CSV
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("**Preview of Uploaded Data**")
    st.dataframe(df.head(3))

    filename = "data_profile_" + uploaded_file.name.split('.')[0] + ".xlsx"
    data_sample = df.head(5).to_string()

    # --- Define Tabs ---
    tab_prompt, tab_eda, tab_stats, tab_summary, tab_null = st.tabs(["Prompt Analysis", "EDA", "Statistics", "Summary", "Null Values"])

    # --- Prompt Tab ---
    with tab_prompt:
        prompt = st.text_area("Enter your prompt:")
        if st.button("Generate"):
            if prompt:
                with st.spinner("Generating response..."):
                    messages = [
                        {"role": "system", "content": "You are a data profiling assistant. Generate concise, structured insights."},
                        {"role": "user", "content": f"Here is the dataset sample:\n{data_sample}\n\n{prompt}"}
                    ]
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1200
                    )
                    result = response['choices'][0]['message']['content']
                    st.markdown("### Result:")
                    st.markdown(result)
            else:
                st.warning("Please enter a prompt.")

    # --- Statistics Tab ---
    with tab_stats:
        prompt = "Generate detailed statistics for the dataset including mean, std, and ranges for numerical columns."
        messages = [
            {"role": "system", "content": "You are a data profiling assistant."},
            {"role": "user", "content": f"Dataset Sample:\n{data_sample}\n\n{prompt}"}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        st.markdown("### Descriptive Statistics (AI Generated)")
        st.markdown(response['choices'][0]['message']['content'])

    # --- Summary Tab ---
    with tab_summary:
        prompt = "Summarize each column in the dataset with data type, number of unique values, sample values."
        messages[1]['content'] = f"Dataset Sample:\n{data_sample}\n\n{prompt}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        st.markdown("### Column Summary")
        st.markdown(response['choices'][0]['message']['content'])

    # --- Null Values Tab ---
    with tab_null:
        prompt = "List missing value counts and percentages for each column in the dataset."
        messages[1]['content'] = f"Dataset Sample:\n{data_sample}\n\n{prompt}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=800
        )
        st.markdown("### Missing Value Analysis")
        st.markdown(response['choices'][0]['message']['content'])

    # --- EDA Tab ---
    with tab_eda:
        prompt = "Provide exploratory insights based on the sample data, such as distribution patterns or common data issues."
        messages[1]['content'] = f"Dataset Sample:\n{data_sample}\n\n{prompt}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=800
        )
        st.markdown("### EDA Insights")
        st.markdown(response['choices'][0]['message']['content'])