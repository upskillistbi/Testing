import streamlit as st
import datetime
import pandas as pd
import psycopg2
from pandas.tseries.offsets import MonthBegin

# -----------------------------
# Streamlit Setup
# -----------------------------
st.set_page_config(page_title="Revenue Dashboard", layout="wide")
st.title("💳 Qualified Credit Card Leads Revenue Dashboard")

# -----------------------------
# Redshift DB Connection
# -----------------------------
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

# -----------------------------
# Fetch Country Options
# -----------------------------
@st.cache_data
def get_distinct_countries():
    query = """
    SELECT DISTINCT LOWER(country) AS country
    FROM data_warehouse.dim_students
    WHERE country IS NOT NULL
    ORDER BY 1;
    """
    df = run_query(query)
    return df["country"].tolist()

# -----------------------------
# UI Filters
# -----------------------------
st.sidebar.header("📅 Select Date Range")
start_date = st.sidebar.date_input("Start Date", datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date(2022, 3, 31))

country_options = get_distinct_countries()
selected_countries = st.sidebar.multiselect("🌍 Select Country (optional)", country_options)

run_btn = st.sidebar.button("▶️ Run Analysis")

# -----------------------------
# Run on Submit
# -----------------------------
if run_btn:

    country_filter_sql = ("TRUE" if not selected_countries else
                           f"LOWER(sc.country) IN ({','.join([f'\'{c}\'' for c in selected_countries])})")

    # 1. CC Summary
    cc_summary_query = f"""
    WITH cc_base AS (
      SELECT s.value__meta_data_lead_id AS cc_id,
             DATE_TRUNC('month', s.created_at) AS cc_month,
             s.created_at AS cc_created_at
      FROM data_marts.combined_subscriptions s
      WHERE DATE_TRUNC('month', s.created_at) BETWEEN DATE '{start_date}' AND DATE '{end_date}'
    ),
    first_txn AS (
      SELECT student_id, MIN(payment_date) AS first_txn_date
      FROM data_marts.combined_transactions
      GROUP BY student_id
    ),
    student_country AS (
      SELECT student_id, LOWER(country) AS country
      FROM data_warehouse.dim_students
    ),
    cc_flagged AS (
      SELECT cb.cc_id, cb.cc_month, cb.cc_created_at, ft.first_txn_date, sc.country,
             CASE WHEN ft.first_txn_date > cb.cc_created_at AND ft.first_txn_date <= cb.cc_created_at + INTERVAL '30 day'
                  THEN 1 ELSE 0 END AS is_first_time_buyer
      FROM cc_base cb
      LEFT JOIN first_txn ft ON cb.cc_id = ft.student_id
      LEFT JOIN student_country sc ON cb.cc_id = sc.student_id
      WHERE {country_filter_sql}
    )
    SELECT cc_month,
           TO_CHAR(cc_month, 'Mon-YY') AS cc_month_label,
           COUNT(DISTINCT cc_id) AS total_ccs,
           SUM(is_first_time_buyer) AS buyers_first_time,
           ROUND(100.0 * SUM(is_first_time_buyer)::NUMERIC / COUNT(DISTINCT cc_id), 1) || '%' AS conv_percentage
    FROM cc_flagged
    GROUP BY cc_month
    ORDER BY cc_month;
    """
    cc_df = run_query(cc_summary_query)
    st.subheader("📌 CC Conversion Summary")
    st.dataframe(cc_df)

    # 2. Revenue Data Query
    base_query = f"""
    WITH cc_base AS (
      SELECT s.value__meta_data_lead_id AS cc_id, s.created_at AS cc_created_at,
             DATE_TRUNC('month', s.created_at) AS cc_month
      FROM data_marts.combined_subscriptions s
      WHERE DATE_TRUNC('month', s.created_at) BETWEEN DATE '{start_date}' AND DATE '{end_date}'
    ),
    transaction_tags AS (
      SELECT t.transaction_id, t.student_id, t.payment_date, t.converted_amount, t.plan_id,
             t.billing_period_t, t.description,
             CASE
               WHEN t.description ILIKE '%lifetime%' THEN 'Rev2'
               WHEN t.description ILIKE '%course%' OR t.description ILIKE '%material%' OR t.description ILIKE '%hard%' THEN 'Rev3'
               WHEN t.plan_id IS NOT NULL THEN 'Rev1'
               ELSE 'Other'
             END AS revenue_type
      FROM data_marts.combined_transactions t
      WHERE t.value__refunded_txn_id IS NOT NULL
    ),
    student_country AS (
      SELECT student_id, LOWER(country) AS country FROM data_warehouse.dim_students
    )
    SELECT TO_CHAR(cb.cc_month, 'Mon-YY') AS cc_month,
           tx.revenue_type,
           CASE
             WHEN DATEDIFF(DAY, cb.cc_created_at, tx.payment_date) BETWEEN 0 AND 30 THEN 'Month1'
             WHEN DATEDIFF(DAY, cb.cc_created_at, tx.payment_date) BETWEEN 31 AND 60 THEN 'Month2'
             WHEN DATEDIFF(DAY, cb.cc_created_at, tx.payment_date) BETWEEN 61 AND 90 THEN 'Month3'
             WHEN DATEDIFF(DAY, cb.cc_created_at, tx.payment_date) BETWEEN 91 AND 120 THEN 'Month4'
             WHEN DATEDIFF(DAY, cb.cc_created_at, tx.payment_date) BETWEEN 121 AND 150 THEN 'Month5'
             WHEN DATEDIFF(DAY, cb.cc_created_at, tx.payment_date) BETWEEN 151 AND 180 THEN 'Month6'
             WHEN DATEDIFF(DAY, cb.cc_created_at, tx.payment_date) BETWEEN 181 AND 210 THEN 'Month7'
             WHEN DATEDIFF(DAY, cb.cc_created_at, tx.payment_date) BETWEEN 211 AND 240 THEN 'Month8'
             WHEN DATEDIFF(DAY, cb.cc_created_at, tx.payment_date) BETWEEN 241 AND 270 THEN 'Month9'
             WHEN DATEDIFF(DAY, cb.cc_created_at, tx.payment_date) BETWEEN 271 AND 300 THEN 'Month10'
             WHEN DATEDIFF(DAY, cb.cc_created_at, tx.payment_date) BETWEEN 301 AND 330 THEN 'Month11'
             WHEN DATEDIFF(DAY, cb.cc_created_at, tx.payment_date) BETWEEN 331 AND 360 THEN 'Month12'
             ELSE '>Month12'
           END AS month_bucket,
           SUM(tx.converted_amount) AS revenue
    FROM cc_base cb
    JOIN transaction_tags tx ON cb.cc_id = tx.student_id
    JOIN student_country sc ON tx.student_id = sc.student_id
    WHERE {country_filter_sql}
      AND tx.payment_date > cb.cc_created_at
      AND tx.payment_date <= cb.cc_created_at + INTERVAL '365 day'
    GROUP BY 1, 2, 3
    ORDER BY 1, 2, 3;
    """

    rev_df = run_query(base_query)

    rev_df["cumulative_revenue"] = (
        rev_df.sort_values(["cc_month", "revenue_type", "month_bucket"])
        .groupby(["cc_month", "revenue_type"])["revenue"]
        .cumsum()
    )

    summary_table = (
        rev_df.groupby(["cc_month", "revenue_type", "month_bucket"])
        .agg(
            total_revenue=("revenue", "sum"),
            cumulative_revenue=("cumulative_revenue", "max")
        )
        .reset_index()
    )

    summary_table = summary_table.merge(
        cc_df[["cc_month_label", "total_ccs"]],
        left_on="cc_month",
        right_on="cc_month_label",
        how="left"
    )
    summary_table["avg_revenue_per_cc"] = summary_table["cumulative_revenue"] / summary_table["total_ccs"]

    for table_name, value_column in [
        ("Rev1", "total_revenue"),
        ("Rev2", "total_revenue"),
        ("Rev3", "total_revenue"),
        ("Total Revenue", "total_revenue"),
        ("Cumulative Revenue", "cumulative_revenue"),
        ("Average Revenue", "avg_revenue_per_cc")
    ]:
        st.subheader(f"\U0001F4C8 {table_name} Pivot Table")

        df_pivot = (summary_table[summary_table.revenue_type == table_name]
                    if table_name in ["Rev1", "Rev2", "Rev3"]
                    else summary_table.copy())

        pivoted = df_pivot.pivot_table(
            index="cc_month_label",
            columns="month_bucket",
            values=value_column,
            aggfunc="sum"
        ).fillna(0)

        ordered_months = [f"Month{i}" for i in range(1, 13)] + [">Month12"]
        pivoted = pivoted[[m for m in ordered_months if m in pivoted.columns]]

        pivoted["Total"] = pivoted.sum(axis=1)
        total_row = pivoted.sum(axis=0)
        total_row.name = "Total"
        pivoted = pd.concat([pivoted, total_row.to_frame().T])

        pivoted.index.name = "CC Month"

        # --- Format & Highlight ---

        def highlight_based_on_mean(val, mean):
            try:
                return f'background-color: {"lightgreen" if val > mean else "lightcoral"}'
            except:
                return ""

        pivot_values_only = pivoted.drop(index="Total", errors="ignore").drop(columns="Total", errors="ignore")
        pivot_mean = pivot_values_only.replace(0, pd.NA).mean().mean()

        styled = pivoted.style.applymap(lambda v: highlight_based_on_mean(v, pivot_mean)).format("{:,.0f}")
       # st.dataframe(styled)
        st.dataframe(pivoted.style.format("{:,.0f}"))
