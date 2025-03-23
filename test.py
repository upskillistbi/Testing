import streamlit as st
import datetime
import pandas as pd
import psycopg2
import plotly.express as px

# Redshift connection
def run_query(query, start_date, end_date):
    conn = psycopg2.connect(
        host="misreporting.cxgsxkol4p2y.eu-west-1.redshift.amazonaws.com",
        port=5439,
        dbname="misreportingdb",
        user="etluser",
        password="Etluser12345"
    )
    cursor = conn.cursor()
    query = query.format(start_date=start_date, end_date=end_date)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# SQL Queries
SQL = {
    "total_leads":"""select COUNT(DISTINCT student_id) AS total_leads
                    FROM data_warehouse.dim_students
                    WHERE created_date BETWEEN '{start_date}' AND '{end_date}';""",

    "total_leads_utm_source":"""select utm_source, COUNT(DISTINCT student_id) AS total_leads
FROM data_warehouse.dim_students
WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
GROUP BY 1 ORDER BY total_leads DESC;""",
    
    "total_leads_utm_medium":"""select utm_medium, COUNT(DISTINCT student_id) AS total_leads
FROM data_warehouse.dim_students
WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
GROUP BY 1 ORDER BY total_leads DESC;""",

    "total_leads_profile_partner":"""select profile__partner_identifier AS partner, COUNT(DISTINCT student_id) AS total_leads
FROM data_warehouse.dim_students
WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
GROUP BY 1 ORDER BY total_leads DESC;""",

    "total_leads_course_picked":"""select coursepicked, COUNT(DISTINCT student_id) AS total_leads
FROM data_warehouse.dim_students
WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
GROUP BY 1 ORDER BY total_leads DESC;""",

    "total_leads_offer_type":"""select offer_type, COUNT(DISTINCT student_id) AS total_leads
FROM data_warehouse.dim_students
WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
GROUP BY 1 ORDER BY total_leads DESC;""",

    "total_leads_age_group":"""select 
    CASE 
        WHEN age_group IN ('18-21', '22-24') THEN '18-24'
        WHEN age_group IN ('25-30', '31-34') THEN '25-34'
        WHEN age_group IN ('35-40', '41-45') THEN '35-44'
        WHEN age_group IN ('46-50', '51-55') THEN '45-54'
        ELSE '55+'
    END AS age_bucket,
    COUNT(DISTINCT student_id) AS total_leads
FROM data_warehouse.dim_students
WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
GROUP BY 1 ORDER BY total_leads DESC;""",

    "qualified_leads": """
        SELECT COUNT(DISTINCT cs.id) AS qualified_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs 
            ON cs.value__meta_data_lead_id = ds.student_id
        WHERE ds.created_date BETWEEN '{start_date}' AND '{end_date}';
    """,
    "conversion_rate": """
        WITH total_leads AS (
            SELECT COUNT(DISTINCT student_id) AS total_leads
            FROM data_warehouse.dim_students
            WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
        ),
        qualified_leads AS (
            SELECT COUNT(DISTINCT cs.id) AS qualified_leads
            FROM data_warehouse.dim_students ds
            JOIN data_marts.combined_subscriptions cs 
                ON cs.value__meta_data_lead_id = ds.student_id
            WHERE ds.created_date BETWEEN '{start_date}' AND '{end_date}'
        )
        SELECT 
            tl.total_leads,
            ql.qualified_leads,
            (ql.qualified_leads * 100.0 / NULLIF(tl.total_leads, 0)) AS conversion_rate
        FROM total_leads tl
        JOIN qualified_leads ql ON 1=1;
    """,
    "cancelled_leads": """
        SELECT COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
        FROM data_marts.combined_subscriptions cs
        WHERE cs.cancellation_intiated_on BETWEEN '{start_date}' AND '{end_date}';
    """,
    "total_by_country": """
        SELECT country, COUNT(DISTINCT student_id) AS total_leads
        FROM data_warehouse.dim_students
        WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY 1 ORDER BY total_leads DESC;
    """,
    "total_by_utm": """
        SELECT utm_source, COUNT(DISTINCT student_id) AS total_leads
        FROM data_warehouse.dim_students
        WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY 1 ORDER BY total_leads DESC;
    """,
    "total_by_partner": """
        SELECT profile__partner_identifier AS partner, COUNT(DISTINCT student_id) AS total_leads
        FROM data_warehouse.dim_students
        WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY 1 ORDER BY total_leads DESC;
    """
}



