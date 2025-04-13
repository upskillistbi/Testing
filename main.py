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

def run_query10(query, start_date, end_date):
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

def run_query1(query, start_date, end_date):
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

def run_query2(query, start_date, end_date):
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

def run_query3(query, start_date, end_date):
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

def run_query4(query, start_date, end_date):
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

def run_query5(query, start_date, end_date):
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

def run_query6(query, start_date, end_date):
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


def run_query7(query, start_date, end_date):
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

def run_query8(query, start_date, end_date):
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

def run_query9(query, start_date, end_date):
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
        ELSE age_group
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
                ELSE age_group
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






# SQL Queries for Registration Metrics ( idm students with Registrations )
registration_queries = {
     "Monthly Registrations (General)": """
    SELECT 
        DATE_TRUNC('month', DSC.registered_on) AS registration_month,
        COUNT(DISTINCT DSC.registration_id) AS total_registrations,
        COUNT(DISTINCT DSC.student_id) AS total_unique_students
    FROM data_warehouse.dim_schedules DSC
    WHERE DSC.registered_on BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY registration_month
    ORDER BY registration_month;
""",
"Lead Registrations by Course Slug": """
    SELECT 
        COALESCE(reg.course_slug, 'Unknown') AS course_name,
        COUNT(DISTINCT reg.registration_id) AS total_registrations
    FROM (
        SELECT DISTINCT value__meta_data_lead_id AS lead_id
        FROM data_marts.combined_subscriptions
        WHERE value__meta_data_lead_id IS NOT NULL
    ) cc
    JOIN data_warehouse.dim_students stu ON cc.lead_id = stu.student_id
    JOIN data_warehouse.dim_schedules reg ON stu.student_id = reg.student_id
    WHERE reg.registered_on BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY reg.course_slug
    ORDER BY total_registrations DESC
    LIMIT 10;
"""
,

    "Registrations by Country": """
        SELECT DS.country, COUNT(DISTINCT DSC.registration_id) AS total_registrations
        FROM data_warehouse.dim_students DS
        JOIN data_warehouse.dim_schedules DSC ON DS.student_id = DSC.student_id
        WHERE DSC.registered_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DS.country
        ORDER BY total_registrations DESC;
    """,

    "Registrations by UTM Source": """
        SELECT DS.latest_utm_source AS utm_source, COUNT(DISTINCT DSC.registration_id) AS total_registrations
        FROM data_warehouse.dim_students DS
        JOIN data_warehouse.dim_schedules DSC ON DS.student_id = DSC.student_id
        WHERE DSC.registered_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DS.latest_utm_source
        ORDER BY total_registrations DESC;
    """,

    "Registrations by Offer Type": """
        SELECT DS.offer_type, COUNT(DISTINCT DSC.registration_id) AS total_registrations
        FROM data_warehouse.dim_students DS
        JOIN data_warehouse.dim_schedules DSC ON DS.student_id = DSC.student_id
        WHERE DSC.registered_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DS.offer_type
        ORDER BY total_registrations DESC;
    """,

    "Registrations by Age Group": """
        SELECT DS.age_group, COUNT(DISTINCT DSC.registration_id) AS total_registrations
        FROM data_warehouse.dim_students DS
        JOIN data_warehouse.dim_schedules DSC ON DS.student_id = DSC.student_id
        WHERE DSC.registered_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DS.age_group
        ORDER BY total_registrations DESC;
    """,

    "Registrations by Gender": """
        SELECT DS.gender, COUNT(DISTINCT DSC.registration_id) AS total_registrations
        FROM data_warehouse.dim_students DS
        JOIN data_warehouse.dim_schedules DSC ON DS.student_id = DSC.student_id
        WHERE DSC.registered_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DS.gender
        ORDER BY total_registrations DESC;
    """,

    "Registrations by Course Slug": """
        SELECT DSC.course_slug, COUNT(DISTINCT DSC.registration_id) AS total_registrations
        FROM data_warehouse.dim_schedules DSC
        WHERE DSC.registered_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DSC.course_slug
        ORDER BY total_registrations DESC;
    """
}

# CC table with registrations
lead_funnel_queries = {
    "Total Lead Funnel Registrations": """
        SELECT 
            COUNT(DISTINCT reg.registration_id) AS total_registrations,
            COUNT(DISTINCT reg.student_id) AS total_unique_cc_students
        FROM (
            SELECT DISTINCT value__meta_data_lead_id AS lead_id
            FROM data_marts.combined_subscriptions
            WHERE value__meta_data_lead_id IS NOT NULL
        ) cc
        JOIN data_warehouse.dim_students stu ON cc.lead_id = stu.student_id
        JOIN data_warehouse.dim_schedules reg ON stu.student_id = reg.student_id
        WHERE reg.registered_on BETWEEN '{start_date}' AND '{end_date}';
    """,

    "Lead Registrations by Country": """
        SELECT 
            COALESCE(stu.country, 'Unknown') AS country,
            COUNT(DISTINCT reg.registration_id) AS total_registrations
        FROM (
            SELECT DISTINCT value__meta_data_lead_id AS lead_id
            FROM data_marts.combined_subscriptions
            WHERE value__meta_data_lead_id IS NOT NULL
        ) cc
        JOIN data_warehouse.dim_students stu ON cc.lead_id = stu.student_id
        JOIN data_warehouse.dim_schedules reg ON stu.student_id = reg.student_id
        WHERE reg.registered_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY stu.country
        ORDER BY total_registrations DESC;
    """,

    "Lead Registrations by Age Group": """
        SELECT 
            COALESCE(stu.age_group, 'Unknown') AS age_group,
            COUNT(DISTINCT reg.registration_id) AS total_registrations
        FROM (
            SELECT DISTINCT value__meta_data_lead_id AS lead_id
            FROM data_marts.combined_subscriptions
            WHERE value__meta_data_lead_id IS NOT NULL
        ) cc
        JOIN data_warehouse.dim_students stu ON cc.lead_id = stu.student_id
        JOIN data_warehouse.dim_schedules reg ON stu.student_id = reg.student_id
        WHERE reg.registered_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY stu.age_group
        ORDER BY total_registrations DESC;
    """,

    "Lead Registrations by UTM Source": """
        SELECT 
            COALESCE(stu.latest_utm_source, 'Unknown') AS utm_source,
            COUNT(DISTINCT reg.registration_id) AS total_registrations
        FROM (
            SELECT DISTINCT value__meta_data_lead_id AS lead_id
            FROM data_marts.combined_subscriptions
            WHERE value__meta_data_lead_id IS NOT NULL
        ) cc
        JOIN data_warehouse.dim_students stu ON cc.lead_id = stu.student_id
        JOIN data_warehouse.dim_schedules reg ON stu.student_id = reg.student_id
        WHERE reg.registered_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY stu.latest_utm_source
        ORDER BY total_registrations DESC;
    """,

    "Lead Registrations by Offer Type": """
        SELECT 
            COALESCE(stu.offer_type, 'Unknown') AS offer_type,
            COUNT(DISTINCT reg.registration_id) AS total_registrations
        FROM (
            SELECT DISTINCT value__meta_data_lead_id AS lead_id
            FROM data_marts.combined_subscriptions
            WHERE value__meta_data_lead_id IS NOT NULL
        ) cc
        JOIN data_warehouse.dim_students stu ON cc.lead_id = stu.student_id
        JOIN data_warehouse.dim_schedules reg ON stu.student_id = reg.student_id
        WHERE reg.registered_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY stu.offer_type
        ORDER BY total_registrations DESC;
    """,

    "Lead Registrations by Course Slug": """
        SELECT 
            COALESCE(reg.course_slug, 'Unknown') AS course_name,
            COUNT(DISTINCT reg.registration_id) AS total_registrations
        FROM (
            SELECT DISTINCT value__meta_data_lead_id AS lead_id
            FROM data_marts.combined_subscriptions
            WHERE value__meta_data_lead_id IS NOT NULL
        ) cc
        JOIN data_warehouse.dim_students stu ON cc.lead_id = stu.student_id
        JOIN data_warehouse.dim_schedules reg ON stu.student_id = reg.student_id
        WHERE reg.registered_on BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY reg.course_slug
        ORDER BY total_registrations DESC
        LIMIT 10;
    """
}

