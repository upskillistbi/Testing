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

reactivation_queries_clean = {
    # 1. Total Reactivated Users
    "Total Reactivated Users": """
        SELECT 
            COUNT(DISTINCT value__meta_data_lead_id) AS total_reactivated_users
        FROM data_marts.combined_subscriptions
        WHERE reactivated_on BETWEEN '{start_date}' AND '{end_date}';
    """,

    # 2. Reactivated Users by Country
    "Reactivated Users by Country": """
        SELECT 
            COALESCE(ds.country, 'Unknown') AS country,
            COUNT(DISTINCT cs.value__meta_data_lead_id) AS total_reactivated_users
        FROM data_marts.combined_subscriptions cs
        JOIN data_warehouse.dim_students ds 
            ON cs.value__meta_data_lead_id = ds.student_id
        WHERE cs.reactivated_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(ds.country, 'Unknown')
        ORDER BY total_reactivated_users DESC;
    """,

    # 3. Reactivated Users by Age Group
    "Reactivated Users by Age Group": """
        SELECT 
            COALESCE(ds.age_group, 'Unknown') AS age_group,
            COUNT(DISTINCT cs.value__meta_data_lead_id) AS total_reactivated_users
        FROM data_marts.combined_subscriptions cs
        JOIN data_warehouse.dim_students ds 
            ON cs.value__meta_data_lead_id = ds.student_id
        WHERE cs.reactivated_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(ds.age_group, 'Unknown')
        ORDER BY total_reactivated_users DESC;
    """,

    # 4. Reactivated Users by UTM Source
    "Reactivated Users by UTM Source": """
        SELECT 
            COALESCE(ds.latest_utm_source, 'Unknown') AS utm_source,
            COUNT(DISTINCT cs.value__meta_data_lead_id) AS total_reactivated_users
        FROM data_marts.combined_subscriptions cs
        JOIN data_warehouse.dim_students ds 
            ON cs.value__meta_data_lead_id = ds.student_id
        WHERE cs.reactivated_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(ds.latest_utm_source, 'Unknown')
        ORDER BY total_reactivated_users DESC;
    """,

    # 5. Reactivated Users by Offer Type
    "Reactivated Users by Offer Type": """
        SELECT 
            COALESCE(ds.offer_type, 'Unknown') AS offer_type,
            COUNT(DISTINCT cs.value__meta_data_lead_id) AS total_reactivated_users
        FROM data_marts.combined_subscriptions cs
        JOIN data_warehouse.dim_students ds 
            ON cs.value__meta_data_lead_id = ds.student_id
        WHERE cs.reactivated_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(ds.offer_type, 'Unknown')
        ORDER BY total_reactivated_users DESC;
    """,



    # 7. Reactivated Users by Month
    "Reactivated Users by Month": """
        SELECT 
            DATE_TRUNC('month', reactivated_on) AS month,
            COUNT(DISTINCT value__meta_data_lead_id) AS total_reactivated_users
        FROM data_marts.combined_subscriptions
        WHERE reactivated_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DATE_TRUNC('month', reactivated_on)
        ORDER BY month;
    """,

    # 8. Reactivated Users by Course (Post Reactivation Attendance)
    "Reactivated Users by Course": """
        SELECT 
            COALESCE(DSC.course_slug, 'Unknown') AS course_slug,
            COUNT(DISTINCT FA.value__student_id) AS total_reactivated_users
        FROM data_marts.combined_subscriptions CS
        JOIN data_warehouse.dim_schedules DSC 
            ON CS.value__meta_data_lead_id = DSC.student_id 
           AND DSC.registered_on >= CS.reactivated_on
        JOIN firestore_api.firestore_attendance FA 
            ON DSC.registration_id = FA.value__registrations_id
           AND FA.value__create_at >= CS.reactivated_on
        WHERE FA.value__watched__bigint > 0
        GROUP BY COALESCE(DSC.course_slug, 'Unknown')
        ORDER BY total_reactivated_users DESC;
    """,

    # 9. Reactivated + Attended At Least One Lesson
    "Reactivated Attended At Least One Lesson": """
        SELECT 
            COALESCE(DSC.course_slug, 'Unknown') AS course_slug,
            COUNT(DISTINCT FA.value__student_id) AS attended_users
        FROM data_marts.combined_subscriptions CS
        JOIN data_warehouse.dim_schedules DSC 
            ON CS.value__meta_data_lead_id = DSC.student_id 
           AND DSC.registered_on >= CS.reactivated_on
        JOIN firestore_api.firestore_attendance FA 
            ON DSC.registration_id = FA.value__registrations_id
           AND FA.value__create_at >= CS.reactivated_on
        WHERE FA.value__watched__bigint > 0
        GROUP BY COALESCE(DSC.course_slug, 'Unknown')
        ORDER BY attended_users DESC;
    """,

    # 10. Reactivated + Full Attendance (Dynamic Lessons)
    "Reactivated Full Attendance": """
        WITH course_total_lessons AS (
            SELECT 
                course_slug,
                COUNT(DISTINCT value__lesson_number__bigint) AS total_lessons
            FROM firestore_api.firestore_attendance
            WHERE value__watched__bigint > 0
            GROUP BY course_slug
        ),
        attendance_counts AS (
            SELECT 
                DSC.course_slug,
                FA.value__registrations_id AS registration_id,
                COUNT(DISTINCT FA.value__lesson_number__bigint) AS lessons_watched
            FROM data_marts.combined_subscriptions CS
            JOIN data_warehouse.dim_schedules DSC 
                ON CS.value__meta_data_lead_id = DSC.student_id 
               AND DSC.registered_on >= CS.reactivated_on
            JOIN firestore_api.firestore_attendance FA 
                ON DSC.registration_id = FA.value__registrations_id
               AND FA.value__create_at >= CS.reactivated_on
            WHERE FA.value__watched__bigint > 0
            GROUP BY DSC.course_slug, FA.value__registrations_id
        )
        SELECT 
            ac.course_slug,
            COUNT(DISTINCT ac.registration_id) AS full_attendance_users
        FROM attendance_counts ac
        JOIN course_total_lessons ctl 
            ON ac.course_slug = ctl.course_slug
        WHERE ac.lessons_watched = ctl.total_lessons
        GROUP BY ac.course_slug
        ORDER BY full_attendance_users DESC;
    """,

    # 11. Reactivated + Cancelled Again
    "Reactivated Cancelled Again": """
        SELECT 
            COALESCE(DSC.course_slug, 'Unknown') AS course_slug,
            COUNT(DISTINCT CS.value__meta_data_lead_id) AS cancelled_again
        FROM data_marts.combined_subscriptions CS
        LEFT JOIN data_warehouse.dim_schedules DSC 
            ON CS.value__meta_data_lead_id = DSC.student_id 
           AND DSC.registered_on >= CS.reactivated_on
        WHERE CS.reactivated_on BETWEEN '{start_date}' AND '{end_date}'
          AND CS.cancelled_after_reactivation = TRUE
        GROUP BY COALESCE(DSC.course_slug, 'Unknown')
        ORDER BY cancelled_again DESC;
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
    # Tabs for breakdowns
    tab7, = st.tabs(["♻️ Reactivations"])


    with tab7:
        st.title("♻️ Reactivations Analysis (Clean — Post Reactivation Only)")

            # Load data from your clean SQL dictionary
    st.info(f"Showing data for selected range: **{start_date} to {end_date}**")

    for metric_name, query in reactivation_queries_clean.items():
        st.markdown(f"### {metric_name}")
        df = run_query(query, start_date, end_date)

        if not df.empty:
            # Display data table
            st.dataframe(df)

            # --- Top Insights ---
            top_row = df.iloc[0]
            if "Course" in metric_name and df.columns[0] in ["course_slug", "course_id"]:
                st.markdown(f"🚀 **Top Course:** `{top_row[df.columns[0]]}` with `{top_row[df.columns[1]]:,}` users")
            if "Country" in metric_name:
                st.markdown(f"🌍 **Top Country:** `{top_row['country']}` with `{top_row[df.columns[1]]:,}` users")
            if "Age Group" in metric_name:
                st.markdown(f"👥 **Top Age Group:** `{top_row['age_group']}` with `{top_row[df.columns[1]]:,}` users")
            if "UTM" in metric_name:
                st.markdown(f"🔗 **Top UTM Source:** `{top_row['utm_source']}` with `{top_row[df.columns[1]]:,}` users")
            if "Offer Type" in metric_name:
                st.markdown(f"🏷️ **Top Offer Type:** `{top_row['offer_type']}` with `{top_row[df.columns[1]]:,}` users")
            if "Cancelled Again" in metric_name:
                st.markdown(f"❌ **Top Course for Repeat Cancellations:** `{top_row['course_slug']}` with `{top_row['cancelled_again']:,}` users")
            if "Full Attendance" in metric_name:
                st.markdown(f"🏆 **Top Full Attendance Course:** `{top_row['course_slug']}` with `{top_row['full_attendance_users']:,}` users")

            # --- Chart (Bar or Line auto-detect) ---
            numeric_cols = [col for col in df.columns if df[col].dtype != 'object']
            if len(numeric_cols) >= 1:
                x_col = df.columns[0]
                y_col = numeric_cols[0]

                if "Month" in metric_name or "Trend" in metric_name:
                    fig = px.line(df, x=x_col, y=y_col, markers=True, title=metric_name)
                else:
                    fig = px.bar(df, x=x_col, y=y_col, text=y_col, title=metric_name)

                st.plotly_chart(fig, use_container_width=True)

            # --- CSV Export ---
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"Download {metric_name} as CSV",
                data=csv,
                file_name=f"{metric_name.replace(' ', '_').lower()}.csv",
                mime='text/csv',
            )

        else:
            st.warning(f"No data available for **{metric_name}** in the selected date range.")



else:
    st.info("📅 Select a date range and click 'Run Analysis' to load data.")

    
