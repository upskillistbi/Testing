import streamlit as st
import datetime
import pandas as pd
pd.options.display.float_format = '{:,.2f}'.format
import psycopg2
import plotly.express as px
from concurrent.futures import ThreadPoolExecutor


# ---- Database connection function ----
@st.cache_data(ttl=3600)
def run_query(query, start_date, end_date):
    conn = psycopg2.connect(
        host="misreporting.cxgsxkol4p2y.eu-west-1.redshift.amazonaws.com",
        port=5439,
        dbname="misreportingdb",
        user="etluser",
        password="Etluser12345"
    )
    query = query.format(start_date=start_date, end_date=end_date)
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def run_parallel_queries(query_keys, start_date, end_date):
    with ThreadPoolExecutor() as executor:
        future_to_key = {
            executor.submit(run_query, revenue_queries[key], start_date, end_date): key
            for key in query_keys
        }
        return {future_to_key[future]: future.result() for future in future_to_key}





# ---- SQL Queries ----
revenue_queries = {

    "Post Reactivation Revenue": """
    SELECT
    SUM(converted_amount) AS post_reactivation_revenue
    FROM data_marts.combined_transactions
    WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
    AND converted_amount > 0
    AND reactivated_on IS NOT NULL
    AND payment_date > reactivated_on;
    """,
    # Core Metrics
    "Total Revenue": """SELECT SUM(converted_amount) AS total_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0;""",
    "Unique Buyers": """SELECT COUNT(DISTINCT student_id) AS unique_buyers FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 AND student_id IS NOT NULL;""",
    "Average Order Value (AOV)": """SELECT SUM(converted_amount) / NULLIF(COUNT(transaction_id), 0) AS average_order_value FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0;""",
    # Revenue splits
    "Rev1 Revenue":
      """SELECT SUM(converted_amount) AS rev1_revenue
FROM data_marts.combined_transactions
WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
  AND converted_amount > 0
  AND plan_id IS NOT NULL;""",


    "Rev2 Revenue": """SELECT SUM(converted_amount) AS rev2_revenue
FROM data_marts.combined_transactions
WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
  AND converted_amount > 0
  AND description ILIKE '%lifetime%';""",

  
    "Rev3 Revenue": """SELECT SUM(converted_amount) AS rev3_revenue
FROM data_marts.combined_transactions
WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
  AND converted_amount > 0
  AND (
    description ILIKE '%course%' OR
    description ILIKE '%material%' OR
    description ILIKE '%hard%'
  );
""",

# Rev1 Revenue by Plan ID
    "Rev1 Revenue by Plan ID": """
    SELECT 
      plan_id,
      SUM(converted_amount) AS rev1_revenue
    FROM data_marts.combined_transactions
    WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
      AND converted_amount > 0
      AND plan_id IS NOT NULL
    GROUP BY plan_id
    ORDER BY rev1_revenue DESC;
    """,

    # Rev2 Revenue by Lifetime Descriptions
    "Rev2 Revenue by Description": """
    SELECT 
      description,
      SUM(converted_amount) AS rev2_revenue
    FROM data_marts.combined_transactions
    WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
      AND converted_amount > 0
      AND plan_id IS NULL
      AND description ILIKE '%lifetime%'
    GROUP BY description
    ORDER BY rev2_revenue DESC;
    """,

    # Rev3 Revenue by Subtype (Course, Toolkit, Hard)
    "Rev3 Revenue by Type": """
    SELECT 
      CASE
        WHEN description ILIKE '%course%' THEN 'Course'
        WHEN description ILIKE '%material%' THEN 'Toolkit'
        WHEN description ILIKE '%hard%' THEN 'Hardcopy'
        ELSE 'Other'
      END AS rev3_type,
      SUM(converted_amount) AS rev3_revenue
    FROM data_marts.combined_transactions
    WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
      AND converted_amount > 0
      AND plan_id IS NULL
      AND (
        description ILIKE '%course%' OR
        description ILIKE '%material%' OR
        description ILIKE '%hard%'
      )
    GROUP BY rev3_type
    ORDER BY rev3_revenue DESC;
    """,
    "Partner Revenue": """SELECT SUM(converted_amount) AS partner_revenue 
    FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' 
    AND converted_amount > 0 AND student_id IS NULL;""",


    "Reactivation Revenue": """SELECT SUM(converted_amount) AS reactivation_revenue FROM data_marts.combined_transactions
     WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 AND reactivated_on IS NOT NULL;""",
    # Time Trends
    "Monthly Revenue Trend": """SELECT DATE_TRUNC('month', payment_date) AS month, SUM(converted_amount) AS 
    total_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' 
    AND converted_amount > 0 GROUP BY month ORDER BY month;""",
    # Demographics
    "Revenue by Country": """SELECT ds.country, SUM(ct.converted_amount) AS total_revenue FROM data_marts.combined_transactions 
    ct JOIN data_warehouse.dim_students ds ON ct.student_id = ds.student_id WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}' AND 
    ct.converted_amount > 0  GROUP BY ds.country ORDER BY total_revenue DESC;""",


    "Revenue by Gender": """SELECT
  COALESCE(LOWER(TRIM(ds.gender)), 'unknown') AS gender,
  SUM(ct.converted_amount) AS total_revenue
FROM data_marts.combined_transactions ct
JOIN data_warehouse.dim_students ds
  ON ct.student_id = ds.student_id
WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}'
  AND ct.converted_amount > 0
GROUP BY COALESCE(LOWER(TRIM(ds.gender)), 'unknown')
ORDER BY total_revenue DESC;""",

    "Revenue by Gateway": """SELECT gateway, SUM(converted_amount) AS total_revenue FROM data_marts.combined_transactions WHERE
      payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 GROUP BY gateway ORDER BY total_revenue DESC;""",

    "Revenue by Brand": """SELECT brand, SUM(converted_amount) AS total_revenue FROM data_marts.combined_transactions WHERE
      payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 GROUP BY brand ORDER BY total_revenue DESC;""",
    "Revenue by Currency": """SELECT currency, SUM(converted_amount) AS total_revenue FROM data_marts.combined_transactions WHERE
      payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 GROUP BY currency ORDER BY total_revenue DESC;""",
  ##  "Revenue by UTM Source": """SELECT cs.value__utm_source AS utm_source, SUM(ct.converted_amount) AS total_revenue FROM data_marts.combined_transactions ct JOIN data_marts.combined_subscriptions cs ON ct.subscription_id = cs.id WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}' AND ct.converted_amount > 0 AND ct.value__refunded_txn_id IS NULL GROUP BY cs.value__utm_source ORDER BY total_revenue DESC;""",

"Revenue by Partner Identifier": """
SELECT 
  ds.profile__partner_identifier AS partner_identifier,
  SUM(ct.converted_amount) AS total_revenue
FROM data_marts.combined_transactions ct
JOIN data_warehouse.dim_students ds 
  ON ct.student_id = ds.student_id
WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}'
  AND ct.converted_amount > 0
GROUP BY ds.profile__partner_identifier
ORDER BY total_revenue DESC;
""",
"Refund Revenue": """
SELECT
  SUM(converted_amount) AS total_refunded
FROM data_marts.combined_transactions
WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
  AND converted_amount > 0
  AND value__refunded_txn_id IS NOT NULL;
""",
    # Buyer Types
    "Revenue from First-Time Buyers": """SELECT SUM(ct.converted_amount) AS first_time_buyer_revenue FROM 
    data_marts.combined_transactions ct WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}' 
    AND ct.converted_amount > 0  AND 
    ct.student_id NOT IN (SELECT DISTINCT student_id FROM data_marts.combined_transactions WHERE payment_date < '{start_date}' AND converted_amount > 0 AND student_id IS NOT NULL);""",
   
   
    "Revenue from Returning Buyers": """SELECT SUM(ct.converted_amount) AS returning_buyer_revenue FROM 
    data_marts.combined_transactions ct WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}' AND ct.converted_amount > 0  
    AND ct.student_id IN (SELECT DISTINCT student_id FROM data_marts.combined_transactions WHERE payment_date < '{start_date}' 
    AND converted_amount > 0 AND student_id IS NOT NULL);""",
   
   
    "Revenue by Registration Cohort": """SELECT DATE_TRUNC('month', ds.created_date) AS registration_month,
      SUM(ct.converted_amount) AS total_revenue FROM data_marts.combined_transactions ct JOIN data_warehouse.dim_students ds ON ct.student_id = ds.student_id WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}' AND ct.converted_amount > 0  GROUP BY registration_month ORDER BY registration_month;""",
    "Top Spenders": """SELECT student_id, SUM(converted_amount) AS total_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 AND student_id IS NOT NULL GROUP BY student_id ORDER BY total_revenue DESC LIMIT 10;"""
,

"Revenue Logic Breakdown": """
SELECT
  CASE
    WHEN description ILIKE '%lifetime%' THEN 'Rev2'
    WHEN description ILIKE '%course%' OR description ILIKE '%material%' OR description ILIKE '%hard%' THEN 'Rev3'
    WHEN plan_id IS NOT NULL THEN 'Rev1'
    ELSE 'Other'
  END AS revenue_type,
  SUM(converted_amount) AS revenue
FROM data_marts.combined_transactions
WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
  AND converted_amount > 0
GROUP BY 1
ORDER BY revenue DESC;
""",

"Revenue by Partner Identifier and Type": """
SELECT
  ds.profile__partner_identifier AS partner_identifier,
  CASE
    WHEN ct.description ILIKE '%lifetime%' THEN 'Rev2'
    WHEN ct.description ILIKE '%course%' OR ct.description ILIKE '%material%' OR ct.description ILIKE '%hard%' THEN 'Rev3'
    WHEN ct.plan_id IS NOT NULL THEN 'Rev1'
    ELSE 'Other'
  END AS revenue_category,
  SUM(ct.converted_amount) AS total_revenue
FROM data_marts.combined_transactions ct
JOIN data_warehouse.dim_students ds
  ON ct.student_id = ds.student_id
WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}'
  AND ct.converted_amount > 0
GROUP BY ds.profile__partner_identifier, revenue_category
ORDER BY ds.profile__partner_identifier, revenue_category;
"""
,
"Rev1 Billing Frequency Breakdown": """
WITH classified_txns AS (
  SELECT
    *,
    CASE
      WHEN description ILIKE '%lifetime%' THEN 'Rev2'
      WHEN description ILIKE '%course%' OR description ILIKE '%toolkit%' OR description ILIKE '%hard%' THEN 'Rev3'
      WHEN plan_id IS NOT NULL THEN 'Rev1'
      ELSE 'Other'
    END AS revenue_type
  FROM data_marts.combined_transactions
  WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
    AND converted_amount > 0
)

SELECT
  revenue_type,
  CASE 
    WHEN revenue_type = 'Rev1' AND billing_period_t IN (1, 28) THEN '1'
    WHEN revenue_type = 'Rev1' THEN billing_period_t
    ELSE NULL
  END AS billing_frequency,
  SUM(converted_amount) AS revenue,
  COUNT(*) AS transaction_count
FROM classified_txns
WHERE revenue_type = 'Rev1'
GROUP BY revenue_type, billing_frequency
ORDER BY revenue_type, billing_frequency;
"""

}



