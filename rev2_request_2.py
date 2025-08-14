# tab6_app.py
import pandas as pd
import psycopg2
import streamlit as st
from datetime import date

st.set_page_config(page_title="Tab 6 — Key Metrics", layout="wide")
st.title("📊 Tab 6 — Key Cohort Metrics from Uploaded Emails")

# DB connection
def redshift_conn():
    return psycopg2.connect(
        host="misreporting.cxgsxkol4p2y.eu-west-1.redshift.amazonaws.com",
        port=5439,
        dbname="misreportingdb",
        user="etluser",
        password="Etluser12345"
    )

# Sidebar inputs
st.sidebar.header("📁 Input Data")
lp_file = st.sidebar.file_uploader("Upload Lifetime Purchases (Excel/CSV)", type=["xlsx", "xls", "csv"])
default_start = date(2024, 1, 1)
start_date = st.sidebar.date_input("Start date (Lead created ≥)", default_start)
end_date = st.sidebar.date_input("End date", date.today())

# File helpers
def read_any(file):
    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

def clean_email_series(s):
    return (
        pd.Series(s, dtype="string")
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "", regex=True)
    )

if lp_file is None:
    st.info("Upload your Lifetime Purchases file to begin.")
    st.stop()

lp_df = read_any(lp_file)
lp_df.columns = [c.strip() for c in lp_df.columns]
if "Customer Email" not in lp_df.columns:
    st.error("The file must contain a 'Customer Email' column.")
    st.stop()

emails = clean_email_series(lp_df["Customer Email"]).dropna().drop_duplicates()
emails = emails[emails.str.contains("@")]
if emails.empty:
    st.error("No valid emails found in uploaded file.")
    st.stop()

try:
    conn = redshift_conn()
    conn.autocommit = False
    cur = conn.cursor()

    # Create temp table for emails
    cur.execute("CREATE TEMP TABLE IF NOT EXISTS input_emails (email_address VARCHAR(320));")
    cur.execute("TRUNCATE TABLE input_emails;")
    records = [(e,) for e in emails.tolist()]
    for i in range(0, len(records), 1000):
        chunk = records[i:i+1000]
        args_str = ",".join(cur.mogrify("(%s)", r).decode("utf-8") for r in chunk)
        cur.execute("INSERT INTO input_emails (email_address) VALUES " + args_str)

    # Check if assignments table exists
    cur.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema='firestore_api' 
        AND table_name='firestore_assignments'
    """)
    assignments_exist = cur.fetchone()[0] > 0

    # Build SQL dynamically
    assignments_cte = ""
    assignments_select = ""
    assignments_join = ""

    if assignments_exist:
        assignments_cte = f"""
        , assignments AS (
            SELECT
                dsc.student_id,
                SUM(CASE WHEN LOWER(COALESCE(fa.value__status, '')) LIKE '%complete%' THEN 1 ELSE 0 END) AS assignments_completed,
                SUM(CASE WHEN LOWER(COALESCE(fa.value__status, '')) LIKE '%click%' THEN 1 ELSE 0 END) AS assignments_clicked
            FROM firestore_api.firestore_assignments fa
            JOIN data_warehouse.dim_schedules dsc
              ON fa.value__registrations_id = dsc.registration_id
            JOIN ds ON ds.student_id = dsc.student_id
            GROUP BY 1
        )
        """
        assignments_select = """
            , COALESCE(asg.assignments_completed, 0) AS assignments_completed
            , COALESCE(asg.assignments_clicked, 0) AS assignments_clicked
        """
        assignments_join = "LEFT JOIN assignments asg ON asg.student_id = ds.student_id"

    sql_tab6 = f"""
    WITH ds AS (
        SELECT
            student_id,
            LOWER(TRIM(email_address)) AS email_address,
            created_date AS lead_created_date
        FROM data_warehouse.dim_students
        WHERE LOWER(TRIM(email_address)) IN (SELECT email_address FROM input_emails)
          AND created_date BETWEEN '{start_date}' AND '{end_date}'
    ),
    cc AS (
        SELECT
            cs.value__meta_data_lead_id AS student_id,
            MIN(cs.created_at) AS cc_date
        FROM data_marts.combined_subscriptions cs
        JOIN ds ON ds.student_id = cs.value__meta_data_lead_id
        GROUP BY 1
    ),
    first_purchase AS (
        SELECT
            t.student_id,
            MIN(t.payment_date) AS first_purchase_date
        FROM data_marts.combined_transactions t
        JOIN cc ON cc.student_id = t.student_id
        WHERE t.payment_date >= cc.cc_date
          AND t.converted_amount > 0
        GROUP BY 1
    ),
    prior_subs AS (
        SELECT
            cs.value__meta_data_lead_id AS student_id,
            COUNT(*) AS prior_subscriptions
        FROM data_marts.combined_subscriptions cs
        JOIN cc ON cc.student_id = cs.value__meta_data_lead_id
        WHERE cs.created_at < cc.cc_date
        GROUP BY 1
    ),
    attendance AS (
        SELECT
            dsc.student_id,
            COUNT(*) AS attended_sessions
        FROM firestore_api.firestore_attendance fa
        JOIN data_warehouse.dim_schedules dsc
            ON fa.value__registrations_id = dsc.registration_id
        JOIN ds ON ds.student_id = dsc.student_id
        WHERE fa.value__watched__bigint > 0
        GROUP BY 1
    )
    {assignments_cte}
    SELECT
        ds.student_id,
        ds.email_address,
        ds.lead_created_date,
        cc.cc_date,
        fp.first_purchase_date,
        DATEDIFF('day', cc.cc_date, fp.first_purchase_date) AS days_cc_to_purchase,
        COALESCE(att.attended_sessions, 0) AS attended_sessions
        {assignments_select},
        COALESCE(ps.prior_subscriptions, 0) AS prior_subscriptions
    FROM ds
    LEFT JOIN cc ON cc.student_id = ds.student_id
    LEFT JOIN first_purchase fp ON fp.student_id = ds.student_id
    LEFT JOIN prior_subs ps ON ps.student_id = ds.student_id
    LEFT JOIN attendance att ON att.student_id = ds.student_id
    {assignments_join}
    ;
    """

    df_tab6 = pd.read_sql(sql_tab6, conn)
    conn.commit()

except Exception as e:
    conn.rollback()
    st.error(f"Error running Tab 6 query: {e}")
    st.stop()
finally:
    try:
        cur.execute("DROP TABLE IF EXISTS input_emails;")
        conn.commit()
    except Exception:
        pass
    cur.close()
    conn.close()

# Display results
if df_tab6.empty:
    st.info("No matching records found.")
else:
    avg_days = df_tab6["days_cc_to_purchase"].dropna()
    st.metric("Avg Days CC → Purchase", f"{avg_days.mean():.1f}" if not avg_days.empty else "—")
    st.metric("Avg Attendance Sessions", f"{df_tab6['attended_sessions'].mean():.2f}")
    st.metric("Prior Subscriptions", f"{int(df_tab6['prior_subscriptions'].sum()):,}")
    if "assignments_completed" in df_tab6.columns:
        st.metric("Assignments Completed", f"{int(df_tab6['assignments_completed'].sum()):,}")
        st.metric("Assignments Clicked", f"{int(df_tab6['assignments_clicked'].sum()):,}")

    st.markdown("### Preview Data")
    st.dataframe(df_tab6.head(50), use_container_width=True)
    st.download_button(
        "⬇️ Download Tab 6 Dataset",
        data=df_tab6.to_csv(index=False).encode("utf-8"),
        file_name="tab6_metrics.csv",
        mime="text/csv",
    )
