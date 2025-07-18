import streamlit as st
import datetime
import pandas as pd
import plotly.express as px
import psycopg2

# ----------------------------
# Streamlit Page Config
# ----------------------------
st.set_page_config(page_title="📦 Cert & HCD Buyer Dashboard", layout="wide")
st.title("📦 Cert & Hard Copy Diploma Buyer Dashboard")

# ----------------------------
# Date Range Selector
# ----------------------------
today = datetime.date.today()
default_start = today - datetime.timedelta(days=365)
col1, col2 = st.columns(2)
start_date = col1.date_input("Start Date", default_start)
end_date = col2.date_input("End Date", today)

# ----------------------------
# Database Query Function
# ----------------------------
@st.cache_data
def run_query(query):
    conn = psycopg2.connect(
        host="misreporting.cxgsxkol4p2y.eu-west-1.redshift.amazonaws.com",
        port=5439,
        dbname="misreportingdb",
        user="etluser",
        password="Etluser12345"
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ----------------------------
# Cert/HCD Buyer Query with course_slug
# ----------------------------
query_cert_hcd = f"""
SELECT DISTINCT
    ct.student_id,
    ct.description,
    ct.converted_amount,
    ct.payment_date,
    ds.country,
    ds.offer_type,
    ds.profile__partner_identifier AS partner,
    ds.age_group,
    ds.coursepicked,
    ds.created_date,
    fa.course_slug,
    CASE 
        WHEN ct.plan_id IS NOT NULL THEN 'Rev1'
        WHEN LOWER(ct.description) LIKE '%lifetime%' THEN 'Rev2'
        WHEN LOWER(ct.description) LIKE '%certificate%' OR LOWER(ct.description) LIKE '%material%' OR LOWER(ct.description) LIKE '%hard%' THEN 'Rev3'
        ELSE 'Other'
    END AS revenue_type,
    COALESCE(fa.attended_flag, 0) AS attended,
    COALESCE(dsc.registered_flag, 0) AS registered
FROM data_marts.combined_transactions ct
INNER JOIN data_warehouse.dim_students ds ON ct.student_id = ds.student_id
LEFT JOIN (
    SELECT DISTINCT 
        value__student_id, 
        value__course_slug AS course_slug,
        1 AS attended_flag
    FROM firestore_api.firestore_attendance
    WHERE value__watched__bigint > 60
) fa ON ct.student_id = fa.value__student_id
LEFT JOIN (
    SELECT DISTINCT student_id, 1 AS registered_flag
    FROM data_warehouse.dim_schedules
) dsc ON ct.student_id = dsc.student_id
WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}'
  AND ct.converted_amount > 0
  AND (
    LOWER(ct.description) LIKE '%cert%' OR
    LOWER(ct.description) LIKE '%hard%'
  )
"""

buyers_df = run_query(query_cert_hcd)

# ----------------------------
# Summary Metrics
# ----------------------------
st.subheader("📊 Overview Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("🎯 Unique Buyers", buyers_df["student_id"].nunique())
col2.metric("💸 Total Revenue", f"€{buyers_df['converted_amount'].sum():,.2f}")
col3.metric("🧾 Total Transactions", len(buyers_df))

# ----------------------------
# Engagement Metrics
# ----------------------------
total_buyers = buyers_df["student_id"].nunique()
attended = buyers_df[buyers_df["attended"] == 1]["student_id"].nunique()
registered = buyers_df[buyers_df["registered"] == 1]["student_id"].nunique()
course_picked = buyers_df[buyers_df["coursepicked"].notnull()]["student_id"].nunique()

st.subheader("📚 Engagement")
col1, col2, col3 = st.columns(3)
col1.metric("👨‍🏫 Attended Lessons", f"{attended} ({attended / total_buyers:.0%})")
col2.metric("📝 Registered", f"{registered} ({registered / total_buyers:.0%})")
col3.metric("📘 Course Picked", f"{course_picked} ({course_picked / total_buyers:.0%})")

# ----------------------------
# Reusable Bar Chart
# ----------------------------
def bar_chart(df, x, y, title):
    if not df.empty:
        fig = px.bar(df, x=x, y=y, text_auto=True, title=title)
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Buyer Segmentation Charts
# ----------------------------
st.subheader("🌍 Buyers by Country")
df = buyers_df.groupby("country")["student_id"].nunique().reset_index().rename(columns={"student_id": "buyers"})
bar_chart(df, "country", "buyers", "Buyers by Country")

st.subheader("🎂 Buyers by Age Group")
df = buyers_df.groupby("age_group")["student_id"].nunique().reset_index().rename(columns={"student_id": "buyers"})
bar_chart(df, "age_group", "buyers", "Buyers by Age Group")

st.subheader("🪙 Revenue by Rev Type")
df = buyers_df.groupby("revenue_type")["converted_amount"].sum().reset_index()
bar_chart(df, "revenue_type", "converted_amount", "Revenue by Type (Rev1/Rev2/Rev3)")

st.subheader("🎁 Buyers by Offer Type")
df = buyers_df.groupby("offer_type")["student_id"].nunique().reset_index().rename(columns={"student_id": "buyers"})
bar_chart(df, "offer_type", "buyers", "Buyers by Offer Type")

st.subheader("🤝 Buyers by Partner")
df = buyers_df.groupby("partner")["student_id"].nunique().reset_index().rename(columns={"student_id": "buyers"})
bar_chart(df, "partner", "buyers", "Buyers by Partner")

st.subheader("📘 Course Picked Trends")
df = buyers_df.groupby("coursepicked")["student_id"].nunique().reset_index().rename(columns={"student_id": "buyers"})
bar_chart(df, "coursepicked", "buyers", "Course Picked Trends")

# ----------------------------
# 📚 Course Slug Trends from Attendance
# ----------------------------
st.subheader("🏷️ Course Slug from Attendance")
slug_buyers = buyers_df[buyers_df["course_slug"].notnull()]["student_id"].nunique()
st.metric("📒 Buyers with Course Slug", f"{slug_buyers} ({slug_buyers / total_buyers:.0%})")

df = buyers_df[buyers_df["course_slug"].notnull()]\
    .groupby("course_slug")["student_id"].nunique()\
    .reset_index().rename(columns={"student_id": "buyers"})
bar_chart(df, "course_slug", "buyers", "Buyers by Course Slug")

# ----------------------------
# Raw Data + Download
# ----------------------------
st.subheader("📄 Raw Cert/HCD Buyer Data")
st.dataframe(buyers_df.head(100))
st.download_button("📥 Download Full Data", data=buyers_df.to_csv(index=False), file_name="cert_hcd_buyers.csv")