revenue_queries["Rev1 Breakdown by Description"] = """
SELECT
  description,
  SUM(converted_amount) AS rev1_revenue
FROM data_marts.combined_transactions
WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
  AND converted_amount > 0
  AND plan_id IS NOT NULL
  AND description NOT ILIKE '%lifetime%'
  AND description NOT ILIKE '%course%'
  AND description NOT ILIKE '%toolkit%'
  AND description NOT ILIKE '%hard%'
GROUP BY description
ORDER BY rev1_revenue DESC;
"""

revenue_queries["Rev2 Breakdown by Description"] = """
WITH classified_txns AS (
  SELECT
    *,
    CASE
      WHEN LOWER(description) ILIKE '%lifetime%' THEN 'Rev2'
      WHEN LOWER(description) LIKE '%certificate%' OR LOWER(description) LIKE '%material%' OR LOWER(description) LIKE '%diploma%' THEN 'Rev3'
      WHEN plan_id IS NOT NULL THEN 'Rev1'
      ELSE 'Other'
    END AS revenue_type
  FROM data_marts.combined_transactions
  WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
    AND converted_amount > 0
)
SELECT
  CASE
    WHEN LOWER(description) LIKE '%basic%' THEN 'Lifetime - Basic'
    WHEN LOWER(description) LIKE '%standard%' THEN 'Lifetime - Standard'
    WHEN LOWER(description) LIKE '%unlimited%' THEN 'Lifetime - Unlimited'
    ELSE 'Lifetime - Other'
  END AS rev2_type,
  SUM(converted_amount) AS revenue,
  COUNT(*) AS transaction_count
FROM classified_txns
WHERE revenue_type = 'Rev2'
GROUP BY rev2_type
ORDER BY revenue DESC;
"""

