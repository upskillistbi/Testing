import streamlit as st
# ✅ Page config must be the first Streamlit command
st.set_page_config(page_title="Upskillist BI Agent", layout="wide")

import pandas as pd
import psycopg2
from transformers import pipeline
import datetime

from gtts import gTTS
import base64

# --- Redshift Query Function ---
def run_query(query):
    conn = psycopg2.connect(
        host="misreporting.cxgsxkol4p2y.eu-west-1.redshift.amazonaws.com",
        port=5439,
        dbname="misreportingdb",
        user="etluser",
        password="Etluser12345"
    )
    cur = conn.cursor()
    cur.execute("SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL READ COMMITTED")
    conn.commit()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- Load Local Hugging Face Model ---
@st.cache_resource
def load_local_model():
    return pipeline("text2text-generation", model="google/flan-t5-base")

local_agent = load_local_model()


# --- LLM-Based Summary + Your Logic ---
def explain_results(df, role, context, objective):
    # Generate basic insights using real values
    if df.empty or 'revenue' not in df.columns:
        return "No data available to summarize."

    top_rev = df.loc[df['revenue'].idxmax()]
    total = df['revenue'].sum()
    top_pct = round((top_rev['revenue'] / total) * 100, 2)

    bullet_points = f"""
- 💡 The top revenue type is **{top_rev['revenue_type']}**, contributing **{top_pct}%** of the total revenue.
- 🧾 Total revenue collected in the selected period is **${total:,.2f}**
- 📌 Strategic recommendation: Focus on growing **{top_rev['revenue_type']}** further to increase overall revenue.
"""

    # Add a short explanation from the LLM
    prompt = f"""
You are a business analyst at Upskillist.

Context:
{context}

Objective:
{objective}

Here is the table:
{df.to_string(index=False)}

Summarize the data clearly in simple language without repeating any revenue type more than once. Keep it to 2 lines.
"""
    result = local_agent(prompt, max_length=256, do_sample=False)[0]['generated_text']

    return bullet_points + "\n\n🧠 *LLM Summary:* " + result.strip()


def play_audio(text):
    tts = gTTS(text)
    tts.save("explanation.mp3")

    # Read the MP3 and convert to base64
    with open("explanation.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        b64 = base64.b64encode(audio_bytes).decode()

    audio_html = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)


st.title("📊 Upskillist Revenue Agent")

role = st.text_area("🧑‍💼 Role of Business Analyst")
context = st.text_area("🏢 Company & Data Context")
objective = st.text_input("🔍 Business Question (e.g. revenue breakdown by type)")
start_date = st.date_input("Start Date", datetime.date(2024, 1, 1))
end_date = st.date_input("End Date", datetime.date(2024, 12, 31))

if st.button("🔎 Run Agent"):
    revenue_where_clause = ""  # You can add filters dynamically if needed

    query = f"""
        SELECT
            CASE
                WHEN t.description ILIKE '%lifetime%' THEN 'Rev2'
                WHEN t.description ILIKE '%course%' OR t.description ILIKE '%material%' OR t.description ILIKE '%hard%' THEN 'Rev3'
                WHEN t.plan_id IS NOT NULL THEN 'Rev1'
                ELSE 'Other'
            END AS revenue_type,
            SUM(t.converted_amount) AS revenue
        FROM data_marts.combined_transactions t
        JOIN data_marts.combined_subscriptions cs ON t.student_id = cs.value__meta_data_lead_id
        JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
        WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'
        AND t.converted_amount > 0
        {revenue_where_clause}
        GROUP BY 1
        ORDER BY revenue DESC
    """
    df = run_query(query)
    st.dataframe(df)

    with st.spinner("🧠 Generating business explanation..."):
        explanation = explain_results(df, role, context, objective)
        st.markdown("### 📘 Business Analyst Summary")
        st.write(explanation)
        # Add this below explanation display
        st.markdown("### 🔈 Audio Summary")
        play_audio(explanation)