attendance_leads_queries = {
    "Attendance Leads by Country": """
        SELECT 
            COALESCE(DS.country, 'Unknown') AS country,
            COUNT(DISTINCT FA.value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
        JOIN data_warehouse.dim_students DS ON DSC.student_id = DS.student_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(DS.country, 'Unknown')
        ORDER BY total_students_attended DESC;
    """,

    "Attendance Leads by Age Group": """
        SELECT 
            COALESCE(DS.age_group, 'Unknown') AS age_group,
            COUNT(DISTINCT FA.value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
        JOIN data_warehouse.dim_students DS ON DSC.student_id = DS.student_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(DS.age_group, 'Unknown')
        ORDER BY total_students_attended DESC;
    """,

    "Attendance Leads by UTM Source": """
        SELECT 
            COALESCE(DS.shaw_source, 'Unknown') AS utm_source,
            COUNT(DISTINCT FA.value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
        JOIN data_warehouse.dim_students DS ON DSC.student_id = DS.student_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(DS.shaw_source, 'Unknown')
        ORDER BY total_students_attended DESC;
    """,

    "Attendance Leads by Offer Type": """
        SELECT 
            COALESCE(DS.offer_type, 'Unknown') AS offer_type,
            COUNT(DISTINCT FA.value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
        JOIN data_warehouse.dim_students DS ON DSC.student_id = DS.student_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(DS.offer_type, 'Unknown')
        ORDER BY total_students_attended DESC;
    """,

    "Attendance Leads by Course Slug": """
        SELECT 
            COALESCE(DSC.course_slug, 'Unknown') AS course_slug,
            COUNT(DISTINCT FA.value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(DSC.course_slug, 'Unknown')
        ORDER BY total_students_attended DESC;
    """,

    "Attendance Leads by Month": """
        SELECT 
            DATE_TRUNC('month', DSC.first_lesson_start_time) AS registration_month,
            COUNT(DISTINCT FA.value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
        WHERE FA.value__watched__bigint > 0
        AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DATE_TRUNC('month', DSC.first_lesson_start_time)
        ORDER BY registration_month;
    """
}

attendance_cc_queries = {
    "Attendance CC by Country": """
        SELECT 
            COALESCE(DS.country, 'Unknown') AS country,
            COUNT(DISTINCT FA.value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
        JOIN data_marts.combined_subscriptions CS ON DSC.student_id = CS.value__meta_data_lead_id
        LEFT JOIN data_warehouse.dim_students DS ON DSC.student_id = DS.student_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(DS.country, 'Unknown')
        ORDER BY total_students_attended DESC;
    """,

    "Attendance CC by Age Group": """
        SELECT 
            COALESCE(DS.age_group, 'Unknown') AS age_group,
            COUNT(DISTINCT FA.value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
        JOIN data_marts.combined_subscriptions CS ON DSC.student_id = CS.value__meta_data_lead_id
        LEFT JOIN data_warehouse.dim_students DS ON DSC.student_id = DS.student_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(DS.age_group, 'Unknown')
        ORDER BY total_students_attended DESC;
    """,

    "Attendance CC by UTM Source": """
        SELECT 
            COALESCE(DS.latest_utm_source, 'Unknown') AS utm_source,
            COUNT(DISTINCT FA.value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
        JOIN data_marts.combined_subscriptions CS ON DSC.student_id = CS.value__meta_data_lead_id
        LEFT JOIN data_warehouse.dim_students DS ON DSC.student_id = DS.student_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(DS.latest_utm_source, 'Unknown')
        ORDER BY total_students_attended DESC;
    """,

    "Attendance CC by Offer Type": """
        SELECT 
            COALESCE(DS.offer_type, 'Unknown') AS offer_type,
            COUNT(DISTINCT FA.value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
        JOIN data_marts.combined_subscriptions CS ON DSC.student_id = CS.value__meta_data_lead_id
        LEFT JOIN data_warehouse.dim_students DS ON DSC.student_id = DS.student_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(DS.offer_type, 'Unknown')
        ORDER BY total_students_attended DESC;
    """,

    "Attendance CC by Course Slug": """
        SELECT 
            COALESCE(DSC.course_slug, 'Unknown') AS course_slug,
            COUNT(DISTINCT FA.value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
        JOIN data_marts.combined_subscriptions CS ON DSC.student_id = CS.value__meta_data_lead_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COALESCE(DSC.course_slug, 'Unknown')
        ORDER BY total_students_attended DESC;
    """,

    "Attendance CC by Month": """
        SELECT 
            DATE_TRUNC('month', DSC.first_lesson_start_time) AS registration_month,
            COUNT(DISTINCT FA.value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
        JOIN data_marts.combined_subscriptions CS ON DSC.student_id = CS.value__meta_data_lead_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DATE_TRUNC('month', DSC.first_lesson_start_time)
        ORDER BY registration_month;
    """
}