# SQL Queries for Cancelled Leads
cancelled_leads_queries = {
    "cancelled_total": """
        SELECT COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
        FROM data_marts.combined_subscriptions cs
        WHERE cs.cancellation_intiated_on BETWEEN '{start_date}' AND '{end_date}';
    """,
    "cancelled_by_country": """
        SELECT ds.country, COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs ON ds.student_id = cs.value__meta_data_lead_id
        WHERE cs.cancellation_intiated_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY ds.country ORDER BY cancelled_leads DESC;
    """,
    "cancelled_by_utm_source": """
        SELECT ds.utm_source, COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs ON ds.student_id = cs.value__meta_data_lead_id
        WHERE cs.cancellation_intiated_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY ds.utm_source ORDER BY cancelled_leads DESC;
    """,
    "cancelled_by_partner": """
        SELECT ds.profile__partner_identifier AS partner, COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs ON ds.student_id = cs.value__meta_data_lead_id
        WHERE cs.cancellation_intiated_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY ds.profile__partner_identifier ORDER BY cancelled_leads DESC;
    """,
    "cancelled_by_offer_type": """
        SELECT ds.offer_type, COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs ON ds.student_id = cs.value__meta_data_lead_id
        WHERE cs.cancellation_intiated_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY ds.offer_type ORDER BY cancelled_leads DESC;
    """,
    "cancelled_by_course_picked": """
        SELECT ds.coursepicked, COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs ON ds.student_id = cs.value__meta_data_lead_id
        WHERE cs.cancellation_intiated_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY ds.coursepicked ORDER BY cancelled_leads DESC;
    """,
    "cancelled_by_age_group": """
        SELECT 
            CASE 
                WHEN ds.age_group IN ('18-21', '22-24') THEN '18-24'
                WHEN ds.age_group IN ('25-30', '31-34') THEN '25-34'
                WHEN ds.age_group IN ('35-40', '41-45') THEN '35-44'
                WHEN ds.age_group IN ('46-50', '51-55') THEN '45-54'
                ELSE '55+'
            END AS age_bucket,
            COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs ON ds.student_id = cs.value__meta_data_lead_id
        WHERE cs.cancellation_intiated_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY 1 ORDER BY cancelled_leads DESC;
    """
}


