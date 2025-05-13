import streamlit as st
import datetime
import pandas as pd
import psycopg2
import plotly.express as px

# Page layout
st.set_page_config(page_title="Qualified Leads Dashboard", layout="wide")
st.title("💳 Qualified Credit Card Leads Dashboard")

def run_query(query, start_date, end_date):
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

    query = query.format(start_date=start_date, end_date=end_date)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data
def get_filter_options():
    country_query = "SELECT DISTINCT country FROM data_warehouse.dim_students WHERE country IS NOT NULL"
    partner_query = "SELECT DISTINCT profile__partner_identifier FROM data_warehouse.dim_students WHERE profile__partner_identifier IS NOT NULL"
    offer_query = "SELECT DISTINCT offer_type FROM data_warehouse.dim_students WHERE offer_type IS NOT NULL"
    countries = run_query(country_query, '2020-01-01', '2030-01-01')['country'].tolist()
    partners = run_query(partner_query, '2020-01-01', '2030-01-01')['profile__partner_identifier'].tolist()
    offers = run_query(offer_query, '2020-01-01', '2030-01-01')['offer_type'].tolist()
    return countries, partners, offers


# Where clauses
def build_where_clause(countries, partners, offers):
    clause = "WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'"
    if countries:
        clause += f" AND ds.country IN ({', '.join([repr(c) for c in countries])})"
    if partners:
        clause += f" AND ds.profile__partner_identifier IN ({', '.join([repr(p) for p in partners])})"
    if offers:
        clause += f" AND ds.offer_type IN ({', '.join([repr(o) for o in offers])})"
    return clause
def build_revenue_where_clause(countries, partners, offers):
    clause = ""
    if countries:
        clause += f" AND ds.country IN ({', '.join([repr(c) for c in countries])})"
    if partners:
        clause += f" AND ds.profile__partner_identifier IN ({', '.join([repr(p) for p in partners])})"
    if offers:
        clause += f" AND ds.offer_type IN ({', '.join([repr(o) for o in offers])})"
    return clause
def build_course_details_where_clause(countries, partners, offers):
    clause = "WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'"
    if countries:
        clause += f" AND ds.country IN ({', '.join([repr(c) for c in countries])})"
    if partners:
        clause += f" AND ds.profile__partner_identifier IN ({', '.join([repr(p) for p in partners])})"
    if offers:
        clause += f" AND ds.offer_type IN ({', '.join([repr(o) for o in offers])})"
    return clause

def build_course_details_where_clause(countries, partners, offers):
    clause = "WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'"
    if countries:
        clause += f" AND ds.country IN ({', '.join([repr(c) for c in countries])})"
    if partners:
        clause += f" AND ds.profile__partner_identifier IN ({', '.join([repr(p) for p in partners])})"
    if offers:
        clause += f" AND ds.offer_type IN ({', '.join([repr(o) for o in offers])})"
    return clause
# SQL Queries 
def get_qualified_leads(start, end, countries, partners, offers):
    where_clause = build_where_clause(countries, partners, offers)
    query = f"""
        SELECT COUNT(DISTINCT cs.value__meta_data_lead_id) AS qualified_leads
        FROM data_marts.combined_subscriptions cs
        JOIN data_warehouse.dim_students ds
          ON ds.student_id = cs.value__meta_data_lead_id
        {where_clause}
    """
    df = run_query(query, start, end)
    return df.iloc[0]['qualified_leads']

def get_leads_by_dimension(dimension, start, end, countries, partners, offers):
    where_clause = build_where_clause(countries, partners, offers)
    query = f"""
        SELECT ds.{dimension} AS dimension_value,
               COUNT(DISTINCT cs.value__meta_data_lead_id) AS qualified_leads
        FROM data_marts.combined_subscriptions cs
        JOIN data_warehouse.dim_students ds
          ON ds.student_id = cs.value__meta_data_lead_id
        {where_clause}
        GROUP BY ds.{dimension}
        ORDER BY qualified_leads DESC;
    """
    return run_query(query, start, end)


def get_cancellation_details(start, end, countries, partners, offers):
    where_clause = build_where_clause(countries, partners, offers).replace("WHERE", "AND")
    query = f"""
        SELECT
            ds.student_id,
            DATEDIFF(day, cs.created_at, cs.cancellation_intiated_on) AS days_to_cancel,
            cs.data__custom_data__cancellation_reason_code AS cancellation_reason
        FROM (
            SELECT cs.*,
                   ROW_NUMBER() OVER (PARTITION BY cs.value__meta_data_lead_id ORDER BY cs.cancellation_intiated_on) AS rn
            FROM data_marts.combined_subscriptions cs
            JOIN data_warehouse.dim_students ds
              ON ds.student_id = cs.value__meta_data_lead_id
            WHERE cs.cancellation_intiated_on IS NOT NULL
              AND cs.created_at BETWEEN '{start}' AND '{end}'
              {where_clause}
        ) cs
        JOIN data_warehouse.dim_students ds
          ON ds.student_id = cs.value__meta_data_lead_id
        WHERE rn = 1
    """
    return run_query(query, start, end)


