import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# Database credentials
DB_CONFIG = {
    'host': "misreporting.cxgsxkol4p2y.eu-west-1.redshift.amazonaws.com",
    'port': 5439,
    'dbname': "misreportingdb",
    'user': "etluser",
    'password': "Etluser12345"
}

def run_query():
    query = """
    WITH attendance_filtered AS (
        SELECT 
            value__student_id AS student_id,
            value__course_slug AS course_slug,
            value__lesson_number__bigint AS lesson_number,
            value__watched__bigint AS watch_time,
            DATE_TRUNC('month', value__create_at::timestamp) AS watch_month
        FROM firestore_api.firestore_attendance
        WHERE value__watched__bigint > 0 AND value__create_at >= '2025-01-01'
    ),

    student_summary AS (
        SELECT 
            student_id,
            course_slug,
            COUNT(DISTINCT lesson_number) AS lessons_watched,
            SUM(watch_time) AS total_watch_time
        FROM attendance_filtered
        GROUP BY student_id, course_slug
    ),

    basic_kpis AS (
        SELECT 
            (SELECT course_slug FROM attendance_filtered GROUP BY course_slug ORDER BY SUM(watch_time) DESC LIMIT 1) AS most_watched_course,
            (SELECT AVG(total_watch_time) FROM student_summary) AS avg_watch_time_per_student,
            (SELECT AVG(lessons_watched) FROM student_summary) AS avg_lessons_per_student
    ),

    top_courses AS (
        SELECT course_slug
        FROM attendance_filtered
        GROUP BY course_slug
        ORDER BY SUM(watch_time) DESC
        LIMIT 10
    ),

    top_course_monthly AS (
        SELECT 
            course_slug,
            watch_month,
            SUM(watch_time) AS total_watch_time,
            COUNT(DISTINCT student_id) AS unique_students
        FROM attendance_filtered
        WHERE course_slug IN (SELECT course_slug FROM top_courses)
        GROUP BY course_slug, watch_month
    ),

    lesson_watch_time AS (
        SELECT 
            course_slug,
            lesson_number,
            SUM(watch_time) AS total_watch_time
        FROM attendance_filtered
        WHERE course_slug IN (SELECT course_slug FROM top_courses)
        GROUP BY course_slug, lesson_number
    ),

    most_engaged_course AS (
        SELECT course_slug
        FROM attendance_filtered
        GROUP BY course_slug
        ORDER BY SUM(watch_time) DESC
        LIMIT 1
    ),

    lesson_engagement AS (
        SELECT 
            course_slug,
            lesson_number,
            COUNT(DISTINCT student_id) AS students_watched
        FROM attendance_filtered
        WHERE course_slug = (SELECT course_slug FROM most_engaged_course)
        GROUP BY course_slug, lesson_number
    ),

    passionate_students AS (
        SELECT
            student_id,
            course_slug,
            COUNT(DISTINCT lesson_number) AS lessons_watched
        FROM attendance_filtered
        GROUP BY student_id, course_slug
        HAVING COUNT(DISTINCT lesson_number) >= 8
    )

    SELECT * FROM basic_kpis;
    """
    conn = psycopg2.connect(**DB_CONFIG)
    df_kpis = pd.read_sql(query, conn)

    # Additional queries for breakdowns
    df_monthly = pd.read_sql("""
        SELECT * FROM (
            WITH attendance_filtered AS (
                SELECT 
                    value__student_id AS student_id,
                    value__course_slug AS course_slug,
                    value__lesson_number__bigint AS lesson_number,
                    value__watched__bigint AS watch_time,
                    DATE_TRUNC('month', value__create_at::timestamp) AS watch_month
                FROM firestore_api.firestore_attendance
                WHERE value__watched__bigint > 0 AND value__create_at >= '2025-01-01'
            )
            SELECT 
                course_slug,
                watch_month,
                SUM(watch_time) AS total_watch_time
            FROM attendance_filtered
            WHERE course_slug IN (
                SELECT course_slug FROM attendance_filtered 
                GROUP BY course_slug ORDER BY SUM(watch_time) DESC LIMIT 10
            )
            GROUP BY course_slug, watch_month
        ) x
    """, conn)

    df_lessons = pd.read_sql("""
        WITH attendance_filtered AS (
            SELECT 
                value__student_id AS student_id,
                value__course_slug AS course_slug,
                value__lesson_number__bigint AS lesson_number,
                value__watched__bigint AS watch_time
            FROM firestore_api.firestore_attendance
            WHERE value__watched__bigint > 0 AND value__create_at >= '2025-01-01'
        )
        SELECT 
            course_slug,
            lesson_number,
            SUM(watch_time) AS total_watch_time
        FROM attendance_filtered
        WHERE course_slug IN (
            SELECT course_slug FROM attendance_filtered 
            GROUP BY course_slug ORDER BY SUM(watch_time) DESC LIMIT 10
        )
        GROUP BY course_slug, lesson_number
    """, conn)

    df_passion = pd.read_sql("""
        WITH attendance_filtered AS (
            SELECT 
                value__student_id AS student_id,
                value__course_slug AS course_slug,
                value__lesson_number__bigint AS lesson_number
            FROM firestore_api.firestore_attendance
            WHERE value__watched__bigint > 0 AND value__create_at >= '2025-01-01'
        )
        SELECT
            student_id,
            course_slug,
            COUNT(DISTINCT lesson_number) AS lessons_watched
        FROM attendance_filtered
        GROUP BY student_id, course_slug
        HAVING COUNT(DISTINCT lesson_number) >= 8
    """, conn)

    conn.close()
    return df_kpis, df_monthly, df_lessons, df_passion

# Streamlit App
st.title("📊 Student Attendance Dashboard (2025+)")

try:
    df_kpis, df_monthly, df_lessons, df_passion = run_query()

    st.header("📌 Basic KPIs")
    st.metric("Most Watched Course", df_kpis['most_watched_course'].iloc[0])
    st.metric("Avg Watch Time per Student", round(df_kpis['avg_watch_time_per_student'].iloc[0], 2))
    st.metric("Avg Lessons per Student", round(df_kpis['avg_lessons_per_student'].iloc[0], 2))

    st.divider()

    st.subheader("📈 Monthly Watch Time for Top 10 Courses")
    selected_course = st.selectbox("Filter by Course", df_monthly['course_slug'].unique())
    fig = px.line(
        df_monthly[df_monthly['course_slug'] == selected_course],
        x="watch_month", y="total_watch_time", title=f"Watch Time Trend - {selected_course}"
    )
    st.plotly_chart(fig)

    st.subheader("📘 Lesson-by-Lesson Watch Time")
    fig2 = px.bar(
        df_lessons[df_lessons['course_slug'] == selected_course],
        x="lesson_number", y="total_watch_time",
        title=f"Lesson Engagement for {selected_course}"
    )
    st.plotly_chart(fig2)

    st.subheader("🎯 Passionate Students")
    st.dataframe(df_passion, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {e}")
