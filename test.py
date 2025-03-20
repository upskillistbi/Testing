import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Redshift connection details
REDSHIFT_HOST = "misreporting.cxgsxkol4p2y.eu-west-1.redshift.amazonaws.com"
REDSHIFT_PORT = "5439"
REDSHIFT_DB = "misreportingdb"
REDSHIFT_USER = "etluser"
REDSHIFT_PASSWORD = "Etluser12345"

# Create SQLAlchemy engine for Redshift
engine = create_engine(f"postgresql+psycopg2://{REDSHIFT_USER}:{REDSHIFT_PASSWORD}@{REDSHIFT_HOST}:{REDSHIFT_PORT}/{REDSHIFT_DB}")

# Function to fetch data from Redshift
def fetch_data(query):
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# SQL Queries for Lead to CC Conversion Metrics
SQL_QUERIES = {
    "Total Leads": """
        SELECT COUNT(DISTINCT student_id) AS total_leads
        FROM data_warehouse.dim_students
        WHERE created_date BETWEEN '2025-01-01' AND '2025-03-31';
    """,
    
    "Qualified Leads": """
        SELECT COUNT(DISTINCT cs.id) AS qualified_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs 
            ON cs.value__meta_data_lead_id = ds.student_id
        WHERE ds.created_date BETWEEN '2025-01-01' AND '2025-03-31'
        AND cs.id IS NOT NULL;
    """,

    "Interested Leads": """
        SELECT COUNT(DISTINCT ds.student_id) AS interested_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs 
            ON cs.value__meta_data_lead_id = ds.student_id
        WHERE ds.created_date BETWEEN '2025-01-01' AND '2025-03-31'
        AND LOWER(ds.offer_type) LIKE '%skip2%';
    """,

    "Total Cancellations in Q1 2025": """
        SELECT COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_students
        FROM data_marts.combined_subscriptions cs
        WHERE cs.cancellation_intiated_on IS NOT NULL
        AND cs.cancellation_intiated_on BETWEEN '2025-01-01' AND '2025-03-31';
    """,

    "Total Active Subscriptions in 2025": """
        SELECT COUNT(DISTINCT cs.id) AS total_active_subscriptions_2025
        FROM data_marts.combined_subscriptions cs
        WHERE cs.value__status IN ('active', 'trialing', 'past_due')
        AND cs.created_at BETWEEN '2025-01-01' AND '2025-12-31';
    """,

    "Monthly Cancellations (Q1 2025)": """
        SELECT 
            DATE_TRUNC('month', cs.cancellation_intiated_on) AS cancel_month,
            COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_students
        FROM data_marts.combined_subscriptions cs
        WHERE cs.cancellation_intiated_on IS NOT NULL
        AND cs.cancellation_intiated_on BETWEEN '2025-01-01' AND '2025-03-31'
        GROUP BY 1
        ORDER BY 1;
    """
}

# Streamlit UI
st.title("📊 Lead to CC Conversion Metrics Dashboard")
st.subheader("Data from Amazon Redshift (Q1 2025)")

# Fetch and display metrics
metrics_data = {}
for metric_name, query in SQL_QUERIES.items():
    if "Monthly" not in metric_name:  # Exclude charts
        df = fetch_data(query)
        if df is not None and not df.empty:
            metrics_data[metric_name] = df.iloc[0, 0]
            st.metric(label=metric_name, value=f"{df.iloc[0, 0]:,.0f}")

# Conversion Rate Calculation
if "Total Leads" in metrics_data and "Qualified Leads" in metrics_data:
    lead_to_qualified_rate = (metrics_data["Qualified Leads"] / metrics_data["Total Leads"]) * 100
    st.metric(label="Lead to Qualified Rate (%)", value=f"{lead_to_qualified_rate:.2f}")

# Monthly Cancellations Line Chart
st.subheader("📉 Monthly Cancellations in Q1 2025")
df_cancellations = fetch_data(SQL_QUERIES["Monthly Cancellations (Q1 2025)"])
if df_cancellations is not None and not df_cancellations.empty:
    st.line_chart(df_cancellations.set_index("cancel_month"))