def get_leads_by_course(start, end, countries, partners, offers):
    where_clause = build_where_clause(countries, partners, offers)
    query = f"""
        SELECT ds.coursepicked AS dimension_value,
               COUNT(DISTINCT cs.value__meta_data_lead_id) AS qualified_leads
        FROM data_marts.combined_subscriptions cs
        JOIN data_warehouse.dim_students ds
          ON ds.student_id = cs.value__meta_data_lead_id
        {where_clause}
        GROUP BY ds.coursepicked
        ORDER BY qualified_leads DESC;
    """
    return run_query(query, start, end)


# These dimensions exist in data_warehouse.dim_students and combined_subscriptions
dimensions = {
    "Gender": "gender",
    "Employment Status": "employment_status",
    "Qualification": "qualification",
    "Goal": "goal",
    "Brand": "brand"  # comes from cs.brand
}


def get_leads_by_dimension_dynamic(dimension, source_table, start, end, countries, partners, offers):
    where_clause = build_where_clause(countries, partners, offers)

    query = f"""
        SELECT {source_table}.{dimension} AS dimension_value,
               COUNT(DISTINCT cs.value__meta_data_lead_id) AS qualified_leads
        FROM data_marts.combined_subscriptions cs
        JOIN data_warehouse.dim_students ds
          ON ds.student_id = cs.value__meta_data_lead_id
        {where_clause}
        GROUP BY {source_table}.{dimension}
        ORDER BY qualified_leads DESC;
    """
    return run_query(query, start, end)


def get_leads_by_age(start, end, countries, partners, offers):
    where_clause = build_where_clause(countries, partners, offers)
    query = f"""
        SELECT ds.age_group AS dimension_value,
               COUNT(DISTINCT cs.value__meta_data_lead_id) AS qualified_leads
        FROM data_marts.combined_subscriptions cs
        JOIN data_warehouse.dim_students ds
          ON ds.student_id = cs.value__meta_data_lead_id
        {where_clause}
        GROUP BY ds.age_group
        ORDER BY qualified_leads DESC;
    """
    return run_query(query, start, end)



def display_chart(df, x_col, y_col, title):
    if not df.empty:
        col1, col2 = st.columns([1, 2])  # 1/3 for table, 2/3 for chart
        with col1:
            st.markdown(f"**📋 Data: {title}**")
            st.dataframe(df)
        with col2:
            fig = px.bar(df, x=x_col, y=y_col, title=title,text_auto=True,  
                         labels={x_col: x_col.replace('_', ' ').title(),
                                 y_col: y_col.replace('_', ' ').title()})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No data available for {title}")


def display_chart(df, x_col, y_col, title):
    if not df.empty:
        col1, col2 = st.columns([1, 2])  # 1/3 for table, 2/3 for chart
        with col1:
            st.markdown(f"**📋 Data: {title}**")
            st.dataframe(df)
        with col2:
            fig = px.bar(df, x=x_col, y=y_col, title=title,text_auto=True,  
                         labels={x_col: x_col.replace('_', ' ').title(),
                                 y_col: y_col.replace('_', ' ').title()})
            st.plotly_chart(fig, use_container_width=True, key=title)  # ✅ Unique key added here
    else:
        st.warning(f"No data available for {title}")

                    # 🔍 Display Logic-Based Rev1/2/3 Split
def display_chart_table_dual(title, df, x_col, y_cols):
    """
    Displays two bar charts (for each y_col) and a combined data table.
    """
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(df, x=x_col, y=y_cols[0], text=y_cols[0], text_auto=True,  title=f"{title} - {y_cols[0].replace('_', ' ').title()}")
        st.plotly_chart(fig1)

    with col2:
         fig2 = px.bar(df, x=x_col, y=y_cols[1], text=y_cols[1],text_auto=True,   title=f"{title} - {y_cols[1].replace('_', ' ').title()}")
         st.plotly_chart(fig2)

    st.markdown("### 📋 Full Data Table")
    st.dataframe(df)
      

# --- Dimension Queries ---


# Filters
start_date = st.date_input("📅 Start Date of CC cohort ", datetime.date(2025, 1, 1))
end_date = st.date_input("📅 End Date of CC cohort ", datetime.date(2025, 12, 31))
valid_dates = end_date >= start_date

with st.spinner("🔄 Loading filters..."):
    countries, partners, offers = get_filter_options()

with st.expander("🔍 Select your Qualified CC Cohort"):
    col1, col2 = st.columns(2)
    selected_countries = col1.multiselect("🌍 Country", countries)
    selected_partners = col2.multiselect("🤝 Partner Identifier", partners)
    selected_offers = st.multiselect("🎁 Offer Type", offers)