lesson_leads_queries = {
    "Total Students Attended (Leads)": """
        SELECT 
            COUNT(DISTINCT value__student_id) AS total_students_attended
        FROM firestore_api.firestore_attendance
        WHERE value__watched__bigint > 0
          AND value__create_at BETWEEN '{start_date}' AND '{end_date}';
    """,

    "Lesson-wise Attendance Per Course (Leads)": """
        SELECT 
            DSC.course_slug,
            FA.value__lesson_number__bigint AS lesson_number,
            COUNT(DISTINCT FA.value__student_id) AS students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC 
            ON FA.value__registrations_id = DSC.registration_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DSC.course_slug, FA.value__lesson_number__bigint
        ORDER BY DSC.course_slug, lesson_number;
    """,

    "Most Watched Lesson Per Course (Leads)": """
        WITH lesson_counts AS (
            SELECT 
                DSC.course_slug,
                FA.value__lesson_number__bigint AS lesson_number,
                COUNT(DISTINCT FA.value__student_id) AS students_attended
            FROM firestore_api.firestore_attendance FA
            JOIN data_warehouse.dim_schedules DSC 
                ON FA.value__registrations_id = DSC.registration_id
            WHERE FA.value__watched__bigint > 0
              AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY DSC.course_slug, FA.value__lesson_number__bigint
        )
        SELECT *
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY course_slug ORDER BY students_attended DESC) AS rn
            FROM lesson_counts
        ) sub
        WHERE rn = 1;
    """,

    "Average Watch Time Per Lesson Per Course (Leads)": """
        SELECT 
            DSC.course_slug,
            FA.value__lesson_number__bigint AS lesson_number,
            ROUND(AVG(FA.value__watched__bigint) / 60.0, 2) AS avg_watch_time_minutes
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC 
            ON FA.value__registrations_id = DSC.registration_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DSC.course_slug, FA.value__lesson_number__bigint
        ORDER BY DSC.course_slug, lesson_number;
    """,

    "Lesson Retention Per Course (Leads)": """
        WITH lesson_summary AS (
            SELECT 
                DSC.course_slug,
                FA.value__lesson_number__bigint AS lesson_number,
                COUNT(DISTINCT FA.value__student_id) AS students_attended
            FROM firestore_api.firestore_attendance FA
            JOIN data_warehouse.dim_schedules DSC 
                ON FA.value__registrations_id = DSC.registration_id
            WHERE FA.value__watched__bigint > 0
              AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY DSC.course_slug, FA.value__lesson_number__bigint
        )
        SELECT 
            course_slug,
            lesson_number,
            students_attended,
            LAG(students_attended) OVER (PARTITION BY course_slug ORDER BY lesson_number) AS previous_students_attended,
            CASE 
                WHEN LAG(students_attended) OVER (PARTITION BY course_slug ORDER BY lesson_number) IS NULL THEN NULL
                WHEN LAG(students_attended) OVER (PARTITION BY course_slug ORDER BY lesson_number) = 0 THEN NULL
                ELSE ROUND(100.0 * (students_attended::decimal / LAG(students_attended) OVER (PARTITION BY course_slug ORDER BY lesson_number)), 2)
            END AS retention_percentage
        FROM lesson_summary
        ORDER BY course_slug, lesson_number;
    """
}
lesson_cc_queries = {
    "Lesson-wise Attendance Per Course (CC)": """
        SELECT 
            DSC.course_slug,
            FA.value__lesson_number__bigint AS lesson_number,
            CASE WHEN CS.value__customer_id IS NOT NULL THEN 'CC User' ELSE 'Non-CC User' END AS user_type,
            COUNT(DISTINCT FA.value__student_id) AS students_attended
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC 
            ON FA.value__registrations_id = DSC.registration_id
        LEFT JOIN data_marts.combined_subscriptions CS 
            ON DSC.student_id = CS.value__meta_data_lead_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DSC.course_slug, FA.value__lesson_number__bigint, user_type
        ORDER BY DSC.course_slug, lesson_number, user_type;
    """,

    "Most Watched Lesson Per Course (CC)": """
        WITH lesson_counts AS (
            SELECT 
                DSC.course_slug,
                FA.value__lesson_number__bigint AS lesson_number,
                CASE WHEN CS.value__customer_id IS NOT NULL THEN 'CC User' ELSE 'Non-CC User' END AS user_type,
                COUNT(DISTINCT FA.value__student_id) AS students_attended
            FROM firestore_api.firestore_attendance FA
            JOIN data_warehouse.dim_schedules DSC 
                ON FA.value__registrations_id = DSC.registration_id
            LEFT JOIN data_marts.combined_subscriptions CS 
                ON DSC.student_id = CS.value__meta_data_lead_id
            WHERE FA.value__watched__bigint > 0
              AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY DSC.course_slug, FA.value__lesson_number__bigint, user_type
        )
        SELECT *
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY course_slug, user_type ORDER BY students_attended DESC) AS rn
            FROM lesson_counts
        ) sub
        WHERE rn = 1;
    """,

    "Average Watch Time Per Lesson Per Course (CC)": """
        SELECT 
            DSC.course_slug,
            FA.value__lesson_number__bigint AS lesson_number,
            CASE WHEN CS.value__customer_id IS NOT NULL THEN 'CC User' ELSE 'Non-CC User' END AS user_type,
            ROUND(AVG(FA.value__watched__bigint) / 60.0, 2) AS avg_watch_time_minutes
        FROM firestore_api.firestore_attendance FA
        JOIN data_warehouse.dim_schedules DSC 
            ON FA.value__registrations_id = DSC.registration_id
        LEFT JOIN data_marts.combined_subscriptions CS 
            ON DSC.student_id = CS.value__meta_data_lead_id
        WHERE FA.value__watched__bigint > 0
          AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DSC.course_slug, FA.value__lesson_number__bigint, user_type
        ORDER BY DSC.course_slug, lesson_number, user_type;
    """,

    "Lesson Retention Per Course (CC)": """
        WITH lesson_summary AS (
            SELECT 
                DSC.course_slug,
                FA.value__lesson_number__bigint AS lesson_number,
                CASE WHEN CS.value__customer_id IS NOT NULL THEN 'CC User' ELSE 'Non-CC User' END AS user_type,
                COUNT(DISTINCT FA.value__student_id) AS students_attended
            FROM firestore_api.firestore_attendance FA
            JOIN data_warehouse.dim_schedules DSC 
                ON FA.value__registrations_id = DSC.registration_id
            LEFT JOIN data_marts.combined_subscriptions CS 
                ON DSC.student_id = CS.value__meta_data_lead_id
            WHERE FA.value__watched__bigint > 0
              AND FA.value__create_at BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY DSC.course_slug, FA.value__lesson_number__bigint, user_type
        )
        SELECT 
            course_slug,
            lesson_number,
            user_type,
            students_attended,
            LAG(students_attended) OVER (PARTITION BY course_slug, user_type ORDER BY lesson_number) AS previous_students_attended,
            CASE 
                WHEN LAG(students_attended) OVER (PARTITION BY course_slug, user_type ORDER BY lesson_number) IS NULL THEN NULL
                WHEN LAG(students_attended) OVER (PARTITION BY course_slug, user_type ORDER BY lesson_number) = 0 THEN NULL
                ELSE ROUND(100.0 * (students_attended::decimal / LAG(students_attended) OVER (PARTITION BY course_slug, user_type ORDER BY lesson_number)), 2)
            END AS retention_percentage
        FROM lesson_summary
        ORDER BY course_slug, lesson_number, user_type;
    """
}

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

}



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
    "Rev1 Revenue": """SELECT SUM(converted_amount) AS rev1_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 AND plan_id IS NOT NULL;""",
    "Rev2 Revenue": """SELECT SUM(converted_amount) AS rev2_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 AND plan_id IS NULL AND description ILIKE '%lifetime%';""",
    "Rev3 Revenue": """SELECT SUM(converted_amount) AS rev3_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 AND plan_id IS NULL AND description NOT ILIKE '%lifetime%';""",
    "Partner Revenue": """SELECT SUM(converted_amount) AS partner_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 AND student_id IS NULL;""",
    "Reactivation Revenue": """SELECT SUM(converted_amount) AS reactivation_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 AND reactivated_on IS NOT NULL;""",
    # Time Trends
    "Monthly Revenue Trend": """SELECT DATE_TRUNC('month', payment_date) AS month, SUM(converted_amount) AS total_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 GROUP BY month ORDER BY month;""",
    # Demographics
    "Revenue by Country": """SELECT ds.country, SUM(ct.converted_amount) AS total_revenue FROM data_marts.combined_transactions ct JOIN data_warehouse.dim_students ds ON ct.student_id = ds.student_id WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}' AND ct.converted_amount > 0 AND ct.value__refunded_txn_id IS NULL GROUP BY ds.country ORDER BY total_revenue DESC;""",
    "Revenue by Gender": """SELECT ds.gender, SUM(ct.converted_amount) AS total_revenue FROM data_marts.combined_transactions ct JOIN data_warehouse.dim_students ds ON ct.student_id = ds.student_id WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}' AND ct.converted_amount > 0 AND ct.value__refunded_txn_id IS NULL GROUP BY ds.gender ORDER BY total_revenue DESC;""",
    "Revenue by Gateway": """SELECT gateway, SUM(converted_amount) AS total_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 GROUP BY gateway ORDER BY total_revenue DESC;""",
    "Revenue by Brand": """SELECT brand, SUM(converted_amount) AS total_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 GROUP BY brand ORDER BY total_revenue DESC;""",
    "Revenue by Currency": """SELECT currency, SUM(converted_amount) AS total_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 GROUP BY currency ORDER BY total_revenue DESC;""",
  ##  "Revenue by UTM Source": """SELECT cs.value__utm_source AS utm_source, SUM(ct.converted_amount) AS total_revenue FROM data_marts.combined_transactions ct JOIN data_marts.combined_subscriptions cs ON ct.subscription_id = cs.id WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}' AND ct.converted_amount > 0 AND ct.value__refunded_txn_id IS NULL GROUP BY cs.value__utm_source ORDER BY total_revenue DESC;""",
    "Revenue by UTM Source": """
    SELECT ds.latest_utm_source AS utm_source,
           SUM(ct.converted_amount) AS total_revenue
    FROM data_marts.combined_transactions ct
    JOIN data_warehouse.dim_students ds ON ct.student_id = ds.student_id
    WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}'
      AND ct.converted_amount > 0
      AND ct.value__refunded_txn_id IS NULL
    GROUP BY ds.latest_utm_source
    ORDER BY total_revenue DESC;
""",
    # Buyer Types
    "Revenue from First-Time Buyers": """SELECT SUM(ct.converted_amount) AS first_time_buyer_revenue FROM data_marts.combined_transactions ct WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}' AND ct.converted_amount > 0 AND ct.value__refunded_txn_id IS NULL AND ct.student_id NOT IN (SELECT DISTINCT student_id FROM data_marts.combined_transactions WHERE payment_date < '{start_date}' AND converted_amount > 0 AND student_id IS NOT NULL);""",
    "Revenue from Returning Buyers": """SELECT SUM(ct.converted_amount) AS returning_buyer_revenue FROM data_marts.combined_transactions ct WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}' AND ct.converted_amount > 0 AND ct.value__refunded_txn_id IS NULL AND ct.student_id IN (SELECT DISTINCT student_id FROM data_marts.combined_transactions WHERE payment_date < '{start_date}' AND converted_amount > 0 AND student_id IS NOT NULL);""",
    "Revenue by Registration Cohort": """SELECT DATE_TRUNC('month', ds.created_date) AS registration_month, SUM(ct.converted_amount) AS total_revenue FROM data_marts.combined_transactions ct JOIN data_warehouse.dim_students ds ON ct.student_id = ds.student_id WHERE ct.payment_date BETWEEN '{start_date}' AND '{end_date}' AND ct.converted_amount > 0 AND ct.value__refunded_txn_id IS NULL GROUP BY registration_month ORDER BY registration_month;""",
    "Top Spenders": """SELECT student_id, SUM(converted_amount) AS total_revenue FROM data_marts.combined_transactions WHERE payment_date BETWEEN '{start_date}' AND '{end_date}' AND converted_amount > 0 AND student_id IS NOT NULL GROUP BY student_id ORDER BY total_revenue DESC LIMIT 10;"""
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
    tab1, tab2, tab3, tab4,tab5,tab6,tab7,tab8,tab9 = st.tabs([
        "📥 Total Leads",
        "🎯 Qualified Leads",
        "🔁 Infographics",
        "❌ Cancelled Leads",
        "📝 Registrations",
        "📥 Attendance",
        "💡Lesson",
        "🚀Reactivated",
        "✅Revenue "
    ])

    with tab1:
            st.subheader("📊 Breakdown of Total Leads")
            st.metric("📥 Total Leads (All Sources)", f"{total:,}")
        ##   by_utm_medium=run_query(SQL["total_leads_utm_medium"] ,start_date, end_date)
            by_country = run_query10(SQL["total_by_country"], start_date, end_date)
            by_utm = run_query10(SQL["total_by_utm"], start_date, end_date)
            by_partner = run_query10(SQL["total_by_partner"], start_date, end_date)
            total_leads_course_picked= run_query10(SQL["total_leads_course_picked"], start_date, end_date)
        ## total_leads_profile_partner= run_query10(SQL["total_leads_profile_partner"], start_date, end_date)
            total_leads_offer_type= run_query10(SQL["total_leads_offer_type"], start_date, end_date)
            total_leads_age_group= run_query10(SQL["total_leads_age_group"], start_date, end_date)

        
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
            q_by_country = run_query2(SQL["total_by_country"].replace("total_leads", "qualified_leads")
                                    .replace("student_id", "cs.id")
                                    .replace("dim_students", "dim_students ds JOIN data_marts.combined_subscriptions cs ON cs.value__meta_data_lead_id = ds.student_id"), 
                                    start_date, end_date)

            q_by_utm = run_query2(SQL["total_by_utm"].replace("total_leads", "qualified_leads")
                                .replace("student_id", "cs.id")
                                .replace("dim_students", "dim_students ds JOIN data_marts.combined_subscriptions cs ON cs.value__meta_data_lead_id = ds.student_id"), 
                                start_date, end_date)

            q_by_partner = run_query2(SQL["total_by_partner"].replace("total_leads", "qualified_leads")
                                    .replace("student_id", "cs.id")
                                    .replace("dim_students", "dim_students ds JOIN data_marts.combined_subscriptions cs ON cs.value__meta_data_lead_id = ds.student_id"), 
                                    start_date, end_date)

            q_course = run_query2(SQL["total_leads_course_picked"].replace("total_leads", "qualified_leads")
                                .replace("dim_students", "dim_students ds JOIN data_marts.combined_subscriptions cs ON cs.value__meta_data_lead_id = ds.student_id"), 
                                start_date, end_date)

            q_offer = run_query2(SQL["total_leads_offer_type"].replace("total_leads", "qualified_leads")
                                .replace("dim_students", "dim_students ds JOIN data_marts.combined_subscriptions cs ON cs.value__meta_data_lead_id = ds.student_id"), 
                                start_date, end_date)

            q_age = run_query2(SQL["total_leads_age_group"].replace("total_leads", "qualified_leads")
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
            leads_df = run_query3(sql_mom["leads_mom"], start_date, end_date)
            qualified_df = run_query3(sql_mom["qualified_mom"], start_date, end_date)
            cancelled_df = run_query3(sql_mom["cancelled_mom"], start_date, end_date)
            conversion_df = run_query3(sql_mom["conversion_mom"], start_date, end_date)
            utm_df = run_query3(sql_mom["utm_kpis"], start_date, end_date)

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

    with tab5:
        st.subheader("📝 Registrations Overview")

        # --- General Registrations Queries ---
        reg_country = run_query4(registration_queries["Registrations by Country"], start_date, end_date)
        reg_utm = run_query4(registration_queries["Registrations by UTM Source"], start_date, end_date)
        reg_offer = run_query4(registration_queries["Registrations by Offer Type"], start_date, end_date)
        reg_age = run_query4(registration_queries["Registrations by Age Group"], start_date, end_date)
        reg_gender = run_query4(registration_queries["Registrations by Gender"], start_date, end_date)
        reg_course = run_query4(registration_queries["Registrations by Course Slug"], start_date, end_date)
        reg_monthly = run_query4(registration_queries["Monthly Registrations (General)"], start_date, end_date)

        # --- Lead Funnel Registrations Queries ---
        lead_total = run_query4(lead_funnel_queries["Total Lead Funnel Registrations"], start_date, end_date)
        lead_country = run_query4(lead_funnel_queries["Lead Registrations by Country"], start_date, end_date)
        lead_age = run_query4(lead_funnel_queries["Lead Registrations by Age Group"], start_date, end_date)
        lead_utm = run_query4(lead_funnel_queries["Lead Registrations by UTM Source"], start_date, end_date)
        lead_offer = run_query4(lead_funnel_queries["Lead Registrations by Offer Type"], start_date, end_date)
        lead_course = run_query4(lead_funnel_queries["Lead Registrations by Course Slug"], start_date, end_date)

        # --- Reusable function for metric display ---
        def display_metric(title, df, xcol, ycol):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"### {title}")
                st.dataframe(df)
            with col2:
                if not df.empty:
                    fig = px.bar(df, x=xcol, y=ycol, text=ycol, title=title)
                    st.plotly_chart(fig, use_container_width=True)

        # ============================
        # Section 1: General Registrations
        # ============================
        st.markdown("## 📋 General Registrations Metrics")
        
        total_registrations = reg_course["total_registrations"].sum() if not reg_course.empty else 0
        st.metric("Total Registrations", f"{total_registrations:,}")

        st.markdown("### 🔍 Top Insights (General Registrations)")
        if not reg_country.empty:
            st.markdown(f"🌍 **Top Country**: `{reg_country.iloc[0]['country']}` with `{reg_country.iloc[0]['total_registrations']:,}` registrations")
        if not reg_utm.empty:
            st.markdown(f"🔗 **Top UTM Source**: `{reg_utm.iloc[0]['utm_source']}` with `{reg_utm.iloc[0]['total_registrations']:,}` registrations")
        if not reg_offer.empty:
            st.markdown(f"🏷️ **Top Offer Type**: `{reg_offer.iloc[0]['offer_type']}` with `{reg_offer.iloc[0]['total_registrations']:,}` registrations")
        if not reg_age.empty:
            st.markdown(f"👥 **Top Age Group**: `{reg_age.iloc[0]['age_group']}` with `{reg_age.iloc[0]['total_registrations']:,}` registrations")
        if not reg_gender.empty:
            st.markdown(f"🧑‍🤝‍🧑 **Top Gender**: `{reg_gender.iloc[0]['gender']}` with `{reg_gender.iloc[0]['total_registrations']:,}` registrations")
        if not reg_course.empty:
            st.markdown(f"📘 **Top Course**: `{reg_course.iloc[0]['course_slug']}` with `{reg_course.iloc[0]['total_registrations']:,}` registrations")

        # --- Visualizations ---
        display_metric("🌍 Registrations by Country", reg_country, "country", "total_registrations")
        display_metric("🔗 Registrations by UTM Source", reg_utm, "utm_source", "total_registrations")
        display_metric("🏷️ Registrations by Offer Type", reg_offer, "offer_type", "total_registrations")
        display_metric("👥 Registrations by Age Group", reg_age, "age_group", "total_registrations")
        display_metric("🧑‍🤝‍🧑 Registrations by Gender", reg_gender, "gender", "total_registrations")
        display_metric("📘 Registrations by Course Slug", reg_course, "course_slug", "total_registrations")

        # --- Monthly Trend ---
        st.markdown("### 📈 Monthly Registration Trend")
        if not reg_monthly.empty:
            st.dataframe(reg_monthly)
            fig_monthly = px.line(reg_monthly, x="registration_month", y="total_registrations", markers=True, title="Monthly Registrations")
            st.plotly_chart(fig_monthly, use_container_width=True)

        st.markdown("---")

        # ============================
        # Section 2: Lead Funnel Registrations
        # ============================
        st.markdown("## 🧩 Lead Funnel Registrations (CC Leads)")

        if not lead_total.empty:
            st.metric("Total Lead Funnel Registrations", f"{lead_total.iloc[0]['total_registrations']:,}")
            st.metric("Total Unique CC Students", f"{lead_total.iloc[0]['total_unique_cc_students']:,}")

        st.markdown("### 🔍 Top Insights (Lead Funnel Registrations)")
        if not lead_country.empty:
            st.markdown(f"🌍 **Top Country**: `{lead_country.iloc[0]['country']}` with `{lead_country.iloc[0]['total_registrations']:,}` registrations")
        if not lead_utm.empty:
            st.markdown(f"🔗 **Top UTM Source**: `{lead_utm.iloc[0]['utm_source']}` with `{lead_utm.iloc[0]['total_registrations']:,}` registrations")
        if not lead_offer.empty:
            st.markdown(f"🏷️ **Top Offer Type**: `{lead_offer.iloc[0]['offer_type']}` with `{lead_offer.iloc[0]['total_registrations']:,}` registrations")
        if not lead_age.empty:
            st.markdown(f"👥 **Top Age Group**: `{lead_age.iloc[0]['age_group']}` with `{lead_age.iloc[0]['total_registrations']:,}` registrations")
        if not lead_course.empty:
            st.markdown(f"📘 **Top Course**: `{lead_course.iloc[0]['course_name']}` with `{lead_course.iloc[0]['total_registrations']:,}` registrations")

        # --- Visualizations ---
        display_metric("🌍 Lead Registrations by Country", lead_country, "country", "total_registrations")
        display_metric("🔗 Lead Registrations by UTM Source", lead_utm, "utm_source", "total_registrations")
        display_metric("🏷️ Lead Registrations by Offer Type", lead_offer, "offer_type", "total_registrations")
        display_metric("👥 Lead Registrations by Age Group", lead_age, "age_group", "total_registrations")
        display_metric("📘 Lead Registrations by Course Slug", lead_course, "course_name", "total_registrations")

    
    with tab6:
        st.subheader("🎥 Attendance Analysis: Leads & CC View (Side by Side)")

        # Define both views
        views = [
            ("Leads View (dim_students)", attendance_leads_queries, "Leads"),
            ("CC View (combined_subscriptions)", attendance_cc_queries, "CC")
        ]

        for view_title, selected_queries, view_label in views:

            st.markdown(f"## 📊 {view_title}")

            # --- Run queries for selected view ---
            country_df = run_query5(selected_queries[f"Attendance {view_label} by Country"], start_date, end_date)
            age_df = run_query5(selected_queries[f"Attendance {view_label} by Age Group"], start_date, end_date)
            utm_df = run_query5(selected_queries[f"Attendance {view_label} by UTM Source"], start_date, end_date)
            offer_df = run_query5(selected_queries[f"Attendance {view_label} by Offer Type"], start_date, end_date)
            course_df = run_query5(selected_queries[f"Attendance {view_label} by Course Slug"], start_date, end_date)
            month_df = run_query5(selected_queries[f"Attendance {view_label} by Month"], start_date, end_date)

            # --- Top Metrics ---
            total_attendance = course_df["total_students_attended"].sum() if not course_df.empty else 0
            st.metric(f"🧑‍🎓 Total Students Attended ({view_label} View)", f"{total_attendance:,}")

            # --- Top Insights ---
            st.markdown(f"### 🔍 Top Insights ({view_label} View)")
            if not country_df.empty:
                st.markdown(f"🌍 **Top Country:** `{country_df.iloc[0]['country']}` with `{country_df.iloc[0]['total_students_attended']:,}` students")
            if not age_df.empty:
                st.markdown(f"👥 **Top Age Group:** `{age_df.iloc[0]['age_group']}` with `{age_df.iloc[0]['total_students_attended']:,}` students")
            if not utm_df.empty:
                st.markdown(f"🔗 **Top UTM Source:** `{utm_df.iloc[0]['utm_source']}` with `{utm_df.iloc[0]['total_students_attended']:,}` students")
            if not offer_df.empty:
                st.markdown(f"🏷️ **Top Offer Type:** `{offer_df.iloc[0]['offer_type']}` with `{offer_df.iloc[0]['total_students_attended']:,}` students")
            if not course_df.empty:
                st.markdown(f"📘 **Top Course:** `{course_df.iloc[0]['course_slug']}` with `{course_df.iloc[0]['total_students_attended']:,}` students")

            st.markdown("---")

            # --- Reusable chart + table display ---
            def display_chart_and_table(title, df, x_column, y_column):
                if not df.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"### {title}")
                        st.dataframe(df)
                    with col2:
                        fig = px.bar(df, x=x_column, y=y_column, text=y_column, title=title)
                        st.plotly_chart(fig, use_container_width=True)

            # --- Section: Breakdown Visualizations ---
            st.markdown(f"## 📊 Breakdown Visualizations ({view_label} View)")

            display_chart_and_table(f"🌍 Attendance by Country ({view_label})", country_df, "country", "total_students_attended")
            display_chart_and_table(f"👥 Attendance by Age Group ({view_label})", age_df, "age_group", "total_students_attended")
            display_chart_and_table(f"🔗 Attendance by UTM Source ({view_label})", utm_df, "utm_source", "total_students_attended")
            display_chart_and_table(f"🏷️ Attendance by Offer Type ({view_label})", offer_df, "offer_type", "total_students_attended")
            display_chart_and_table(f"📘 Attendance by Course Slug ({view_label})", course_df, "course_slug", "total_students_attended")

            # --- Monthly trend ---
            st.markdown(f"## 🗓️ Monthly Attendance Trend ({view_label} View)")
            if not month_df.empty:
                st.dataframe(month_df)
                fig_month = px.line(month_df, x="registration_month", y="total_students_attended", markers=True,
                                    title=f"Monthly Attendance Trend ({view_label} View)")
                st.plotly_chart(fig_month, use_container_width=True)

            # --- Optional: CSV export ---
            st.markdown(f"## 📥 Download Data ({view_label} View)")

            csv = course_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"Download Attendance by Course ({view_label}) as CSV",
                data=csv,
                file_name=f'attendance_by_course_{view_label.lower()}.csv',
                mime='text/csv',
            )

            st.markdown("---")


    with tab7:
        st.title("🎓 Lesson-Level Attendance Analysis")

        # -------------------------------
        # Leads View (dim_students)
        # -------------------------------
        st.subheader("Leads View (dim_students)")

        for metric_name, query in lesson_leads_queries.items():
            st.markdown(f"### {metric_name}")
            df = run_query7(query, start_date, end_date)

            if not df.empty:
                # Table
                st.dataframe(df)

                # Insights
                if "Most Watched Lesson" in metric_name:
                    for idx, row in df.iterrows():
                        st.markdown(f"🔥 Most Watched Lesson for **{row['course_slug']}**: Lesson {int(row['lesson_number'])} with {int(row['students_attended'])} students")
                if "Retention" in metric_name:
                    dropoff_df = df.dropna(subset=['retention_percentage'])
                    if not dropoff_df.empty:
                        max_dropoff = dropoff_df.loc[dropoff_df['retention_percentage'].idxmin()]
                        st.markdown(f"📉 **Biggest Drop-off**: Course `{max_dropoff['course_slug']}`, Lesson `{int(max_dropoff['lesson_number'])}`, Retention `{max_dropoff['retention_percentage']}%`")

                # Chart (Optional for metrics with numeric columns)
                numeric_cols = [col for col in df.columns if df[col].dtype != 'object']
                if len(numeric_cols) >= 2:
                    x_col, y_col = numeric_cols[0], numeric_cols[1]
                    fig = px.bar(df, x=x_col, y=y_col, text=y_col, title=f"{metric_name} (Leads View)")
                    st.plotly_chart(fig, use_container_width=True)

                # CSV Export
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"Download {metric_name} as CSV (Leads View)",
                    data=csv,
                    file_name=f"{metric_name.replace(' ', '_').lower()}_leads.csv",
                    mime='text/csv',
                )

            else:
                st.info(f"No data available for {metric_name} in the selected date range.")

            st.markdown("---")


        # -------------------------------
        # CC View (combined_subscriptions)
        # -------------------------------
        st.subheader("CC View (combined_subscriptions)")

        for metric_name, query in lesson_cc_queries.items():
            st.markdown(f"### {metric_name}")
            df = run_query7(query, start_date, end_date)

            if not df.empty:
                # Table
                st.dataframe(df)

                # Insights
                if "Most Watched Lesson" in metric_name:
                    for idx, row in df.iterrows():
                        st.markdown(f"🔥 Most Watched Lesson for **{row['course_slug']}** ({row['user_type']}): Lesson {int(row['lesson_number'])} with {int(row['students_attended'])} students")
                if "Retention" in metric_name:
                    dropoff_df = df.dropna(subset=['retention_percentage'])
                    if not dropoff_df.empty:
                        max_dropoff = dropoff_df.loc[dropoff_df['retention_percentage'].idxmin()]
                        st.markdown(f"📉 **Biggest Drop-off**: Course `{max_dropoff['course_slug']}`, Lesson `{int(max_dropoff['lesson_number'])}`, User Type `{max_dropoff['user_type']}`, Retention `{max_dropoff['retention_percentage']}%`")

                # Chart (Optional for metrics with numeric columns)
                numeric_cols = [col for col in df.columns if df[col].dtype != 'object']
                if len(numeric_cols) >= 2:
                    x_col, y_col = numeric_cols[0], numeric_cols[1]
                    color_col = "user_type" if "user_type" in df.columns else None
                    fig = px.bar(df, x=x_col, y=y_col, color=color_col, text=y_col, title=f"{metric_name} (CC View)")
                    st.plotly_chart(fig, use_container_width=True)

                # CSV Export
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"Download {metric_name} as CSV (CC View)",
                    data=csv,
                    file_name=f"{metric_name.replace(' ', '_').lower()}_cc.csv",
                    mime='text/csv',
                )

            else:
                st.info(f"No data available for {metric_name} in the selected date range.")

            st.markdown("---")

    with tab8:
        st.title("♻️ Reactivations Analysis (Clean — Post Reactivation Only)")

                # Load data from your clean SQL dictionary
        st.info(f"Showing data for selected range: **{start_date} to {end_date}**")

        for metric_name, query in reactivation_queries_clean.items():
            st.markdown(f"### {metric_name}")
            df = run_query8(query, start_date, end_date)

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

    with tab9:
        st.header("📊 Revenue Tab Insights")

        # -- Top Summary Metrics --
        with st.spinner("Loading summary metrics..."):
            total_revenue = run_query(revenue_queries["Total Revenue"], start_date, end_date).iloc[0, 0]
            unique_buyers = run_query(revenue_queries["Unique Buyers"], start_date, end_date).iloc[0, 0]
            aov = run_query(revenue_queries["Average Order Value (AOV)"], start_date, end_date).iloc[0, 0]

            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total Revenue", f"{total_revenue:,.2f}")
            col2.metric("🧑‍🎓 Unique Buyers", f"{unique_buyers:,}")
            col3.metric("💳 AOV", f"{aov:,.2f}")

            st.markdown("---")

            # -- Helper Function --
            def display_chart_table(title, query_key, x_col=None, y_col=None, chart_type="bar"):
                with st.spinner(f"Loading {title}..."):
                    df = run_query(revenue_queries[query_key], start_date, end_date)
                    if not df.empty:
                        st.subheader(title)
                        st.dataframe(df)
                        if x_col and y_col:
                            if chart_type == "bar":
                                fig = px.bar(df, x=x_col, y=y_col, text=y_col, title=title)
                            else:
                                fig = px.line(df, x=x_col, y=y_col, markers=True, title=title)
                            st.plotly_chart(fig, use_container_width=True)
                        st.download_button(
                            label=f"Download {title} CSV",
                            data=df.to_csv(index=False).encode('utf-8'),
                            file_name=f"{title.lower().replace(' ', '_')}.csv",
                            mime="text/csv"
                        )
                        st.markdown("---")

            # -- Revenue Splits --
            rev1 = run_query(revenue_queries["Rev1 Revenue"], start_date, end_date).iloc[0, 0]
            rev2 = run_query(revenue_queries["Rev2 Revenue"], start_date, end_date).iloc[0, 0]
            rev3 = run_query(revenue_queries["Rev3 Revenue"], start_date, end_date).iloc[0, 0]
            rev_split_df = pd.DataFrame({"Type": ["Rev1", "Rev2", "Rev3"], "Revenue": [rev1, rev2, rev3]})
            st.subheader("Revenue Split: Rev1 / Rev2 / Rev3")
            st.dataframe(rev_split_df)
            fig_rev_split = px.pie(rev_split_df, names="Type", values="Revenue", title="Revenue Split")
            st.plotly_chart(fig_rev_split, use_container_width=True)
            st.markdown("---")

            # --- Rev1 / Rev2 / Rev3 Description-Level Breakdown ---
            st.subheader("🧩 Clean Revenue Breakdown by Rev1 / Rev2 / Rev3")

            # Custom Query for Clean Descriptions
            description_query = f"""
            SELECT
            CASE
                WHEN plan_id IS NOT NULL THEN 'Rev1'
                WHEN plan_id IS NULL AND description ILIKE '%lifetime%' THEN 'Rev2'
                WHEN plan_id IS NULL AND description NOT ILIKE '%lifetime%' THEN 'Rev3'
            END AS revenue_bucket,

            TRIM(
                REGEXP_REPLACE(
                SPLIT_PART(description, ':', 1),
                '.* - ',
                ''
                )
            ) AS clean_description,

            SUM(converted_amount) AS total_revenue,
            COUNT(*) AS transaction_count

            FROM data_marts.combined_transactions
            WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
            AND converted_amount > 0
            GROUP BY 1, 2
            ORDER BY revenue_bucket, total_revenue DESC;
            """

            # Run the query
            description_df = run_query(description_query, start_date, end_date)

            if not description_df.empty:
                st.dataframe(description_df)

                # Download Button
                st.download_button(
                    label="Download Description Breakdown CSV",
                    data=description_df.to_csv(index=False).encode('utf-8'),
                    file_name="description_breakdown.csv",
                    mime="text/csv"
                )

                # Pie Charts for Each Revenue Bucket
                for bucket in description_df['revenue_bucket'].unique():
                    bucket_data = description_df[description_df['revenue_bucket'] == bucket]
                    if not bucket_data.empty:
                        st.markdown(f"### {bucket} Revenue Distribution")
                        fig = px.pie(
                            bucket_data,
                            names='clean_description',
                            values='total_revenue',
                            title=f"{bucket} - Clean Description Revenue Split"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")
            else:
                st.warning("No data available for the selected period in description breakdown.")
            # -- Breakdown Charts and Tables --
            display_chart_table("Monthly Revenue Trend", "Monthly Revenue Trend", "month", "total_revenue", "line")
            display_chart_table("Revenue by Country", "Revenue by Country", "country", "total_revenue")
            display_chart_table("Revenue by Gender", "Revenue by Gender", "gender", "total_revenue")
            display_chart_table("Revenue by Gateway", "Revenue by Gateway", "gateway", "total_revenue")
            display_chart_table("Revenue by Brand", "Revenue by Brand", "brand", "total_revenue")
            display_chart_table("Revenue by Currency", "Revenue by Currency", "currency", "total_revenue")
            display_chart_table("Revenue by UTM Source", "Revenue by UTM Source", "utm_source", "total_revenue")
            display_chart_table("Revenue by Registration Cohort", "Revenue by Registration Cohort", "registration_month", "total_revenue", "line")
            display_chart_table("Top Spenders", "Top Spenders", "student_id", "total_revenue")



            st.success("✅ Revenue analysis complete!")

else:
    st.info("📅 Select a date range and click 'Run Analysis' to load data.")

    
