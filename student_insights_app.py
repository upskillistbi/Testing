import streamlit as st
import pandas as pd
import psycopg2
import re
import plotly.express as px
# --- DB Connection ---
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

# --- Page Setup ---
st.set_page_config(page_title="📘 Student Lookup (ID + Email)", layout="wide")
st.title("🎯 Multi-Student Deep Dive Dashboard")
st.markdown("Paste a mix of **student IDs** and/or **emails** (one per line):")

# --- Input Area ---
user_input = st.text_area("Enter student IDs or Emails (one per line):")



def normalize_email(email):
    if '+' in email:
        local, domain = email.split('@')
        local = re.sub(r'\+.*', '', local)
        return f"{local}@{domain}"
    return email

def separate_ids_emails(raw_input):
    ids, emails = [], []
    for line in raw_input.strip().split('\n'):
        val = line.strip()
        if not val:
            continue
        if "@" in val:
            cleaned_email = normalize_email(val.lower())
            emails.append(cleaned_email)
        else:
            ids.append(val)
    return ids, emails, ', '.join(f"'{x}'" for x in ids), ', '.join(f"'{x}'" for x in emails)



# --- Run ---
if st.button("🔍 Run Lookup") and user_input:
    ids, emails, formatted_ids, formatted_emails = separate_ids_emails(user_input)

    if not ids and not emails:
        st.warning("⚠️ Please enter valid student IDs or emails.")
    else:
        st.success(f"🔎 Running for {len(ids)} IDs and {len(emails)} emails...")

        # --- Filter Clause ---
        filters = []
        if ids:
            filters.append(f"student_id IN ({formatted_ids})")
        if emails:
            filters.append(f"REGEXP_REPLACE(LOWER(email_address), '\\\\+[^@]*', '') IN ({formatted_emails})")

        where_clause = " OR ".join(filters)

        # --- 1. Student Info ---
        st.subheader("🧑 Student Info")
        query_info = f"""
            SELECT student_id, email_address AS email, age_group, offer_type, country,
                   profile__partner_identifier AS partner_identifier, created_date, coursepicked
            FROM data_warehouse.dim_students
            WHERE {where_clause};
        """
        df_info = run_query(query_info)
        # Replace formatted_resolved_ids if emails were given
        resolved_ids = df_info["student_id"].dropna().unique().tolist()
        formatted_resolved_ids = ', '.join(f"'{x}'" for x in resolved_ids)

        st.dataframe(df_info, use_container_width=True)

       
        # --- 2. Qualified CC Leads ---
        st.subheader("💳 Qualified Leads Presence")

        if resolved_ids:
            query_cc = f"""
                SELECT DISTINCT value__meta_data_lead_id AS student_id
                FROM data_marts.combined_subscriptions
                WHERE value__meta_data_lead_id IN ({formatted_resolved_ids});
            """
            df_cc = run_query(query_cc)
            df_info["is_qualified_lead"] = df_info["student_id"].isin(df_cc["student_id"])
        else:
            df_cc = pd.DataFrame(columns=["student_id"])
            df_info["is_qualified_lead"] = False

        st.dataframe(df_info[["student_id", "email", "is_qualified_lead"]], use_container_width=True)

        # --- 3. Courses Picked Count ---
        st.subheader("📚 Courses Picked Count")
        coursepicked_query = f"""
            SELECT student_id, coursepicked AS courses_clicked_on_leads_table
            FROM data_warehouse.dim_students
            WHERE {where_clause}
            GROUP BY student_id,coursepicked;
        """
        df_coursepicked = run_query(coursepicked_query)
        st.dataframe(df_coursepicked, use_container_width=True)

        
        # --- 4. Registrations ---
        st.subheader("📝 Course Registrations")

        if resolved_ids:
            reg_query = f"""
                SELECT DISTINCT student_id, registration_id, course_slug, registered_on
                FROM data_warehouse.dim_schedules
                WHERE student_id IN ({formatted_resolved_ids})
                ORDER BY student_id, registered_on;
            """
            df_reg = run_query(reg_query)
        else:
            df_reg = pd.DataFrame(columns=["student_id", "registration_id", "course_slug", "registered_on"])

        st.dataframe(df_reg, use_container_width=True)

        
        if ids:
            reg_query = f"""
                SELECT DISTINCT student_id, registration_id, course_slug, registered_on
                FROM data_warehouse.dim_schedules
                WHERE student_id IN ({formatted_resolved_ids})
                ORDER BY student_id, registered_on;
            """
            df_reg = run_query(reg_query)
        else:
            df_reg = pd.DataFrame(columns=["student_id", "registration_id", "course_slug", "registered_on"])

        # --- 6. Revenue Breakdown ---
        st.subheader("💰 Revenue & Transactions")

        if resolved_ids:
            rev_query = f"""
                SELECT student_id, transaction_id, payment_date, converted_amount,
                    CASE
                        WHEN description ILIKE '%lifetime%' THEN 'Rev2'
                        WHEN description ILIKE '%course%' OR description ILIKE '%material%' OR description ILIKE '%hard%' THEN 'Rev3'
                        WHEN plan_id IS NOT NULL THEN 'Rev1'
                        ELSE 'Other'
                    END AS revenue_type,
                    description
                FROM data_marts.combined_transactions
                WHERE student_id IN ({formatted_resolved_ids})
                AND converted_amount > 0
                ORDER BY student_id, payment_date;
            """
            df_rev = run_query(rev_query)
        else:
            df_rev = pd.DataFrame(columns=["student_id", "transaction_id", "payment_date", "converted_amount", "revenue_type", "description"])

        st.dataframe(df_rev, use_container_width=True)



        # --- 5. Attendance After Registration (for filtered students only) ---
        st.subheader("🎥 Attendance (Watched > 0 sec, Post Registration)")

        if resolved_ids:
            att_query_post_reg = f"""
                SELECT distinct 
                    dsc.student_id,
                    fa.value__registrations_id AS registration_id,
                    dsc.course_slug,
                    fa.value__create_at AS attended_on,
                    fa.value__module_number__bigint AS module_number,
                    fa.value__lesson_number__bigint AS lesson_number,
                    fa.value__watched__bigint AS watched_secs
                FROM firestore_api.firestore_attendance fa
                JOIN data_warehouse.dim_schedules dsc
                ON fa.value__registrations_id = dsc.registration_id
                WHERE dsc.student_id IN ({formatted_resolved_ids})
                AND fa.value__watched__bigint > 0
                ORDER BY dsc.student_id, fa.value__create_at, module_number, lesson_number;
            """
            df_att_post = run_query(att_query_post_reg)
        else:
            df_att_post = pd.DataFrame(columns=[
                "student_id", "registration_id", "course_slug", "attended_on",
                "module_number", "lesson_number", "watched_secs"
            ])

        st.dataframe(df_att_post, use_container_width=True)
        # --- 📊 Attendance Grouped by Module (Color = Lesson) ---
        if not df_att_post.empty:
            df_att_post["watched_mins"] = df_att_post["watched_secs"] / 60
            df_att_post["lesson_number"] = df_att_post["lesson_number"].astype(int)
            df_att_post["module_number"] = df_att_post["module_number"].astype('Int64')
            df_att_post["attended_on"] = pd.to_datetime(df_att_post["attended_on"])

            st.subheader("📊 Module-wise Attendance (Colored by Lesson)")

            for student_id, student_df in df_att_post.groupby("student_id"):
                with st.expander(f"👤 Student ID: {student_id}", expanded=False):
                    for (reg_id, course), reg_df in student_df.groupby(["registration_id", "course_slug"]):
                        watch_dates = reg_df["attended_on"].dt.date.unique()
                        st.markdown(
                            f"""
                            <div style='margin-bottom: 10px; margin-top: 20px;'>
                                <b>📘 Course:</b> <span style='color: #4AE0A7;'>{course}</span> &nbsp;&nbsp;
                                <b>🕒 Watch Dates:</b> <span style='color: #F96900;'>{', '.join(map(str, watch_dates))}</span><br>
                                <b>🆔 Registration ID:</b> <code>{reg_id}</code>
                            </div>
                            """, unsafe_allow_html=True
                        )

                        fig = px.bar(
                            reg_df,
                            x="module_number",
                            y="watched_mins",
                            color="lesson_number",
                            barmode="group",
                            labels={
                                "module_number": "Module Number",
                                "lesson_number": "Lesson",
                                "watched_mins": "Minutes Watched"
                            },
                            title=None,
                            height=400
                        )
                        fig.update_layout(
                            bargap=0.2,
                            xaxis=dict(type="category"),
                            margin=dict(t=10, l=10, r=10, b=30),
                            legend_title="Lesson"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            
            
        # --- 6. Attendance (All-Time Records) ---
        st.subheader("🎥 Attendance Records (Watched > 0 sec)")

        if resolved_ids:
            att_query_all = f"""
                SELECT distinct
                    fa.value__student_id AS student_id,
                    fa.value__registrations_id AS registration_id,
                    dsc.course_slug,
                    fa.value__module_number__bigint AS module_number,
                    fa.value__lesson_number__bigint AS lesson_number,
                    fa.value__watched__bigint AS watched_secs
                FROM firestore_api.firestore_attendance fa
                JOIN data_warehouse.dim_schedules dsc 
                ON fa.value__registrations_id = dsc.registration_id
                WHERE fa.value__student_id IN ({formatted_resolved_ids})
                AND fa.value__watched__bigint > 0;
            """
            df_att_all = run_query(att_query_all)
        else:
            df_att_all = pd.DataFrame(columns=[
                "student_id", "registration_id", "course_slug",
                "module_number", "lesson_number", "watched_secs"
            ])

        st.dataframe(df_att_all, use_container_width=True)

        # --- 📊 Attendance Chart per Course ---
        if not df_att_all.empty:
            df_att_all["watched_mins"] = df_att_all["watched_secs"] / 60
            df_att_all["lesson_number"] = df_att_all["lesson_number"].astype(int)
            df_att_all["module_number"] = df_att_all["module_number"].astype('Int64')

            st.subheader("📊 Lesson-wise Attendance by Course")

            for course in df_att_all["course_slug"].unique():
                st.markdown(f"**📘 Course: `{course}`**")

                course_data = df_att_all[df_att_all["course_slug"] == course].sort_values(["module_number", "lesson_number"])

                fig = px.bar(
                    course_data,
                    x="lesson_number",
                    y="watched_mins",
                    color="module_number",
                    barmode="group",
                    labels={"lesson_number": "Lesson", "watched_mins": "Minutes Watched"},
                    height=350
                )
                fig.update_layout(
                    xaxis=dict(tickmode='linear'),
                    bargap=0.25,
                    margin=dict(t=10, l=10, r=10, b=40),
                )
                st.plotly_chart(fig, use_container_width=True)