if st.button("🚀 Run Analysis - All numbers are for the CC cohort selected in the above filters "):
    if not valid_dates:
        st.error("❌ End date must be on or after Start date.")
    else:
        tabs = st.tabs([
            "📊 CC Cohort Overview", 
            "❌ Cohort Cancellations",
            "💰 Cohort Revenue", 
            "📘  Cohort Details "
            
        ])

        with tabs[0]:
            st.header("📊 CC Hyperpersonalization Features from Leads table")
            qualified = get_qualified_leads(start_date, end_date, selected_countries, selected_partners, selected_offers)
            by_country = get_leads_by_dimension("country", start_date, end_date, selected_countries, selected_partners, selected_offers)
            by_partner = get_leads_by_dimension("profile__partner_identifier", start_date, end_date, selected_countries, selected_partners, selected_offers)
            by_offer = get_leads_by_dimension("offer_type", start_date, end_date, selected_countries, selected_partners, selected_offers)
            course_df = get_leads_by_course(start_date, end_date, selected_countries, selected_partners, selected_offers)
            age_df = get_leads_by_age(start_date, end_date, selected_countries, selected_partners, selected_offers)

            st.metric("📈 Total Qualified Leads", f"{qualified:,}")
            display_chart(by_country, "dimension_value", "qualified_leads", "Qualified Leads by Country")
            display_chart(by_partner, "dimension_value", "qualified_leads", "Qualified Leads by Partner Identifier")
            display_chart(by_offer, "dimension_value", "qualified_leads", "Qualified Leads by Offer Type")
            display_chart(course_df, "dimension_value", "qualified_leads", "Qualified Leads by Course Picked")
            display_chart(age_df, "dimension_value", "qualified_leads", "Qualified Leads by Age Group")

            
            st.subheader("📊 Additional Breakdowns")
            dimensions = {
                "Gender": "gender",
                "Employment Status": "employment_status",
                "Qualification": "qualification",
                "Goal": "goal",
                "Brand": "brand"
            }
            for label, col_name in dimensions.items():
                source = "cs" if col_name == "brand" else "ds"
                df_dim = get_leads_by_dimension_dynamic(col_name, source, start_date, end_date, selected_countries, selected_partners, selected_offers)
                display_chart(df_dim, "dimension_value", "qualified_leads", f"Qualified Leads by {label}")



        with tabs[1]:

            
            cancellation_where_clause = build_where_clause(
            selected_countries, selected_partners, selected_offers
             ).replace("WHERE", "WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}' AND")
            st.header("❌ Cancellation Analysis")
            cancellation_details = get_cancellation_details(start_date, end_date, selected_countries, selected_partners, selected_offers)

                        # Total Cancellations among qualified CCs
            query_cancelled_metric = f"""
                SELECT COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
                FROM data_marts.combined_subscriptions cs
                JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                {cancellation_where_clause}
                AND cs.cancellation_intiated_on IS NOT NULL
            """
            cancelled_count_df = run_query(query_cancelled_metric, start_date, end_date)
            total_cancelled = cancelled_count_df.iloc[0]['cancelled_leads']
            st.metric("❌ Cancelled Qualified Leads", f"{total_cancelled:,}")
            # % of Cancelled Qualified Leads
            cancel_rate = (total_cancelled / qualified) * 100 if qualified else 0
            st.metric("📉 % Cancelled from Qualified CC Leads", f"{cancel_rate:.2f}%")
            avg_days_to_cancel = cancellation_details["days_to_cancel"].mean()
            st.metric("📆 Average Days to Cancel", f"{avg_days_to_cancel:.1f} days")



            with st.expander("📋 View Cancellation Details by Student ID", expanded=False):
                st.dataframe(cancellation_details)

            st.subheader("📊 Days to Cancel Distribution")
            fig_cancel_days = px.histogram(cancellation_details, x="days_to_cancel", nbins=10, title="Distribution of Days to Cancel", text_auto=True)
            st.plotly_chart(fig_cancel_days, use_container_width=True, key="cancel_days_histogram")

            st.subheader("📊 Top Cancellation Reasons")
            reason_counts = cancellation_details['cancellation_reason'].value_counts().reset_index()
            reason_counts.columns = ["Reason", "Count"]
            fig_cancel_reasons = px.bar(reason_counts, x="Reason", y="Count", title="Top Cancellation Reasons",text_auto=True)
            st.plotly_chart(fig_cancel_reasons, use_container_width=True, key="cancel_reasons_bar")

            # Days to Cancel by Course
            query_days_cancel_course = f"""
                SELECT
                ds.coursepicked AS dimension_value,
                ROUND(AVG(DATEDIFF(day, cs.created_at, cs.cancellation_intiated_on))) AS avg_days_to_cancel,
                COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
                FROM data_marts.combined_subscriptions cs
                JOIN data_warehouse.dim_students ds
                ON ds.student_id = cs.value__meta_data_lead_id
                {cancellation_where_clause}
                AND cs.cancellation_intiated_on IS NOT NULL
                GROUP BY ds.coursepicked
                ORDER BY avg_days_to_cancel DESC
            """
            df_days_cancel_course = run_query(query_days_cancel_course, start_date, end_date)
            display_chart(df_days_cancel_course, "dimension_value", "avg_days_to_cancel", "Average Days to Cancel by Course Picked")


            # Reuse filter logic for cancellations
            cancellation_where_clause = build_where_clause(selected_countries, selected_partners, selected_offers)



            # Cancellation by Course Picked
            query_course = f"""
                SELECT ds.coursepicked AS dimension_value,
                       COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
                FROM data_marts.combined_subscriptions cs
                JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                {cancellation_where_clause}
                AND cs.cancellation_intiated_on IS NOT NULL
                GROUP BY ds.coursepicked
                ORDER BY cancelled_leads DESC
            """
            df_course_cancel = run_query(query_course, start_date, end_date)
            display_chart(df_course_cancel, "dimension_value", "cancelled_leads", "Cancellations by Course Picked")

            # Cancellation by Offer Type
            query_offer = f"""
                SELECT ds.offer_type AS dimension_value,
                       COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
                FROM data_marts.combined_subscriptions cs
                JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                {cancellation_where_clause}
                AND cs.cancellation_intiated_on IS NOT NULL
                GROUP BY ds.offer_type
                ORDER BY cancelled_leads DESC
            """

                        # --- Cancellation by Country ---
            query_country = f"""
                SELECT ds.country AS dimension_value,
                    COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
                FROM data_marts.combined_subscriptions cs
                JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                {cancellation_where_clause}
                AND cs.cancellation_intiated_on IS NOT NULL
                GROUP BY ds.country
                ORDER BY cancelled_leads DESC
            """
            df_country_cancel = run_query(query_country, start_date, end_date)
            display_chart(df_country_cancel, "dimension_value", "cancelled_leads", "Cancellations by Country")


            df_offer_cancel = run_query(query_offer, start_date, end_date)
            display_chart(df_offer_cancel, "dimension_value", "cancelled_leads", "Cancellations by Offer Type")

            # Cancellation by Partner Identifier
            query_partner = f"""
                SELECT ds.profile__partner_identifier AS dimension_value,
                       COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
                FROM data_marts.combined_subscriptions cs
                JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                {cancellation_where_clause}
                AND cs.cancellation_intiated_on IS NOT NULL
                GROUP BY ds.profile__partner_identifier
                ORDER BY cancelled_leads DESC
            """
            df_partner_cancel = run_query(query_partner, start_date, end_date)
            display_chart(df_partner_cancel, "dimension_value", "cancelled_leads", "Cancellations by Partner Identifier")


        with tabs[2]:
            st.header("💰 Revenue from Qualified Credit Card Users")

            # Clause for filtering qualified CCs
            revenue_where_clause = build_revenue_where_clause(selected_countries, selected_partners, selected_offers)

            # --- Total Revenue ---
            query_total_revenue = f"""
                SELECT SUM(t.converted_amount) AS total_revenue
                FROM data_marts.combined_transactions t
                JOIN data_marts.combined_subscriptions cs ON t.student_id = cs.value__meta_data_lead_id
                JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND t.converted_amount > 0
                {revenue_where_clause}
            """
            df_total_revenue = run_query(query_total_revenue, start_date, end_date)
            total_revenue = df_total_revenue.iloc[0]['total_revenue'] or 0
            st.metric("💰 Total Revenue", f"€{total_revenue:,.2f}")

            # --- AOV ---
            query_aov = f"""
                SELECT SUM(t.converted_amount) / NULLIF(COUNT(t.transaction_id), 0) AS average_order_value
                FROM data_marts.combined_transactions t
                JOIN data_marts.combined_subscriptions cs ON t.student_id = cs.value__meta_data_lead_id
                JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND t.converted_amount > 0
                {revenue_where_clause}
            """
            df_aov = run_query(query_aov, start_date, end_date)
            aov = df_aov.iloc[0]['average_order_value'] or 0
            st.metric("🧾 AOV per Transaction", f"€{aov:,.2f}")
            aov_per_buyer = total_revenue / qualified if qualified else 0
            st.metric("👤 AOV per CC Buyer", f"€{aov_per_buyer:,.2f}")


            # --- Revenue Breakdown by Type ---
            query_breakdown = f"""
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
            df_revenue_breakdown = run_query(query_breakdown, start_date, end_date)
            display_chart(df_revenue_breakdown, "revenue_type", "revenue", "Revenue by Type (Rev1/Rev2/Rev3)")
    
 
            query_first_time_buyers_detail = f"""
                SELECT
                    ct.student_id,
                    ct.transaction_id,
                    ct.converted_amount,
                    ct.payment_date
                FROM data_marts.combined_transactions ct
                JOIN data_marts.combined_subscriptions cs 
                    ON ct.student_id = cs.value__meta_data_lead_id
                JOIN data_warehouse.dim_students ds 
                    ON ds.student_id = cs.value__meta_data_lead_id
                WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND ct.converted_amount > 0
                {revenue_where_clause}
                AND ct.student_id NOT IN (
                    SELECT DISTINCT student_id 
                    FROM data_marts.combined_transactions
                    WHERE payment_date < '{start_date}'
                        AND converted_amount > 0
                        AND student_id IS NOT NULL
                )
            """

            df_first_time_buyers = run_query(query_first_time_buyers_detail, start_date, end_date)
            first_time_revenue = df_first_time_buyers["converted_amount"].sum()


            st.metric("🧑‍🎓 Revenue from First-Time Buyers", f"€{first_time_revenue:,.2f}")

            with st.expander("📋 First-Time Buyer Transactions"):
                st.dataframe(df_first_time_buyers)


            query_returning_buyers_detail = f"""
                SELECT
                    ct.student_id,
                    ct.transaction_id,
                    ct.converted_amount,
                    ct.payment_date
                FROM data_marts.combined_transactions ct
                JOIN data_marts.combined_subscriptions cs 
                    ON ct.student_id = cs.value__meta_data_lead_id
                JOIN data_warehouse.dim_students ds 
                    ON ds.student_id = cs.value__meta_data_lead_id
                WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND ct.converted_amount > 0
                {revenue_where_clause}
                AND ct.student_id IN (
                    SELECT DISTINCT student_id 
                    FROM data_marts.combined_transactions
                    WHERE payment_date < '{start_date}'
                        AND converted_amount > 0
                        AND student_id IS NOT NULL
                )
            """


            df_returning_buyers = run_query(query_returning_buyers_detail, start_date, end_date)
            returning_buyer_revenue = df_returning_buyers["converted_amount"].sum()

            st.metric("🔁 Revenue from Returning Buyers", f"€{returning_buyer_revenue:,.2f}")

            with st.expander("📋 Returning Buyer Transactions"):
                st.dataframe(df_returning_buyers)



            if total_revenue > 0:
                first_time_share = (first_time_revenue / total_revenue) * 100
                returning_share = (returning_buyer_revenue / total_revenue) * 100
                st.write(f"🧾 Revenue Share — First-Time Buyers: **{first_time_share:.2f}%**, Returning Buyers: **{returning_share:.2f}%**")


            first_time_revenue = df_first_time_buyers["converted_amount"].sum()
            returning_buyer_revenue = df_returning_buyers["converted_amount"].sum()

            # 📊 Pie Chart: Revenue Split by Buyer Type
            revenue_share_df = pd.DataFrame({
                "Buyer Type": ["First-Time Buyers", "Returning Buyers"],
                "Revenue": [first_time_revenue, returning_buyer_revenue]
            })

            fig_share = px.pie(
                revenue_share_df,
                names="Buyer Type",
                values="Revenue",
                title="💹 Revenue Share by Buyer Type",
                hole=0.4
            )

            st.plotly_chart(fig_share, use_container_width=True)


            query_rev1_billing_frequency = f"""
                WITH classified_txns AS (
                    SELECT t.*,
                        CASE
                            WHEN t.description ILIKE '%lifetime%' THEN 'Rev2'
                            WHEN t.description ILIKE '%course%' OR t.description ILIKE '%material%' OR t.description ILIKE '%hard%' THEN 'Rev3'
                            WHEN t.plan_id IS NOT NULL THEN 'Rev1'
                            ELSE 'Other'
                        END AS revenue_type
                    FROM data_marts.combined_transactions t
                    JOIN data_marts.combined_subscriptions cs ON t.student_id = cs.value__meta_data_lead_id
                    JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                    WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                    AND t.converted_amount > 0
                    {revenue_where_clause}
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
            df_billing_freq = run_query(query_rev1_billing_frequency, start_date, end_date)
            display_chart(df_billing_freq, "billing_frequency", "revenue", "Rev1 Billing Frequency Breakdown")
          #  display_chart_table_dual("Rev1 Billing Frequency Breakdown", df_billing_freq, "billing_frequency", ["revenue", "transaction_count"])

            query_rev1_desc = f"""
                SELECT t.description,
                    SUM(t.converted_amount) AS rev1_revenue
                FROM data_marts.combined_transactions t
                JOIN data_marts.combined_subscriptions cs ON t.student_id = cs.value__meta_data_lead_id
                JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND t.converted_amount > 0
                AND t.plan_id IS NOT NULL
                AND t.description NOT ILIKE '%lifetime%'
                AND t.description NOT ILIKE '%course%'
                AND t.description NOT ILIKE '%toolkit%'
                AND t.description NOT ILIKE '%hard%'
                {revenue_where_clause}
                GROUP BY t.description
                ORDER BY rev1_revenue DESC;
            """
            df_rev1_desc = run_query(query_rev1_desc, start_date, end_date)
            display_chart(df_rev1_desc, "description", "rev1_revenue", "Rev1 Breakdown by Description")


            query_rev2_desc = f"""
                WITH classified_txns AS (
                    SELECT t.*,
                        CASE
                            WHEN t.description ILIKE '%lifetime%' THEN 'Rev2'
                            WHEN t.description ILIKE '%certificate%' OR t.description ILIKE '%material%' OR t.description ILIKE '%diploma%' THEN 'Rev3'
                            WHEN t.plan_id IS NOT NULL THEN 'Rev1'
                            ELSE 'Other'
                        END AS revenue_type
                    FROM data_marts.combined_transactions t
                    JOIN data_marts.combined_subscriptions cs ON t.student_id = cs.value__meta_data_lead_id
                    JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                    WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                    AND t.converted_amount > 0
                    {revenue_where_clause}
                )
                SELECT
                    CASE
                        WHEN description ILIKE '%basic%' THEN 'Lifetime - Basic'
                        WHEN description ILIKE '%standard%' THEN 'Lifetime - Standard'
                        WHEN description ILIKE '%unlimited%' THEN 'Lifetime - Unlimited'
                        ELSE 'Lifetime - Other'
                    END AS rev2_type,
                    SUM(converted_amount) AS revenue,
                    COUNT(*) AS transaction_count
                FROM classified_txns
                WHERE revenue_type = 'Rev2'
                GROUP BY rev2_type
                ORDER BY revenue DESC;
            """
            df_rev2_desc = run_query(query_rev2_desc, start_date, end_date)
            display_chart(df_rev2_desc, "rev2_type", "revenue", "Rev2 Breakdown by Description")

            query_rev3_type = f"""
                WITH classified_txns AS (
                    SELECT t.*,
                        CASE
                            WHEN t.description ILIKE '%lifetime%' THEN 'Rev2'
                            WHEN t.description ILIKE '%certificate%' OR t.description ILIKE '%material%' OR t.description ILIKE '%diploma%' THEN 'Rev3'
                            WHEN t.plan_id IS NOT NULL THEN 'Rev1'
                            ELSE 'Other'
                        END AS revenue_type
                    FROM data_marts.combined_transactions t
                    JOIN data_marts.combined_subscriptions cs ON t.student_id = cs.value__meta_data_lead_id
                    JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                    WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                    AND t.converted_amount > 0
                    {revenue_where_clause}
                )
                SELECT
                    CASE
                        WHEN description ILIKE '%material%' THEN 'Rev3 - Toolkit'
                        WHEN description ILIKE '%hard%copy%diploma%' THEN 'Rev3 - Diploma'
                        WHEN description ILIKE '%certificate%' THEN 'Rev3 - Certificate'
                        ELSE 'Rev3 - Other'
                    END AS rev3_type,
                    SUM(converted_amount) AS revenue,
                    COUNT(*) AS transaction_count
                FROM classified_txns
                WHERE revenue_type = 'Rev3'
                AND (
                    description ILIKE '%material%'
                    OR description ILIKE '%diploma%'
                    OR description ILIKE '%certificate%'
                )
                GROUP BY rev3_type
                ORDER BY revenue DESC;
            """
            df_rev3_type = run_query(query_rev3_type, start_date, end_date)
            display_chart(df_rev3_type, "rev3_type", "revenue", "Rev3 Breakdown by Type")

            # Revenue by Country
            query_rev_country = f"""
                SELECT ds.country AS dimension_value,
                    SUM(t.converted_amount) AS revenue
                FROM data_marts.combined_transactions t
                JOIN data_marts.combined_subscriptions cs ON t.student_id = cs.value__meta_data_lead_id
                JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                WHERE cs.created_at BETWEEN '{{start_date}}' AND '{{end_date}}'
                AND t.converted_amount > 0
                AND t.student_id IS NOT NULL
                {revenue_where_clause.replace('WHERE', 'AND')}
                GROUP BY ds.country
                ORDER BY revenue DESC
            """
            df_rev_country = run_query(query_rev_country, start_date, end_date)
            display_chart(df_rev_country, "dimension_value", "revenue", "Revenue by Country")

            # Revenue by Partner Identifier
            query_rev_partner = f"""
                SELECT ds.profile__partner_identifier AS dimension_value,
                    SUM(t.converted_amount) AS revenue
                FROM data_marts.combined_transactions t
                JOIN data_marts.combined_subscriptions cs ON t.student_id = cs.value__meta_data_lead_id
                JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id
                WHERE cs.created_at BETWEEN '{{start_date}}' AND '{{end_date}}'
                AND t.converted_amount > 0
                AND t.student_id IS NOT NULL
                {revenue_where_clause.replace('WHERE', 'AND')}
                GROUP BY ds.profile__partner_identifier
                ORDER BY revenue DESC
            """
            df_rev_partner = run_query(query_rev_partner, start_date, end_date)
            display_chart(df_rev_partner, "dimension_value", "revenue", "Revenue by Partner Identifier")


            # Revenue by Coursepicked
            query_rev_by_course = f"""
                SELECT ds.coursepicked AS course,
                    SUM(t.converted_amount) AS revenue
                FROM data_marts.combined_transactions t
                JOIN data_marts.combined_subscriptions cs 
                    ON t.student_id = cs.value__meta_data_lead_id
                JOIN data_warehouse.dim_students ds 
                    ON ds.student_id = cs.value__meta_data_lead_id
                WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND t.converted_amount > 0
                {revenue_where_clause}
                GROUP BY ds.coursepicked
                ORDER BY revenue DESC;
            """
              # --- Revenue by Course Picked ---
            df_rev_by_course = run_query(query_rev_by_course, start_date, end_date)
            display_chart(df_rev_by_course, "course", "revenue", "Revenue by Course Picked")

            # Months_to_cc
            query_months_to_cc = f"""
                SELECT 
                DATEDIFF(month, ds.created_date, cs.created_at) AS months_to_cc,
                COUNT(DISTINCT ds.student_id) AS num_users
                FROM data_marts.combined_subscriptions cs
                JOIN data_warehouse.dim_students ds 
                ON ds.student_id = cs.value__meta_data_lead_id
                WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                {revenue_where_clause}
                GROUP BY 1
                ORDER BY 1
            """;
            df_months_to_cc = run_query(query_months_to_cc, start_date, end_date)
            st.subheader("📆 Months from Lead to CC Conversion")
            display_chart(df_months_to_cc, "months_to_cc", "num_users", "Lead-to-CC Conversion Time (in Months)")

            query_platform_revenue = f"""
                SELECT 
                cs.subscription_platform AS dimension_value,
                SUM(t.converted_amount) AS total_revenue,
                COUNT(*) AS transaction_count
                FROM data_marts.combined_transactions t
                JOIN data_marts.combined_subscriptions cs 
                ON t.student_id = cs.value__meta_data_lead_id
                JOIN data_warehouse.dim_students ds 
                ON ds.student_id = cs.value__meta_data_lead_id
                WHERE cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND t.converted_amount > 0
                {revenue_where_clause}
                GROUP BY cs.subscription_platform
                ORDER BY total_revenue DESC
            """

            df_platform_rev = run_query(query_platform_revenue, start_date, end_date)
            st.subheader("🧩 Revenue by Subscription Platform")
            display_chart(df_platform_rev, "dimension_value", "total_revenue", "Revenue by Platform (Chargebee, etc.)")


        with tabs[3]:
            st.header("📘  Details (Filtered for Qualified CCs)")
            course_details_where_clause = build_course_details_where_clause(selected_countries, selected_partners, selected_offers)
            

            # Monthly Registrations
            query = f"""
                SELECT DATE_TRUNC('month', dsc.registered_on) AS registration_month,
                    COUNT(DISTINCT dsc.registration_id) AS total_registrations,
                    COUNT(DISTINCT dsc.student_id) AS total_unique_students
                FROM data_warehouse.dim_schedules dsc
                JOIN data_marts.combined_subscriptions cs ON dsc.student_id = cs.value__meta_data_lead_id
                left JOIN data_warehouse.dim_students ds ON ds.student_id = dsc.student_id

                {course_details_where_clause}
                and cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY 1 ORDER BY 1;
            """
            df = run_query(query, start_date, end_date)
            display_chart(df, "registration_month", "total_registrations", "🗓️ Monthly Registrations")

            # Registrations by Country
            query = f"""
                SELECT ds.country, COUNT(DISTINCT dsc.registration_id) AS total_registrations
                FROM data_warehouse.dim_students ds
                JOIN data_marts.combined_subscriptions cs ON ds.student_id = cs.value__meta_data_lead_id
                JOIN data_warehouse.dim_schedules dsc ON ds.student_id = dsc.student_id
                
                {course_details_where_clause}
                and cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY ds.country ORDER BY total_registrations DESC;
            """
            df = run_query(query, start_date, end_date)
            display_chart(df, "country", "total_registrations", "🌍 Registrations by Country")

            # Registrations by Course
            query = f"""
                SELECT dsc.course_slug, COUNT(DISTINCT dsc.registration_id) AS total_registrations
                FROM data_warehouse.dim_schedules dsc
                JOIN data_marts.combined_subscriptions cs ON dsc.student_id = cs.value__meta_data_lead_id
                left JOIN data_warehouse.dim_students ds ON ds.student_id = dsc.student_id

                {course_details_where_clause}
                and cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                
                GROUP BY dsc.course_slug ORDER BY total_registrations DESC;
            """
            df = run_query(query, start_date, end_date)
            display_chart(df, "course_slug", "total_registrations", "🎯 Registrations by Course Slug")

            # Attendance by Course
            query = f"""
                SELECT COALESCE(dsc.course_slug, 'Unknown') AS course_slug,
                    COUNT(DISTINCT fa.value__student_id) AS total_students_attended
                FROM firestore_api.firestore_attendance fa
                JOIN data_warehouse.dim_schedules dsc ON fa.value__registrations_id = dsc.registration_id
                JOIN data_marts.combined_subscriptions cs ON dsc.student_id = cs.value__meta_data_lead_id
                left JOIN data_warehouse.dim_students ds ON ds.student_id = dsc.student_id

                
                {course_details_where_clause}
                and cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                and fa.value__watched__bigint > 300
                GROUP BY 1 ORDER BY total_students_attended DESC;
            """
            df = run_query(query, start_date, end_date)
            display_chart(df, "course_slug", "total_students_attended", "👨‍🏫 Attendance by Course")

            # Reactivated Users Metric
            query = f"""
                SELECT COUNT(DISTINCT cs.value__meta_data_lead_id) AS total_reactivated_users
                FROM data_marts.combined_subscriptions cs
                left JOIN data_warehouse.dim_students ds ON ds.student_id = cs.value__meta_data_lead_id

                {course_details_where_clause}
                and cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND cs.reactivated_on IS NOT NULL;
            """
            df = run_query(query, start_date, end_date)
            st.metric("🔄 Total Reactivated Users", f"{df.iloc[0]['total_reactivated_users']}")

            # Reactivated Users by Country
            query = f"""
                SELECT COALESCE(ds.country, 'Unknown') AS country,
                    COUNT(DISTINCT cs.value__meta_data_lead_id) AS total_reactivated_users
                FROM data_marts.combined_subscriptions cs
                JOIN data_warehouse.dim_students ds ON cs.value__meta_data_lead_id = ds.student_id
                {course_details_where_clause}
                and cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND cs.reactivated_on IS NOT NULL
                GROUP BY 1 ORDER BY total_reactivated_users DESC;
            """
            df = run_query(query, start_date, end_date)
            display_chart(df, "country", "total_reactivated_users", "🌎 Reactivated Users by Country")

            # Reactivated Users by Offer Type
            query = f"""
                SELECT COALESCE(ds.offer_type, 'Unknown') AS offer_type,
                    COUNT(DISTINCT cs.value__meta_data_lead_id) AS total_reactivated_users
                FROM data_marts.combined_subscriptions cs
                JOIN data_warehouse.dim_students ds ON cs.value__meta_data_lead_id = ds.student_id
                {course_details_where_clause}
                and cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND cs.reactivated_on IS NOT NULL
                GROUP BY 1 ORDER BY total_reactivated_users DESC;
            """
            df = run_query(query, start_date, end_date)
            display_chart(df, "offer_type", "total_reactivated_users", "🎁 Reactivated Users by Offer Type")

            # Reactivated Users by Month
            query = f"""
                SELECT DATE_TRUNC('month', cs.reactivated_on) AS reactivation_month,
                    COUNT(DISTINCT cs.value__meta_data_lead_id) AS total_reactivated_users
                FROM data_marts.combined_subscriptions cs
                JOIN data_warehouse.dim_students ds ON cs.value__meta_data_lead_id = ds.student_id
                {course_details_where_clause}
                and cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND cs.reactivated_on IS NOT NULL
                GROUP BY 1 ORDER BY 1;
            """
            df = run_query(query, start_date, end_date)
            display_chart(df, "reactivation_month", "total_reactivated_users", "📆 Reactivated Users by Month")



            st.subheader("🗓️ Monthly Registrations (After CC Date)")

            query_monthly_regs_after_cc = f"""
                SELECT DATE_TRUNC('month', dsc.registered_on) AS registration_month,
                    COUNT(DISTINCT dsc.registration_id) AS total_registrations,
                    COUNT(DISTINCT dsc.student_id) AS total_unique_students
                FROM data_warehouse.dim_schedules dsc
                JOIN data_marts.combined_subscriptions cs 
                    ON dsc.student_id = cs.value__meta_data_lead_id
                        JOIN data_warehouse.dim_students ds 
                     ON ds.student_id = dsc.student_id
                {course_details_where_clause}
                AND cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND dsc.registered_on > cs.created_at
                GROUP BY 1
                ORDER BY 1;
            """
            df_monthly_regs_after_cc = run_query(query_monthly_regs_after_cc, start_date, end_date)
            display_chart(df_monthly_regs_after_cc, "registration_month", "total_registrations", "🗓️ Monthly Registrations (Post-CC)")


            st.subheader("👨‍🏫 Attendance by Course (Watched > 0 sec)")

            query_attendance_by_course = f"""
                SELECT COALESCE(dsc.course_slug, 'Unknown') AS course_slug,
                    COUNT(DISTINCT fa.value__student_id) AS total_students_attended
                FROM firestore_api.firestore_attendance fa
                JOIN data_warehouse.dim_schedules dsc 
                    ON fa.value__registrations_id = dsc.registration_id
                JOIN data_marts.combined_subscriptions cs 
                    ON dsc.student_id = cs.value__meta_data_lead_id
                        JOIN data_warehouse.dim_students ds 
                      ON ds.student_id = dsc.student_id
                {course_details_where_clause}
                AND cs.created_at BETWEEN '{start_date}' AND '{end_date}'
                AND fa.value__watched__bigint > 0
                GROUP BY 1
                ORDER BY total_students_attended DESC;
            """
            df_attendance_by_course = run_query(query_attendance_by_course, start_date, end_date)
            display_chart(df_attendance_by_course, "course_slug", "total_students_attended", "👨‍🏫 Attendance by Course (Watched > 0 sec)")
