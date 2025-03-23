import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import datetime

# Redshift connection config
REDSHIFT_HOST = "misreporting.cxgsxkol4p2y.eu-west-1.redshift.amazonaws.com"
REDSHIFT_PORT = "5439"
REDSHIFT_DB = "misreportingdb"
REDSHIFT_USER = "etluser"
REDSHIFT_PASSWORD = "Etluser12345"

# SQLAlchemy engine
engine = create_engine(f"postgresql+psycopg2://{REDSHIFT_USER}:{REDSHIFT_PASSWORD}@{REDSHIFT_HOST}:{REDSHIFT_PORT}/{REDSHIFT_DB}")

# Function to run SQL queries
def run_query(query, start_date, end_date):
    with engine.connect() as conn:
        df = pd.read_sql(query.format(start_date=start_date, end_date=end_date), conn)
    return df

# Streamlit UI
st.set_page_config(page_title="Lead to CC Conversion Insights", layout="wide")
st.title("📊 Lead to Credit Card Funnel Dashboard")

# Date filter
col1, col2 = st.columns(2)
start_date = col1.date_input("Start Date", datetime.date(2025, 1, 1))
end_date = col2.date_input("End Date", datetime.date(2025, 3, 31))
run_button = st.button("Run Query")

# Query templates
query_dict = {
    "Total Leads by UTM Source": """
        SELECT utm_source, COUNT(DISTINCT student_id) AS total_leads
        FROM data_warehouse.dim_students
        WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY 1 ORDER BY total_leads DESC LIMIT 5;
    """,
    "Qualified Leads by UTM Source": """
        SELECT ds.utm_source, COUNT(DISTINCT cs.id) AS qualified_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs ON ds.student_id = cs.value__meta_data_lead_id
        WHERE ds.created_date BETWEEN '{start_date}' AND '{end_date}' AND cs.id IS NOT NULL
        GROUP BY 1 ORDER BY qualified_leads DESC LIMIT 5;
    """,
    "Lead to CC Conversion % by UTM Source": """
        WITH total_leads AS (
            SELECT utm_source, COUNT(DISTINCT student_id) AS total_leads
            FROM data_warehouse.dim_students
            WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY 1
        ),
        qualified_leads AS (
            SELECT ds.utm_source, COUNT(DISTINCT cs.id) AS qualified_leads
            FROM data_warehouse.dim_students ds
            JOIN data_marts.combined_subscriptions cs ON ds.student_id = cs.value__meta_data_lead_id
            WHERE ds.created_date BETWEEN '{start_date}' AND '{end_date}' AND cs.id IS NOT NULL
            GROUP BY 1
        )
        SELECT 
            tl.utm_source,
            tl.total_leads,
            ql.qualified_leads,
            (ql.qualified_leads * 100.0 / NULLIF(tl.total_leads, 0)) AS conversion_rate
        FROM total_leads tl
        LEFT JOIN qualified_leads ql ON tl.utm_source = ql.utm_source
        ORDER BY conversion_rate DESC LIMIT 5;
    """,
    "Total Leads by Country": """
        SELECT country, COUNT(DISTINCT student_id) AS total_leads
        FROM data_warehouse.dim_students
        WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY 1 ORDER BY total_leads DESC LIMIT 5;
    """,
    "Qualified Leads by Country": """
        SELECT ds.country, COUNT(DISTINCT cs.id) AS qualified_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs ON ds.student_id = cs.value__meta_data_lead_id
        WHERE ds.created_date BETWEEN '{start_date}' AND '{end_date}' AND cs.id IS NOT NULL
        GROUP BY 1 ORDER BY qualified_leads DESC LIMIT 5;
    """
}

# Display result
if run_button:
    for title, sql in query_dict.items():
        st.subheader(title)
        df = run_query(sql, start_date, end_date)
        st.dataframe(df)
else:
    st.info("Please select a date range and click 'Run Query'.")

                # Row 1
        col1, col2, col3 = st.columns(3)
        with col1:
                st.markdown(f"""
                <div style="background-color:lightgrey;padding:15px;border-radius:10px;box-shadow:1px 1px 10px rgba(0,0,0,0.1)">
                <b>🧠 Top Country:</b><br>
                <code>{by_country.iloc[0]['country']}</code><br>
                Leads: <b>{by_country.iloc[0]['total_leads']:,}</b>
                </div>
            """, unsafe_allow_html=True)

        with col2:
                st.markdown(f"""
                <div style="background-color:lightgrey;padding:15px;border-radius:10px;box-shadow:1px 1px 10px rgba(0,0,0,0.1)">
                <b>🔍 Top UTM Source:</b><br>
                <code>{by_utm.iloc[0]['utm_source']}</code><br>
                Leads: <b>{by_utm.iloc[0]['total_leads']:,}</b>
                </div>
            """, unsafe_allow_html=True)

        with col3:
              st.markdown(f"""
                <div style="background-color:lightgrey;padding:15px;border-radius:10px;box-shadow:1px 1px 10px rgba(0,0,0,0.1)">
                <b>🤝 Top Partner:</b><br>
                <code>{by_partner.iloc[0]['partner']}</code><br>
                Leads: <b>{by_partner.iloc[0]['total_leads']:,}</b>
                </div>
            """, unsafe_allow_html=True)

        # Row 2
        col4, col5, col6 = st.columns(3)
        with col4:
                st.markdown(f"""
                <div style="background-color:lightgrey;padding:15px;border-radius:10px;box-shadow:1px 1px 10px rgba(0,0,0,0.1)">
                <b>📘 Top Course:</b><br>
                <code>{total_leads_course_picked.iloc[0]['coursepicked']}</code><br>
                Leads: <b>{total_leads_course_picked.iloc[0]['total_leads']:,}</b>
                </div>
            """, unsafe_allow_html=True)

        with col5:
                st.markdown(f"""
                <div style="background-color:lightgrey;padding:15px;border-radius:10px;box-shadow:1px 1px 10px rgba(0,0,0,0.1)">
                <b>👥 Top Age Group:</b><br>
                <code>{total_leads_age_group.iloc[0]['age_bucket']}</code><br>
                Leads: <b>{total_leads_age_group.iloc[0]['total_leads']:,}</b>
                </div>
            """, unsafe_allow_html=True)

        with col6:
                st.markdown(f"""
                <div style="background-color:lightgrey;padding:15px;border-radius:10px;box-shadow:1px 1px 10px rgba(0,0,0,0.1)">
                <b>🏷️ Top Offer Type:</b><br>
                <code>{total_leads_offer_type.iloc[0]['offer_type']}</code><br>
                Leads: <b>{total_leads_offer_type.iloc[0]['total_leads']:,}</b>
                </div>
            """, unsafe_allow_html=True)
  */      