revenue_queries["Rev3 Breakdown by Type"] = """
WITH classified_txns AS (
  SELECT
    *,
    CASE
      WHEN LOWER(description) ILIKE '%lifetime%' THEN 'Rev2'
      WHEN LOWER(description) LIKE '%certificate%' OR LOWER(description) LIKE '%material%' OR LOWER(description) LIKE '%diploma%' THEN 'Rev3'
      WHEN plan_id IS NOT NULL THEN 'Rev1'
      ELSE 'Other'
    END AS revenue_type
  FROM data_marts.combined_transactions
  WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
    AND converted_amount > 0
)
SELECT
  CASE
    WHEN LOWER(description) LIKE '%material%' THEN 'Rev3 - Toolkit'
    WHEN LOWER(description) LIKE '%hard%copy%diploma%' THEN 'Rev3 - Diploma'
    WHEN LOWER(description) LIKE '%certificate%' THEN 'Rev3 - Certificate'
    ELSE 'Rev3 - Other'
  END AS rev3_type,
  SUM(converted_amount) AS revenue,
  COUNT(*) AS transaction_count
FROM classified_txns
WHERE revenue_type = 'Rev3'
  AND (
    LOWER(description) LIKE '%material%' OR
    LOWER(description) LIKE '%diploma%' OR
    LOWER(description) LIKE '%certificate%'
  )
GROUP BY rev3_type
ORDER BY revenue DESC;
"""


