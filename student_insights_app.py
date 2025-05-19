import streamlit as st
import pandas as pd
import psycopg2

# --- Redshift Connection ---
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

# --- Streamlit Page Setup ---
st.set_page_config(page_title="🎯 Multi Student Lookup", layout="wide")
st.title("📘 Multi Student Deep Dive Dashboard")
st.markdown("Paste multiple `student_id`s (one per line) below:")

# --- Input Box ---
input_ids = st.text_area("Paste student IDs here (one per line):")

def format_ids(raw_text):
    ids = [x.strip() for x in raw_text.strip().split('\n') if x.strip()]
    return ids, ', '.join(f"'{x}'" for x in ids)

# --- Run Lookup ---
if st.button("🔍 Run Lookup") and input_ids:
    id_list, formatted_ids = format_ids(input_ids)

    if not id_list:
        st.warning("⚠️ Please enter valid student IDs.")
    else:
        st.success(f"🔎 Running for {len(id_list)} students...")

        # --- Student Info ---
        st.subheader("🧑 Student Info")
        student_info_query = f"""
            SELECT student_id,
                age_group,
                offer_type,
                country,
                created_date,
                profile__partner_identifier AS partner_identifier,
                coursepicked
            FROM data_warehouse.dim_students
            WHERE student_id IN ({formatted_ids});
        """
        df_info = run_query(student_info_query)
        st.dataframe(df_info, use_container_width=True)

        # --- Qualified CC Leads ---
        st.subheader("💳 Qualified Leads Presence")
        cc_check_query = f"""
            SELECT DISTINCT value__meta_data_lead_id AS student_id
            FROM data_marts.combined_subscriptions
            WHERE value__meta_data_lead_id IN ({formatted_ids});
        """
        df_cc = run_query(cc_check_query)
        df_info["is_qualified_lead"] = df_info["student_id"].isin(df_cc["student_id"])
        st.dataframe(df_info[["student_id", "is_qualified_lead"]], use_container_width=True)

        # --- Courses Picked in dim_students ---
        st.subheader("📚 Course Clicked Count")
        coursepicked_query = f"""
            SELECT student_id, COUNT(DISTINCT coursepicked) AS courses_clicked
            FROM data_warehouse.dim_students
            WHERE student_id IN ({formatted_ids})
            GROUP BY student_id;
        """
        df_coursepicked = run_query(coursepicked_query)
        st.dataframe(df_coursepicked, use_container_width=True)

        # --- Registrations ---
        st.subheader("📝 Course Registrations")
        reg_query = f"""
            SELECT  student_id, registration_id, course_slug, registered_on
            FROM data_warehouse.dim_schedules
            WHERE student_id IN ({formatted_ids})
            ORDER BY student_id, registered_on;
        """
        df_reg = run_query(reg_query)
        df_reg = df_reg.drop_duplicates(subset=["student_id", "registration_id", "course_slug","registered_on"])
        st.dataframe(df_reg, use_container_width=True)

        # --- Attendance ---
        st.subheader("🎥 Attendance Records (watched > 0 sec)")
        att_query = f"""
                        SELECT 
            fa.value__student_id AS student_id,
            fa.value__registrations_id AS registration_id,
            dsc.course_slug,
            fa.value__lesson_number__bigint AS lesson_number,
            fa.value__watched__bigint AS watched_secs
            FROM firestore_api.firestore_attendance fa
            JOIN data_warehouse.dim_schedules dsc 
            ON fa.value__registrations_id = dsc.registration_id
            WHERE fa.value__student_id IN ({formatted_ids}) AND fa.value__watched__bigint > 0;
        """
        df_att = run_query(att_query)
        st.dataframe(df_att, use_container_width=True)

        # --- Revenue ---
        st.subheader("💰 Revenue & Transaction Details")
        rev_query = f"""
            SELECT student_id, transaction_id, payment_date, converted_amount,
                   CASE
                       WHEN description ILIKE '%lifetime%' THEN 'Rev2'
                       WHEN description ILIKE '%course%' OR description ILIKE '%toolkit%' OR description ILIKE '%hard%' THEN 'Rev3'
                       WHEN plan_id IS NOT NULL THEN 'Rev1'
                       ELSE 'Other'
                   END AS revenue_type,
                   description
            FROM data_marts.combined_transactions
            WHERE student_id IN ({formatted_ids})
              AND converted_amount > 0
            ORDER BY student_id, payment_date;
        """
        df_rev = run_query(rev_query)
        st.dataframe(df_rev, use_container_width=True)