# --- SQL Queries ---
sql_mom = {
    "leads": """
        SELECT DATE_TRUNC('month', created_date) AS month, COUNT(DISTINCT student_id) AS total_leads
        FROM data_warehouse.dim_students
        WHERE created_date >= '2023-01-01'
        GROUP BY 1 ORDER BY 1;
    """,
    "qualified": """
        SELECT DATE_TRUNC('month', ds.created_date) AS month, COUNT(DISTINCT cs.id) AS qualified_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs 
            ON cs.value__meta_data_lead_id = ds.student_id
        WHERE ds.created_date >= '2023-01-01'
        GROUP BY 1 ORDER BY 1;
    """,
    "cancelled": """
        SELECT DATE_TRUNC('month', cancellation_intiated_on) AS month, COUNT(DISTINCT value__meta_data_lead_id) AS cancelled_leads
        FROM data_marts.combined_subscriptions
        WHERE cancellation_intiated_on >= '2023-01-01'
        GROUP BY 1 ORDER BY 1;
    """,
    "conversion": """
        WITH leads AS (
            SELECT DATE_TRUNC('month', created_date) AS month, COUNT(DISTINCT student_id) AS total_leads
            FROM data_warehouse.dim_students
            WHERE created_date >= '2023-01-01'
            GROUP BY 1
        ),
        qualified AS (
            SELECT DATE_TRUNC('month', ds.created_date) AS month, COUNT(DISTINCT cs.id) AS qualified_leads
            FROM data_warehouse.dim_students ds
            JOIN data_marts.combined_subscriptions cs 
                ON cs.value__meta_data_lead_id = ds.student_id
            WHERE ds.created_date >= '2023-01-01'
            GROUP BY 1
        )
        SELECT 
            l.month,
            l.total_leads,
            q.qualified_leads,
            (q.qualified_leads * 100.0 / NULLIF(l.total_leads, 0)) AS conversion_rate
        FROM leads l
        LEFT JOIN qualified q ON l.month = q.month
        ORDER BY l.month;
    """,
    "leads_mom": """
        SELECT DATE_TRUNC('month', created_date) AS month, COUNT(DISTINCT student_id) AS total_leads
        FROM data_warehouse.dim_students
        WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY 1 ORDER BY 1;
    """,
    "qualified_mom": """
        SELECT DATE_TRUNC('month', ds.created_date) AS month, COUNT(DISTINCT cs.id) AS qualified_leads
        FROM data_warehouse.dim_students ds
        JOIN data_marts.combined_subscriptions cs 
        ON cs.value__meta_data_lead_id = ds.student_id
        WHERE ds.created_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY 1 ORDER BY 1;
    """,
    "cancelled_mom": """
        SELECT DATE_TRUNC('month', cancellation_intiated_on) AS month, COUNT(DISTINCT value__meta_data_lead_id) AS cancelled_leads
        FROM data_marts.combined_subscriptions
        WHERE cancellation_intiated_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY 1 ORDER BY 1;
    """,
    "conversion_mom": """
        WITH leads AS (
            SELECT DATE_TRUNC('month', created_date) AS month, COUNT(DISTINCT student_id) AS total_leads
            FROM data_warehouse.dim_students
            WHERE created_date BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY 1
        ),
        qualified AS (
            SELECT DATE_TRUNC('month', ds.created_date) AS month, COUNT(DISTINCT cs.id) AS qualified_leads
            FROM data_warehouse.dim_students ds
            JOIN data_marts.combined_subscriptions cs 
            ON cs.value__meta_data_lead_id = ds.student_id
            WHERE ds.created_date BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY 1
        )
        SELECT l.month, l.total_leads, q.qualified_leads,
            (q.qualified_leads * 100.0 / NULLIF(l.total_leads, 0)) AS conversion_rate
        FROM leads l
        LEFT JOIN qualified q ON l.month = q.month
        ORDER BY l.month;
    """,
    "utm_kpis": """
        SELECT 
            utm_source,
            COUNT(DISTINCT ds.student_id) AS total_leads,
            COUNT(DISTINCT cs.id) AS qualified_leads,
            COUNT(DISTINCT CASE WHEN cs.cancellation_intiated_on IS NOT NULL THEN cs.value__meta_data_lead_id END) AS cancelled_leads
        FROM data_warehouse.dim_students ds
        LEFT JOIN data_marts.combined_subscriptions cs 
        ON cs.value__meta_data_lead_id = ds.student_id
        WHERE ds.created_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY 1 ORDER BY 2 DESC LIMIT 5;
    """
}

# Streamlit layout config
st.set_page_config(page_title="Lead to CC Funnel", layout="wide")

# Sidebar Metrics (placeholder)
st.sidebar.title("📊 KPI Overview")

# Date Filters + Run Button
st.title("📊 Lead to Credit Card Funnel Dashboard")
col1, col2 = st.columns(2)
start_date = col1.date_input("📅 Start Date", datetime.date(2025, 1, 1))
end_date = col2.date_input("📅 End Date", datetime.date(2025, 3, 31))
run_button = st.button("🔄 Run Analysis")