# --- Streamlit App Layout ---
st.set_page_config(page_title="Revenue Dashboard 🚀", layout="wide")
st.title("💰 Revenue Dashboard")
col1, col2 = st.columns(2)
start_date = col1.date_input("Start Date", datetime.date(2025, 1, 1))
end_date = col2.date_input("End Date", datetime.date(2025, 3, 31))
run_button = st.button("Run Analysis 🚀")

if run_button:
    tab8, = st.tabs(["Revenue Tab"])
    with tab8:
        st.header("📊 Revenue Tab Insights")

        # -- Top Summary Metrics --
        with st.spinner("Loading summary metrics..."):    
            total_revenue = run_query(revenue_queries["Total Revenue"], start_date, end_date).iloc[0, 0]
            unique_buyers = run_query(revenue_queries["Unique Buyers"], start_date, end_date).iloc[0, 0]
            aov = run_query(revenue_queries["Average Order Value (AOV)"], start_date, end_date).iloc[0, 0]
            refunds = run_query(revenue_queries["Refund Revenue"], start_date, end_date).iloc[0, 0] or 0.0
            net_revenue = total_revenue - refunds

            reactivation_revenue = run_query(revenue_queries["Reactivation Revenue"], start_date, end_date).iloc[0, 0] or 0.0
            post_reactivation_revenue = run_query(revenue_queries["Post Reactivation Revenue"], start_date, end_date).iloc[0, 0] or 0.0
            first_time_revenue = run_query(revenue_queries["Revenue from First-Time Buyers"], start_date, end_date).iloc[0, 0] or 0.0
            returning_revenue = run_query(revenue_queries["Revenue from Returning Buyers"], start_date, end_date).iloc[0, 0] or 0.0
      

          # Row 1: 2 columns
            col1, col2 = st.columns(2)
            col1.metric("💰 Total Revenue", f"€{total_revenue:,.2f}")
            col2.metric("🔁 Refunds", f"€{refunds:,.2f}")

            # Row 2: 2 columns
            col3, col4 = st.columns(2)
            col3.metric("🧮 Net Revenue", f"€{net_revenue:,.2f}")
            col4.metric("🧑‍🏫 Unique Buyers", f"{unique_buyers:,}")

            # Row 3: 4 columns
            col5, col6, col7, col8 = st.columns(4)
            col5.metric("💳 AOV", f"€{aov:,.2f}")
            col6.metric("♻️ Reactivation Revenue", f"€{reactivation_revenue:,.2f}")
            col7.metric("🆕 Revenue from First-Time Buyers", f"€{first_time_revenue:,.2f}")
            col8.metric("🔁 Revenue from Returning Buyers", f"€{returning_revenue:,.2f}")

        
            def display_chart_table(title, query_key, x_col=None, y_col=None, chart_type="bar"):
                with st.spinner(f"Loading {title}..."):
                    df = run_query(revenue_queries[query_key], start_date, end_date)
                        # 🔢 Round all numeric columns to 2 decimal places
                    df = df.round(2)
                    
                    if not df.empty:
                        st.subheader(title)
                        col1, col2 = st.columns([1, 2])

                        with col1:
                            st.dataframe(df)
                            st.download_button(
                                label=f"Download {title} CSV",
                                data=df.to_csv(index=False).encode('utf-8'),
                                file_name=f"{title.lower().replace(' ', '_')}.csv",
                                mime="text/csv"
                            )

                        if x_col and y_col:
                            with col2:
                                if chart_type == "bar":
                                    fig = px.bar(df, x=x_col, y=y_col, text=y_col, title=title)
                                    fig.update_traces(textposition="outside")
                                else:
                                    fig = px.line(df, x=x_col, y=y_col, markers=True, title=title)
                                st.plotly_chart(fig, use_container_width=True)

                        st.markdown("---")


                    # 🔍 Display Logic-Based Rev1/2/3 Split
            def display_chart_table_dual(title, df, x_col, y_cols):
              """
              Displays two bar charts (for each y_col) and a combined data table.
              """
              col1, col2 = st.columns(2)

              with col1:
                  fig1 = px.bar(df, x=x_col, y=y_cols[0], text=y_cols[0], title=f"{title} - {y_cols[0].replace('_', ' ').title()}")
                  st.plotly_chart(fig1)

              with col2:
                  fig2 = px.bar(df, x=x_col, y=y_cols[1], text=y_cols[1], title=f"{title} - {y_cols[1].replace('_', ' ').title()}")
                  st.plotly_chart(fig2)

              st.markdown("### 📋 Full Data Table")
              st.dataframe(df)
            logic_rev_df = run_query(revenue_queries["Revenue Logic Breakdown"], start_date, end_date).round(2)
            
            # Add total row
            total_row = pd.DataFrame([{
                "revenue_type": "Total",
                "revenue": logic_rev_df["revenue"].sum()
            }])
            logic_rev_df = pd.concat([logic_rev_df, total_row], ignore_index=True)

            st.subheader("📊 Revenue Breakdown: Rev1 / Rev2 / Rev3 (Logic-Based)")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(logic_rev_df)
                st.download_button(
                    label="Download Rev1/2/3 Logic Breakdown",
                    data=logic_rev_df.to_csv(index=False).encode('utf-8'),
                    file_name="revenue_logic_breakdown.csv",
                    mime="text/csv"
                )
            with col2:
                fig = px.pie(
                    logic_rev_df[logic_rev_df["revenue_type"] != "Total"],
                    names="revenue_type",
                    values="revenue",
                    title="Logic-Based Revenue Split"
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("🧩 Deep Dive: Rev1 / Rev2 / Rev3 Logic")

#            with st.expander("📘 Rev1 Breakdown"):
#                display_chart_table("Rev1 Breakdown by Description", "Rev1 Breakdown by Description", "description", "rev1_revenue")
#                st.markdown("### 📆 Rev1 Breakdown by Billing Frequency")
#                display_chart_table("Rev1 Billing Frequency Breakdown", "Rev1 Billing Frequency Breakdown", "billing_frequency", "revenue")

#            with st.expander("📙 Rev2 Breakdown"):
#                display_chart_table("Rev2 Breakdown by Description", "Rev2 Breakdown by Description", "rev2_type", "revenue")
#             with st.expander("📗 Rev3 Breakdown"):
#                display_chart_table("Rev3 Breakdown by Type", "Rev3 Breakdown by Type", "rev3_type", "revenue")
                
            with st.expander("📘 Rev1 Breakdown"):
                rev1_df = run_query(revenue_queries["Rev1 Billing Frequency Breakdown"], start_date, end_date)
                display_chart_table_dual("Rev1 Billing Frequency Breakdown", rev1_df, "billing_frequency", ["revenue", "transaction_count"])

            with st.expander("📙 Rev2 Breakdown"):
                rev2_df = run_query(revenue_queries["Rev2 Breakdown by Description"], start_date, end_date)
                display_chart_table_dual("Rev2 Breakdown by Description", rev2_df, "rev2_type", ["revenue", "transaction_count"])

            with st.expander("📗 Rev3 Breakdown"):
                rev3_df = run_query(revenue_queries["Rev3 Breakdown by Type"], start_date, end_date)
                display_chart_table_dual("Rev3 Breakdown by Type", rev3_df, "rev3_type", ["revenue", "transaction_count"])

            st.markdown("---")
            display_chart_table("Revenue by Partner Identifier", "Revenue by Partner Identifier", "partner_identifier", "total_revenue")
            display_chart_table("Revenue by Partner Identifier and Type","Revenue by Partner Identifier and Type",x_col="partner_identifier",y_col="total_revenue",chart_type="bar")
            display_chart_table("Revenue by Registration Cohort", "Revenue by Registration Cohort", "registration_month", "total_revenue", "line")
            display_chart_table("Top Spenders", "Top Spenders", "student_id", "total_revenue")
            display_chart_table("Monthly Revenue Trend", "Monthly Revenue Trend", "month", "total_revenue", "line")
            display_chart_table("Revenue by Country", "Revenue by Country", "country", "total_revenue")
            display_chart_table("Revenue by Gateway", "Revenue by Gateway", "gateway", "total_revenue")
            display_chart_table("Revenue by Brand", "Revenue by Brand", "brand", "total_revenue")


            st.success("✅ Revenue analysis complete!")

            st.success("✅ Revenue analysis complete!")

else:
   
    st.info("📅 Please select your date range and click 'Run Analysis' to see results.")