# Load data on button click
if run_button:
    st.success("✅ Query complete!")

    # Load all queries
    total = run_query(SQL["total_leads"], start_date, end_date).iloc[0, 0]
    qualified = run_query(SQL["qualified_leads"], start_date, end_date).iloc[0, 0]
    cancelled = run_query(SQL["cancelled_leads"], start_date, end_date).iloc[0, 0]
    conversion_df = run_query(SQL["conversion_rate"], start_date, end_date)
    conversion_pct = conversion_df.iloc[0]["conversion_rate"]

    # Update sidebar
    st.sidebar.metric("📥 Total Leads", f"{total:,}")
    st.sidebar.metric("🎯 Qualified Leads", f"{qualified:,}")
    st.sidebar.metric("🔁 Conversion Rate", f"{conversion_pct:.2f}%")
    st.sidebar.metric("❌ Cancelled Leads", f"{cancelled:,}")

    # Tabs for breakdowns
    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 Total Leads",
        "🎯 Qualified Leads",
        "🔁 Infographics",
        "❌ Cancelled Leads"
    ])

    with tab1:
            st.subheader("📊 Breakdown of Total Leads")
            st.metric("📥 Total Leads (All Sources)", f"{total:,}")
        ##   by_utm_medium=run_query(SQL["total_leads_utm_medium"] ,start_date, end_date)
            by_country = run_query(SQL["total_by_country"], start_date, end_date)
            by_utm = run_query(SQL["total_by_utm"], start_date, end_date)
            by_partner = run_query(SQL["total_by_partner"], start_date, end_date)
            total_leads_course_picked= run_query(SQL["total_leads_course_picked"], start_date, end_date)
        ## total_leads_profile_partner= run_query(SQL["total_leads_profile_partner"], start_date, end_date)
            total_leads_offer_type= run_query(SQL["total_leads_offer_type"], start_date, end_date)
            total_leads_age_group= run_query(SQL["total_leads_age_group"], start_date, end_date)

        
            st.markdown(f"🧠 **Top Country**: `{by_country.iloc[0]['country']}` with `{by_country.iloc[0]['total_leads']:,}` leads.")
            st.markdown(f"🔍 **Top UTM Source**: `{by_utm.iloc[0]['utm_source']}` with `{by_utm.iloc[0]['total_leads']:,}` leads.")
            st.markdown(f"🤝 **Top Partner**: `{by_partner.iloc[0]['partner']}` with `{by_partner.iloc[0]['total_leads']:,}` leads.")
            st.markdown(f"🤝 **Top Course**: `{total_leads_course_picked.iloc[0]['coursepicked']}` with `{total_leads_course_picked.iloc[0]['total_leads']:,}` leads.")
            st.markdown(f"🤝 **Top Age group**: `{total_leads_age_group.iloc[0]['age_bucket']}` with `{total_leads_age_group.iloc[0]['total_leads']:,}` leads.")
            st.markdown(f"🤝 **Top Offer**: `{total_leads_offer_type.iloc[0]['offer_type']}` with `{total_leads_offer_type.iloc[0]['total_leads']:,}` leads.")



                # First Row: Country & UTM Source
            col1, col2 = st.columns(2)
            with col1:
                    st.write("### 📍 Leads by Country")
                    st.dataframe(by_country)
                    fig_country = px.bar(by_country, x='country', y='total_leads', title='Leads by Country', text='total_leads')
                    st.plotly_chart(fig_country, use_container_width=True)

            with col2:
                    st.write("### 🔍 Leads by UTM Source")
                    st.dataframe(by_utm)
                    fig_utm = px.bar(by_utm, x='utm_source', y='total_leads', title='Leads by UTM Source', text='total_leads')
                    st.plotly_chart(fig_utm, use_container_width=True)

                # Second Row: Partner & Course
            col3, col4 = st.columns(2)

            with col3:
                    st.write("### 🤝 Leads by Partner Identifier")
                    st.dataframe(by_partner)
                    fig_partner = px.bar(by_partner, x='partner', y='total_leads', title='Leads by Partner', text='total_leads')
                    st.plotly_chart(fig_partner, use_container_width=True)

            with col4:
                    st.write("### 📘 Leads by Course Picked")
                    st.dataframe(total_leads_course_picked)
                    fig_course = px.bar(total_leads_course_picked, x='coursepicked', y='total_leads', title='Leads by Course', text='total_leads')
                    st.plotly_chart(fig_course, use_container_width=True)

                # Third Row: Offer & Age Group
            col5, col6 = st.columns(2)

            with col5:
                    st.write("### 🏷️ Leads by Offer Type")
                    st.dataframe(total_leads_offer_type)
                    fig_offer = px.bar(total_leads_offer_type, x='offer_type', y='total_leads', title='Leads by Offer Type', text='total_leads')
                    st.plotly_chart(fig_offer, use_container_width=True)

            with col6:
                    st.write("### 👥 Leads by Age Group")
                    st.dataframe(total_leads_age_group)
                    fig_age = px.bar(total_leads_age_group, x='age_bucket', y='total_leads', title='Leads by Age Group', text='total_leads')
                    st.plotly_chart(fig_age, use_container_width=True)
                        

    with tab2:
            st.subheader("🎯 Breakdown of Qualified Leads")
            st.metric("🎯 Qualified Leads (All Sources)", f"{qualified:,}")

            # Run qualified lead breakdown queries
            q_by_country = run_query(SQL["total_by_country"].replace("total_leads", "qualified_leads")
                                    .replace("student_id", "cs.id")
                                    .replace("dim_students", "dim_students ds JOIN data_marts.combined_subscriptions cs ON cs.value__meta_data_lead_id = ds.student_id"), 
                                    start_date, end_date)

            q_by_utm = run_query(SQL["total_by_utm"].replace("total_leads", "qualified_leads")
                                .replace("student_id", "cs.id")
                                .replace("dim_students", "dim_students ds JOIN data_marts.combined_subscriptions cs ON cs.value__meta_data_lead_id = ds.student_id"), 
                                start_date, end_date)

            q_by_partner = run_query(SQL["total_by_partner"].replace("total_leads", "qualified_leads")
                                    .replace("student_id", "cs.id")
                                    .replace("dim_students", "dim_students ds JOIN data_marts.combined_subscriptions cs ON cs.value__meta_data_lead_id = ds.student_id"), 
                                    start_date, end_date)

            q_course = run_query(SQL["total_leads_course_picked"].replace("total_leads", "qualified_leads")
                                .replace("dim_students", "dim_students ds JOIN data_marts.combined_subscriptions cs ON cs.value__meta_data_lead_id = ds.student_id"), 
                                start_date, end_date)

            q_offer = run_query(SQL["total_leads_offer_type"].replace("total_leads", "qualified_leads")
                                .replace("dim_students", "dim_students ds JOIN data_marts.combined_subscriptions cs ON cs.value__meta_data_lead_id = ds.student_id"), 
                                start_date, end_date)

            q_age = run_query(SQL["total_leads_age_group"].replace("total_leads", "qualified_leads")
                            .replace("dim_students", "dim_students ds JOIN data_marts.combined_subscriptions cs ON cs.value__meta_data_lead_id = ds.student_id"), 
                            start_date, end_date)

            # Top Highlights
            st.markdown(f"🧠 **Top Country**: `{q_by_country.iloc[0]['country']}` with `{q_by_country.iloc[0]['qualified_leads']:,}` qualified leads.")
            st.markdown(f"🔍 **Top UTM Source**: `{q_by_utm.iloc[0]['utm_source']}` with `{q_by_utm.iloc[0]['qualified_leads']:,}` qualified leads.")
            st.markdown(f"🤝 **Top Partner**: `{q_by_partner.iloc[0]['partner']}` with `{q_by_partner.iloc[0]['qualified_leads']:,}` qualified leads.")
            st.markdown(f"📘 **Top Course**: `{q_course.iloc[0]['coursepicked']}` with `{q_course.iloc[0]['qualified_leads']:,}` qualified leads.")
            st.markdown(f"👥 **Top Age Group**: `{q_age.iloc[0]['age_bucket']}` with `{q_age.iloc[0]['qualified_leads']:,}` qualified leads.")
            st.markdown(f"🏷️ **Top Offer Type**: `{q_offer.iloc[0]['offer_type']}` with `{q_offer.iloc[0]['qualified_leads']:,}` qualified leads.")

            # First Row
            col1, col2 = st.columns(2)
            with col1:
                st.write("### 📍 Qualified Leads by Country")
                st.dataframe(q_by_country)
                fig = px.bar(q_by_country, x="country", y="qualified_leads", text="qualified_leads", title="Qualified Leads by Country")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.write("### 🔍 Qualified Leads by UTM Source")
                st.dataframe(q_by_utm)
                fig = px.bar(q_by_utm, x="utm_source", y="qualified_leads", text="qualified_leads", title="Qualified Leads by UTM Source")
                st.plotly_chart(fig, use_container_width=True)

            # Second Row
            col3, col4 = st.columns(2)
            with col3:
                st.write("### 🤝 Qualified Leads by Partner")
                st.dataframe(q_by_partner)
                fig = px.bar(q_by_partner, x="partner", y="qualified_leads", text="qualified_leads", title="Qualified Leads by Partner")
                st.plotly_chart(fig, use_container_width=True)

            with col4:
                st.write("### 📘 Qualified Leads by Course Picked")
                st.dataframe(q_course)
                fig = px.bar(q_course, x="coursepicked", y="qualified_leads", text="qualified_leads", title="Qualified Leads by Course")
                st.plotly_chart(fig, use_container_width=True)

            # Third Row
            col5, col6 = st.columns(2)
            with col5:
                st.write("### 🏷️ Qualified Leads by Offer Type")
                st.dataframe(q_offer)
                fig = px.bar(q_offer, x="offer_type", y="qualified_leads", text="qualified_leads", title="Qualified Leads by Offer Type")
                st.plotly_chart(fig, use_container_width=True)

            with col6:
                st.write("### 👥 Qualified Leads by Age Group")
                st.dataframe(q_age)
                fig = px.bar(q_age, x="age_bucket", y="qualified_leads", text="qualified_leads", title="Qualified Leads by Age Group")
                st.plotly_chart(fig, use_container_width=True)


    with tab3:
            leads_df = run_query(sql_mom["leads_mom"], start_date, end_date)
            qualified_df = run_query(sql_mom["qualified_mom"], start_date, end_date)
            cancelled_df = run_query(sql_mom["cancelled_mom"], start_date, end_date)
            conversion_df = run_query(sql_mom["conversion_mom"], start_date, end_date)
            utm_df = run_query(sql_mom["utm_kpis"], start_date, end_date)

                # --- UTM KPI Cards
            st.subheader("🔍 UTM Source KPIs (Top 5)")
            for i in range(len(utm_df)):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric(f"🔗 {utm_df.iloc[i]['utm_source']}", "")
                    col2.metric("📥 Leads", utm_df.iloc[i]['total_leads'])
                    col3.metric("🎯 Qualified", utm_df.iloc[i]['qualified_leads'])
                    col4.metric("❌ Cancelled", utm_df.iloc[i]['cancelled_leads'])

                # --- Charts
            st.subheader("📈 Month-over-Month Trends")

            fig1 = px.line(leads_df, x="month", y="total_leads", title="Monthly Total Leads", markers=True)
            fig2 = px.line(qualified_df, x="month", y="qualified_leads", title="Monthly Qualified Leads", markers=True)
            fig3 = px.line(cancelled_df, x="month", y="cancelled_leads", title="Monthly Cancelled Leads", markers=True)
            fig4 = px.line(conversion_df, x="month", y="conversion_rate", title="Monthly Conversion Rate (%)", markers=True)

            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)
            st.plotly_chart(fig3, use_container_width=True)
            st.plotly_chart(fig4, use_container_width=True)

        
    with tab4:
            st.subheader("❌ Cancellations Breakdown")

            cancelled_total = run_query(cancelled_leads_queries["cancelled_total"], start_date, end_date).iloc[0, 0]
            st.metric("❌ Total Cancelled Leads", f"{cancelled_total:,}")

            # Pulling metric data
            cancelled_by_country = run_query(cancelled_leads_queries["cancelled_by_country"], start_date, end_date)
            cancelled_by_utm = run_query(cancelled_leads_queries["cancelled_by_utm_source"], start_date, end_date)
            cancelled_by_partner = run_query(cancelled_leads_queries["cancelled_by_partner"], start_date, end_date)
            cancelled_by_offer_type = run_query(cancelled_leads_queries["cancelled_by_offer_type"], start_date, end_date)
            cancelled_by_course = run_query(cancelled_leads_queries["cancelled_by_course_picked"], start_date, end_date)
            cancelled_by_age = run_query(cancelled_leads_queries["cancelled_by_age_group"], start_date, end_date)

            # Insights Section
            st.markdown("### 🔍 Highlights")
            if not cancelled_by_country.empty:
                st.markdown(f"🌍 **Top Country**: `{cancelled_by_country.iloc[0]['country']}` with `{cancelled_by_country.iloc[0]['cancelled_leads']:,}` cancellations")
            if not cancelled_by_utm.empty:
                st.markdown(f"🔗 **Top UTM Source**: `{cancelled_by_utm.iloc[0]['utm_source']}` with `{cancelled_by_utm.iloc[0]['cancelled_leads']:,}` cancellations")
            if not cancelled_by_partner.empty:
                st.markdown(f"🤝 **Top Partner**: `{cancelled_by_partner.iloc[0]['partner']}` with `{cancelled_by_partner.iloc[0]['cancelled_leads']:,}` cancellations")
            if not cancelled_by_offer_type.empty:
                st.markdown(f"🤝 **offer_type**: `{cancelled_by_offer_type.iloc[0]['offer_type']}` with `{cancelled_by_offer_type.iloc[0]['cancelled_leads']:,}` cancellations")
            if not cancelled_by_course.empty:
                st.markdown(f"🤝 **Top Course**: `{cancelled_by_course.iloc[0]['coursepicked']}` with `{cancelled_by_course.iloc[0]['cancelled_leads']:,}` cancellations")
            if not cancelled_by_age.empty:
                st.markdown(f"🤝 **Top Age**: `{cancelled_by_age.iloc[0]['age_bucket']}` with `{cancelled_by_age.iloc[0]['cancelled_leads']:,}` cancellations")
        

            # Reusable function for chart + table
            def chart_table(title, df, xcol, ycol):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"### {title}")
                    st.dataframe(df)
                with col2:
                    fig = px.bar(df, x=xcol, y=ycol, text=ycol, title=title)
                    st.plotly_chart(fig, use_container_width=True)

            # Visual Breakdowns
            chart_table("📍 Cancelled by Country", cancelled_by_country, "country", "cancelled_leads")
            chart_table("🔍 Cancelled by UTM Source", cancelled_by_utm, "utm_source", "cancelled_leads")
            chart_table("🤝 Cancelled by Partner", cancelled_by_partner, "partner", "cancelled_leads")
            chart_table("🏷️ Cancelled by Offer Type", cancelled_by_offer_type, "offer_type", "cancelled_leads")
            chart_table("📘 Cancelled by Course Picked", cancelled_by_course, "coursepicked", "cancelled_leads")
            chart_table("👥 Cancelled by Age Group", cancelled_by_age, "age_bucket", "cancelled_leads")

else:
    st.info("📅 Select a date range and click 'Run Analysis' to load data.")
