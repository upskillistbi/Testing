# app.py
import io
from datetime import date
from textwrap import dedent

import numpy as np
import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st

# -----------------------------
# Page & Title
# -----------------------------
st.set_page_config(page_title="Lifetime Purchases → Dim Students (Tab 1)", layout="wide")
st.title("🎓 Lifetime Purchases → Dim Students — Tab 1: Dataset & EDA")

# -----------------------------
# Redshift connection (as requested)
# -----------------------------
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

# Robust fetch: load emails into TEMP table, join to dim_students
def fetch_dim_students_for_emails(emails, start_date="2024-01-01", end_date=None, batch_size=1000):
    """
    Loads emails into a Redshift TEMP table in batches, then returns matching dim_students rows.
    Filters by ds.created_date between start_date and end_date (inclusive).
    """
    emails = pd.Series(emails, dtype="string").dropna().str.strip().str.lower()
    emails = emails[emails.str.contains("@")].drop_duplicates()
    if emails.empty:
        return pd.DataFrame()

    if end_date is None:
        end_date = date.today().isoformat()

    conn = psycopg2.connect(
        host="misreporting.cxgsxkol4p2y.eu-west-1.redshift.amazonaws.com",
        port=5439,
        dbname="misreportingdb",
        user="etluser",
        password="Etluser12345"
    )
    conn.autocommit = False
    cur = conn.cursor()
    try:
        # 1) temp table
        cur.execute("CREATE TEMP TABLE IF NOT EXISTS input_emails (email_address VARCHAR(320));")
        cur.execute("TRUNCATE TABLE input_emails;")

        # 2) batch insert
        records = [(e,) for e in emails.tolist()]
        for i in range(0, len(records), batch_size):
            chunk = records[i:i+batch_size]
            args_str = ",".join(cur.mogrify("(%s)", r).decode("utf-8") for r in chunk)
            cur.execute("INSERT INTO input_emails (email_address) VALUES " + args_str)

        # 3) select
        select_sql = dedent("""
            SELECT
                ds.student_id,
                ds.first_name,
                ds.last_name,
                LOWER(TRIM(ds.email_address)) AS email_address,
                ds.created_date,
                ds.country,
                ds.utm_source,
                ds.latest_utm_source,
                ds.latest_utm_medium,
                ds.latest_utm_campaign,
                ds.coursepicked,
                ds.total_minutes AS live_minutes,
                ds.goal,
                ds.age_group,
                ds.gender,
                ds.profile__partner_identifier AS partner_identifier
            FROM data_warehouse.dim_students ds
            JOIN input_emails ie
              ON LOWER(TRIM(ds.email_address)) = ie.email_address
            WHERE ds.created_date >= %s
              AND ds.created_date <= %s
        """)
        df = pd.read_sql(select_sql, conn, params=[start_date, end_date])

        conn.commit()
        return df
    except Exception:
        conn.rollback()
        raise
    finally:
        try:
            cur.execute("DROP TABLE IF EXISTS input_emails;")
            conn.commit()
        except Exception:
            pass
        cur.close()
        conn.close()

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("📁 Inputs")
lp_file = st.sidebar.file_uploader("Upload Lifetime Purchases (Excel/CSV)", type=["xlsx", "xls", "csv"])

st.sidebar.header("🗓️ Created Date Filter (dim_students)")
default_start = date(2024, 1, 1)
start_date = st.sidebar.date_input("Created date ≥", default_start)
end_date = st.sidebar.date_input("Created date ≤", date.today())
st.sidebar.caption("Applied to data_warehouse.dim_students.created_date")

# -----------------------------
# Helpers
# -----------------------------
def read_any(file):
    name = file.name.lower()
    if name.endswith(".csv"):
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

def standardize_lp_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    # Try to normalize known columns
    rename_candidates = {c.lower(): c for c in df.columns}
    # Ensure required columns exist / normalized
    if "customer email" in rename_candidates and rename_candidates["customer email"] != "Customer Email":
        df.rename(columns={rename_candidates["customer email"]: "Customer Email"}, inplace=True)
    if "id at gateway" in rename_candidates and rename_candidates["id at gateway"] != "Id At Gateway":
        df.rename(columns={rename_candidates["id at gateway"]: "Id At Gateway"}, inplace=True)
    if "amount" in rename_candidates and rename_candidates["amount"] != "Amount":
        df.rename(columns={rename_candidates["amount"]: "Amount"}, inplace=True)
    if "currency" in rename_candidates and rename_candidates["currency"] != "Currency":
        df.rename(columns={rename_candidates["currency"]: "Currency"}, inplace=True)

    # Clean values
    if "Customer Email" in df.columns:
        df["Customer Email"] = clean_email_series(df["Customer Email"])
    if "Currency" in df.columns:
        df["Currency"] = df["Currency"].astype(str).str.strip().str.upper()
    if "Amount" in df.columns:
        df["Amount"] = (
            df["Amount"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.extract(r"([-+]?\d*\.?\d+)", expand=False)
        )
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    return df

# -----------------------------
# Early exit if no file
# -----------------------------
if lp_file is None:
    st.info("Upload your **Lifetime Purchases** Excel/CSV to begin.")
    st.stop()

# -----------------------------
# Load & standardize Excel (Lifetime Purchases)
# -----------------------------
lp_df = read_any(lp_file)
lp_df = standardize_lp_columns(lp_df)

# Validate required column
if "Customer Email" not in lp_df.columns:
    st.error("Your file must include a 'Customer Email' column.")
    st.stop()

# -----------------------------
# Fetch matching dim_students from Redshift
# -----------------------------
emails = lp_df["Customer Email"].dropna().tolist()
dim_df = fetch_dim_students_for_emails(
    emails,
    start_date=start_date.isoformat(),
    end_date=end_date.isoformat()
)

# -----------------------------
# Merge Excel ↔ dim_students
# -----------------------------
out = lp_df.merge(
    dim_df,
    how="left",
    left_on="Customer Email",
    right_on="email_address"
)

# Derived: parsed created date + date-only
if "created_date" in out.columns:
    out["created_date"] = pd.to_datetime(out["created_date"], errors="coerce")
    out["created_date_date"] = out["created_date"].dt.date

# -----------------------------
# Tabs (only Tab 1 implemented)
# -----------------------------
tab1, tab2, tab3, tab4,tab5,tab6,tab7 = st.tabs([
    "1) Dataset & EDA",
    "2) (reserved)",
    "3) (reserved)",
    "4) (reserved)",
    "5) (reserved)","6) (reserved)","7) Requested analysis"
])

# =============================
# TAB 1 — Dataset & EDA
# =============================
with tab1:
    st.subheader("🔍 Merged Dataset Preview")

    # Match metrics
    total_rows = len(lp_df)
    uniq_emails = lp_df["Customer Email"].nunique()
    matched = out["student_id"].notna().sum() if "student_id" in out.columns else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows in Excel", f"{total_rows:,}")
    c2.metric("Unique Emails", f"{uniq_emails:,}")
    c3.metric("Matched in dim_students", f"{matched:,}")

    # Show prioritized columns first
    important_cols = [
        "Id At Gateway", "Customer Email", "Amount", "Currency",
        "student_id", "first_name", "last_name", "created_date",
        "country", "utm_source", "latest_utm_source",
        "latest_utm_medium", "latest_utm_campaign",
        "coursepicked", "live_minutes", "goal", "age_group", "gender",
        "partner_identifier"
    ]
    cols = [c for c in important_cols if c in out.columns] + [c for c in out.columns if c not in important_cols]

    st.dataframe(out[cols].head(50), use_container_width=True)

    # Null summary bar
    st.markdown("### 🧬 Null Summary")
    nulls = out[cols].isna().sum().sort_values(ascending=False)
    st.bar_chart(nulls)

    # Duplicate checks on Id & Email
    st.markdown("### 🧭 Duplicates & Uniqueness")
    dup_id = out["Id At Gateway"].duplicated().sum() if "Id At Gateway" in out.columns else 0
    dup_email = out["Customer Email"].duplicated().sum()
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Unique Gateway IDs", f"{out.get('Id At Gateway', pd.Series(dtype=str)).nunique():,}" if "Id At Gateway" in out.columns else "—")
    d2.metric("Duplicate Gateway IDs", f"{dup_id:,}" if "Id At Gateway" in out.columns else "—")
    d3.metric("Unique Emails", f"{out['Customer Email'].nunique():,}")
    d4.metric("Duplicate Emails", f"{dup_email:,}")

    # Amount summaries (if present)
    if "Amount" in out.columns:
        st.markdown("### 💰 Amount Summary")
        summ_all = out["Amount"].describe(percentiles=[0.25, 0.5, 0.75]).to_frame("Amount").reset_index().rename(columns={"index":"stat"})
        st.dataframe(summ_all, use_container_width=True)

        if "Currency" in out.columns:
            st.markdown("#### By Currency")
            by_cur = (
                out.groupby("Currency", dropna=False)
                  .agg(
                      rows=("Amount", "size"),
                      non_null=("Amount", lambda s: s.notna().sum()),
                      sum_amount=("Amount", "sum"),
                      mean_amount=("Amount", "mean"),
                      median_amount=("Amount", "median"),
                      std_amount=("Amount", "std"),
                      min_amount=("Amount", "min"),
                      p25=("Amount", lambda s: s.quantile(0.25)),
                      p75=("Amount", lambda s: s.quantile(0.75)),
                      max_amount=("Amount", "max"),
                  )
                  .reset_index()
            )
            st.dataframe(by_cur, use_container_width=True)

            # Quick charts
            cA, cB = st.columns(2)
            with cA:
                fig1 = px.bar(by_cur, x="Currency", y="sum_amount", text="sum_amount", title="Total Amount by Currency")
                fig1.update_traces(texttemplate="%{text:.2f}", textposition="outside")
                fig1.update_layout(yaxis_title="Total Amount", xaxis_title=None)
                st.plotly_chart(fig1, use_container_width=True)
            with cB:
                fig2 = px.bar(by_cur, x="Currency", y="rows", text="rows", title="Count by Currency")
                fig2.update_traces(textposition="outside")
                fig2.update_layout(yaxis_title="Rows", xaxis_title=None)
                st.plotly_chart(fig2, use_container_width=True)

            # Distribution
            st.markdown("#### Amount Distribution")
            hist = px.histogram(out, x="Amount", nbins=30, title="Amount Histogram")
            st.plotly_chart(hist, use_container_width=True)

 # =============================
    # Age Group Breakdown
    # =============================
    if "age_group" in out.columns:
        st.markdown("### 👥 Age Group Breakdown")
        age_counts = (
            out.groupby("age_group", dropna=False)
               .agg(
                   rows=("Customer Email", "count"),
                   uniq_students=("student_id", pd.Series.nunique)
               )
               .reset_index()
               .sort_values("rows", ascending=False)
        )
        age_counts["%_of_total"] = (age_counts["rows"] / age_counts["rows"].sum() * 100).round(2)
        st.dataframe(age_counts, use_container_width=True)

        fig_age = px.bar(
            age_counts,
            x="age_group",
            y="rows",
            text="rows",
            title="Purchasers by Age Group"
        )
        fig_age.update_traces(textposition="outside")
        fig_age.update_layout(xaxis_title="Age Group", yaxis_title="Count")
        st.plotly_chart(fig_age, use_container_width=True)

    # =============================
    # Gender Breakdown
    # =============================
    if "gender" in out.columns:
        st.markdown("### 🚻 Gender Breakdown")
        gender_counts = (
            out.groupby("gender", dropna=False)
               .agg(
                   rows=("Customer Email", "count"),
                   uniq_students=("student_id", pd.Series.nunique)
               )
               .reset_index()
               .sort_values("rows", ascending=False)
        )
        gender_counts["%_of_total"] = (gender_counts["rows"] / gender_counts["rows"].sum() * 100).round(2)
        st.dataframe(gender_counts, use_container_width=True)

        fig_gender = px.pie(
            gender_counts,
            names="gender",
            values="rows",
            title="Purchasers by Gender",
            hole=0.3
        )
        fig_gender.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_gender, use_container_width=True)
    # Download merged dataset
    st.markdown("### ⬇️ Download")
    csv = out.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download merged CSV",
        data=csv,
        file_name="lifetime_purchases_joined_dim_students.csv",
        mime="text/csv",
    )


# =============================
# TAB 1 — Dataset & EDA
# =============================
with tab6:
    st.subheader("🔍 Merged Dataset Preview")
    st.write(f"Rows in Excel: **{len(lp_df):,}**  |  Unique Emails: **{lp_df['Customer Email'].nunique():,}**")
    matched = out["student_id"].notna().sum()
    st.write(f"Matched in dim_students (created_date in range): **{matched:,}**  |  Match rate: **{(matched/len(lp_df)*100 if len(lp_df) else 0):.1f}%**")

    # Show important columns first if present
    important_cols = [
        "Id At Gateway", "Customer Email", "Amount", "Currency",
        "student_id", "first_name", "last_name", "created_date",
        "country", "utm_source", "latest_utm_source",
        "coursepicked", "live_minutes", "goal", "age_group", "gender",
        "partner_identifier"
    ]
    cols = [c for c in important_cols if c in out.columns] + [c for c in out.columns if c not in important_cols]
    st.dataframe(out[cols].head(30), use_container_width=True)

    # Null summary
    st.markdown("### 🧬 Null Summary")
    nulls = out[cols].isna().sum().sort_values(ascending=False)
    st.bar_chart(nulls)

    # Download
    csv = out.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download merged CSV", data=csv, file_name="lifetime_purchases_joined_dim_students.csv", mime="text/csv")

# =============================
# TAB 2 — Country Breakdown
# =============================
with tab2:
    st.subheader("🌍 Purchasers by Country")
    if "country" in out.columns:
        ctab = (out.groupby("country", dropna=False)
                  .agg(
                      rows=("Customer Email", "count"),
                      uniq_students=("student_id", pd.Series.nunique),
                      avg_live_minutes=("live_minutes", "mean")
                  )
                  .reset_index()
                  .sort_values("rows", ascending=False))
        st.dataframe(ctab, use_container_width=True)

        fig = px.bar(ctab.head(25), x="country", y="rows", text="rows", title="Count by Country")
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_title=None, yaxis_title="Rows")
        st.plotly_chart(fig, use_container_width=True)

        # Top countries filter to inspect details
        top_countries = ctab["country"].dropna().head(10).tolist()
        pick = st.multiselect("Filter countries", options=ctab["country"].dropna().unique(), default=top_countries)
        filt = out[out["country"].isin(pick)] if pick else out
        st.markdown("**Sample rows for selected countries**")
        st.dataframe(filt[cols].head(50), use_container_width=True)
    else:
        st.info("No `country` column available in the merged output.")

# =============================
# TAB 3 — UTM/Channel Breakdown
# =============================
with tab3:
    st.subheader("📣 UTM / Channel Breakdown")
    # Primary & latest source lenses
    for src_col, title in [("utm_source", "utm_source (original)"),
                           ("latest_utm_source", "latest_utm_source")]:
        if src_col in out.columns:
            st.markdown(f"#### {title}")
            utm = (out.groupby(src_col, dropna=False)
                     .agg(rows=("Customer Email", "count"),
                          uniq_students=("student_id", pd.Series.nunique))
                     .reset_index()
                     .sort_values("rows", ascending=False))
            st.dataframe(utm, use_container_width=True)
            fig = px.bar(utm.head(30), x=src_col, y="rows", text="rows", title=f"Count by {src_col}")
            fig.update_traces(textposition="outside")
            fig.update_layout(xaxis_title=None, yaxis_title="Rows")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption(f"`{src_col}` not present.")
    # Medium/Campaign if present
    for extra_col in ["latest_utm_medium", "latest_utm_campaign"]:
        if extra_col in out.columns:
            st.markdown(f"#### {extra_col}")
            tmp = out[extra_col].value_counts(dropna=False).reset_index()
            tmp.columns = [extra_col, "rows"]
            st.dataframe(tmp.head(30), use_container_width=True)

# =============================
# TAB 4 — Course & Engagement
# =============================
with tab4:
    st.subheader("📚 Coursepicked & Engagement")

    if "coursepicked" in out.columns:
        course_counts = (out["coursepicked"]
                         .value_counts(dropna=False)
                         .rename_axis("coursepicked")
                         .reset_index(name="rows"))
        st.markdown("#### Top Courses")
        st.dataframe(course_counts.head(30), use_container_width=True)

        figc = px.bar(course_counts.head(30), x="coursepicked", y="rows", text="rows", title="Purchasers by Course Picked")
        figc.update_traces(textposition="outside")
        figc.update_layout(xaxis_title=None, yaxis_title="Rows")
        st.plotly_chart(figc, use_container_width=True)

    if "live_minutes" in out.columns:
        st.markdown("#### Live Minutes (Total)")
        stats = out["live_minutes"].describe().to_frame("live_minutes").reset_index().rename(columns={"index":"stat"})
        st.dataframe(stats, use_container_width=True)
        figh = px.histogram(out, x="live_minutes", nbins=30, title="Distribution of Live Minutes")
        st.plotly_chart(figh, use_container_width=True)

    # Cohorting by created_date
    if "created_date_date" in out.columns:
        st.markdown("#### Created Date Cohort (Daily)")
        daily = out.groupby("created_date_date").size().reset_index(name="rows").sort_values("created_date_date")
        st.dataframe(daily.tail(15), use_container_width=True)
        figd = px.line(daily, x="created_date_date", y="rows", title="Counts by Created Date")
        st.plotly_chart(figd, use_container_width=True)

st.success("Tabs ready. Data joined on email, filtered by created_date range (default ≥ 2024-01-01).")


# =============================
# TAB 5 — Cohort Behavior & Global Metrics
# =============================
with tab5:
    st.subheader("🎯 Cohort Behavior: Lead → CC → Purchase + Activity")

    # --- Helper: execute cohort query with TEMP email table ---
    def cohort_query_for_emails(emails, start_date, end_date):
        emails = (
            pd.Series(emails, dtype="string")
            .dropna().str.strip().str.lower()
            .loc[lambda s: s.str.contains("@")].drop_duplicates()
        )
        if emails.empty:
            return pd.DataFrame()

        conn = psycopg2.connect(
            host="misreporting.cxgsxkol4p2y.eu-west-1.redshift.amazonaws.com",
            port=5439,
            dbname="misreportingdb",
            user="etluser",
            password="Etluser12345"
        )
        conn.autocommit = False
        cur = conn.cursor()
        try:
            # 1) temp table for the cohort emails
            cur.execute("CREATE TEMP TABLE IF NOT EXISTS input_emails (email_address VARCHAR(320));")
            cur.execute("TRUNCATE TABLE input_emails;")

            # 2) batch insert emails
            records = [(e,) for e in emails.tolist()]
            for i in range(0, len(records), 1000):
                chunk = records[i:i+1000]
                args_str = ",".join(cur.mogrify("(%s)", r).decode("utf-8") for r in chunk)
                cur.execute("INSERT INTO input_emails (email_address) VALUES " + args_str)

            # 3) main cohort SELECT
            sql = dedent(f"""
                WITH ds AS (
                    SELECT
                        student_id,
                        LOWER(TRIM(email_address)) AS email_address,
                        created_date,
                        country,
                        utm_source,
                        latest_utm_source,
                        latest_utm_medium,
                        latest_utm_campaign,
                        coursepicked,
                        total_minutes AS live_minutes,
                        goal,
                        age_group,
                        gender,
                        profile__partner_identifier AS partner_identifier
                    FROM data_warehouse.dim_students
                    WHERE created_date BETWEEN %s AND %s
                ),
                cohort AS (
                    SELECT ds.*
                    FROM ds
                    JOIN input_emails ie
                      ON ds.email_address = ie.email_address
                ),
                cc AS (  -- first CC (subscription) date per student
                    SELECT
                        cs.value__meta_data_lead_id AS student_id,
                        MIN(cs.created_at) AS cc_date
                    FROM data_marts.combined_subscriptions cs
                    JOIN cohort c ON c.student_id = cs.value__meta_data_lead_id
                    GROUP BY 1
                ),
                tx AS (  -- all paid transactions for these students in the window
                    SELECT
                        t.student_id,
                        t.payment_date,
                        t.converted_amount,
                        t.description,
                        t.plan_id
                    FROM data_marts.combined_transactions t
                    JOIN cohort c ON c.student_id = t.student_id
                    WHERE t.payment_date BETWEEN %s AND %s
                      AND t.converted_amount > 0
                ),
                first_purchase_after_cc AS (  -- first txn on/after CC date
                    SELECT
                        t.student_id,
                        MIN(t.payment_date) AS first_purchase_date
                    FROM tx t
                    JOIN cc ON cc.student_id = t.student_id
                    WHERE t.payment_date >= cc.cc_date
                    GROUP BY 1
                ),
                prior_subs AS (  -- subscriptions before first CC (edge cases)
                    SELECT
                        cs.value__meta_data_lead_id AS student_id,
                        COUNT(*) AS prior_sub_count
                    FROM data_marts.combined_subscriptions cs
                    JOIN cc ON cc.student_id = cs.value__meta_data_lead_id
                    WHERE cs.created_at < cc.cc_date
                    GROUP BY 1
                ),
                prior_tx AS (  -- paid txns before CC date
                    SELECT
                        t.student_id,
                        COUNT(*) AS prior_txn_count
                    FROM data_marts.combined_transactions t
                    JOIN cc ON cc.student_id = t.student_id
                    WHERE t.payment_date < cc.cc_date
                      AND t.converted_amount > 0
                    GROUP BY 1
                ),
                att AS (  -- attendance sessions (watched >0)
                    SELECT
                        dsc.student_id,
                        COUNT(*) AS attended_sessions,
                        COUNT(DISTINCT dsc.registration_id) AS regs_attended
                    FROM firestore_api.firestore_attendance fa
                    JOIN data_warehouse.dim_schedules dsc
                      ON fa.value__registrations_id = dsc.registration_id
                    JOIN cohort c ON c.student_id = dsc.student_id
                    WHERE fa.value__watched__bigint > 0
                      AND fa.value__create_at  BETWEEN %s AND %s
                    GROUP BY 1
                )
                SELECT
                    c.student_id,
                    c.email_address,
                    c.created_date AS lead_created_date,
                    c.country,
                    c.utm_source,
                    c.latest_utm_source,
                    c.latest_utm_medium,
                    c.latest_utm_campaign,
                    c.coursepicked,
                    c.live_minutes,
                    c.goal,
                    c.age_group,
                    c.gender,
                    c.partner_identifier,
                    cc.cc_date,
                    fp.first_purchase_date,
                    DATEDIFF('day', cc.cc_date, fp.first_purchase_date) AS days_cc_to_purchase,
                    COALESCE(prs.prior_sub_count, 0) AS prior_subscriptions,
                    COALESCE(prt.prior_txn_count, 0) AS prior_paid_txns,
                    COALESCE(a.attended_sessions, 0) AS attended_sessions,
                    COALESCE(a.regs_attended, 0) AS regs_attended
                FROM cohort c
                LEFT JOIN cc ON cc.student_id = c.student_id
                LEFT JOIN first_purchase_after_cc fp ON fp.student_id = c.student_id
                LEFT JOIN prior_subs prs ON prs.student_id = c.student_id
                LEFT JOIN prior_tx prt ON prt.student_id = c.student_id
                LEFT JOIN att a ON a.student_id = c.student_id
            """)

            df = pd.read_sql(sql, conn, params=[start_date, end_date, start_date, end_date, start_date, end_date])
            conn.commit()
            return df

        except Exception as e:
            conn.rollback()
            raise
        finally:
            try:
                cur.execute("DROP TABLE IF EXISTS input_emails;")
                conn.commit()
            except Exception:
                pass
            cur.close()
            conn.close()

    # --- run cohort query for current upload ---
    cohort_df = cohort_query_for_emails(
        emails=lp_df["Customer Email"].tolist(),
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )

    # --- (Optional) Assignments: try to enrich if table/schema exists ---
    def try_fetch_assignments(start_date, end_date):
        try:
            sql_asg = dedent("""
                SELECT
                    dsc.student_id,
                    COUNT(*) AS assignment_events,
                    SUM(CASE WHEN LOWER(COALESCE(fa.value__status, '')) LIKE '%complete%' THEN 1 ELSE 0 END) AS assignments_completed,
                    SUM(CASE WHEN LOWER(COALESCE(fa.value__status, '')) LIKE '%click%' THEN 1 ELSE 0 END) AS assignments_clicked
                FROM firestore_api.firestore_assignments fa
                JOIN data_warehouse.dim_schedules dsc
                  ON fa.value__registrations_id = dsc.registration_id
                WHERE fa.value__create_at  BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY dsc.student_id
            """)
            asg = run_query(sql_asg, start_date=start_date, end_date=end_date)
            return asg
        except Exception:
            return None

    asg_df = try_fetch_assignments(start_date.isoformat(), end_date.isoformat())
    if asg_df is not None and not asg_df.empty:
        cohort_df = cohort_df.merge(asg_df, how="left", on="student_id")
        cohort_df[["assignment_events", "assignments_completed", "assignments_clicked"]] = cohort_df[
            ["assignment_events", "assignments_completed", "assignments_clicked"]
        ].fillna(0)

    # --- Show cohort table ---
    st.markdown("#### Cohort Dataset (Lead → CC → First Purchase + Activity)")
    st.dataframe(cohort_df.head(100), use_container_width=True)
    st.caption(f"Rows: {len(cohort_df):,}")

    # --- Cohort KPIs ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Cohort Size", f"{cohort_df['student_id'].nunique():,}")
    k2.metric("Have CC Date", f"{cohort_df['cc_date'].notna().sum():,}")
    k3.metric("Have First Purchase", f"{cohort_df['first_purchase_date'].notna().sum():,}")
    avg_days = cohort_df["days_cc_to_purchase"].dropna()
    k4.metric("Avg Days CC→Purchase", f"{(avg_days.mean() if len(avg_days) else 0):.1f}")

    # --- Visuals: Time to purchase, Attendance, Prior history ---
    cA, cB = st.columns(2)
    with cA:
        st.markdown("**Distribution: Days CC → First Purchase**")
        if "days_cc_to_purchase" in cohort_df.columns and cohort_df["days_cc_to_purchase"].notna().any():
            fig = px.histogram(cohort_df.dropna(subset=["days_cc_to_purchase"]), x="days_cc_to_purchase", nbins=30)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No purchase dates found for this cohort in the selected window.")

    with cB:
        st.markdown("**Attendance: Sessions per Student**")
        if "attended_sessions" in cohort_df.columns:
            fig = px.histogram(cohort_df, x="attended_sessions", nbins=30)
            st.plotly_chart(fig, use_container_width=True)

    cC, cD = st.columns(2)
    with cC:
        st.markdown("**Prior History Before CC: Subscriptions**")
        if "prior_subscriptions" in cohort_df.columns:
            prior_sub = cohort_df["prior_subscriptions"].value_counts().sort_index().reset_index()
            prior_sub.columns = ["prior_subscriptions", "students"]
            st.dataframe(prior_sub, use_container_width=True)
            fig = px.bar(prior_sub, x="prior_subscriptions", y="students")
            st.plotly_chart(fig, use_container_width=True)
    with cD:
        st.markdown("**Prior History Before CC: Paid Txns**")
        if "prior_paid_txns" in cohort_df.columns:
            prior_tx = cohort_df["prior_paid_txns"].value_counts().sort_index().reset_index()
            prior_tx.columns = ["prior_paid_txns", "students"]
            st.dataframe(prior_tx, use_container_width=True)
            fig = px.bar(prior_tx, x="prior_paid_txns", y="students")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Country Split (Cohort)**")
    if "country" in cohort_df.columns:
        ctab = (
            cohort_df.groupby("country", dropna=False)
            .agg(
                students=("student_id", "nunique"),
                with_purchase=("first_purchase_date", lambda s: s.notna().sum()),
                avg_days=("days_cc_to_purchase", "mean"),
                avg_attended_sessions=("attended_sessions", "mean")
            )
            .reset_index()
            .sort_values("students", ascending=False)
        )
        st.dataframe(ctab, use_container_width=True)
        fig = px.bar(ctab.head(25), x="country", y="students", text="students", title="Cohort Students by Country")
        fig.update_traces(textposition="outside"); fig.update_layout(xaxis_title=None, yaxis_title="Students")
        st.plotly_chart(fig, use_container_width=True)

    # === Global metrics (your references) ===
    st.subheader("🌐 Global Metrics (Reference)")

    metrics_sql = {
        "qualified_leads": """
            SELECT COUNT(DISTINCT cs.id) AS qualified_leads
            FROM data_warehouse.dim_students ds
            JOIN data_marts.combined_subscriptions cs 
                ON cs.value__meta_data_lead_id = ds.student_id
            WHERE ds.created_date BETWEEN '{start_date}' AND '{end_date}'
            ;
        """,
        "cancelled_leads": """
            SELECT COUNT(DISTINCT cs.value__meta_data_lead_id) AS cancelled_leads
            FROM data_marts.combined_subscriptions cs
            WHERE cs.cancellation_initiated_on BETWEEN '{start_date}' AND '{end_date}';
        """,
        "Registrations by Course Slug": """
            SELECT DSC.course_slug, COUNT(DISTINCT DSC.registration_id) AS total_registrations
            FROM data_warehouse.dim_schedules DSC
            WHERE DSC.registered_on BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY DSC.course_slug
            ORDER BY total_registrations DESC;
        """,
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
        "Attendance CC by Country": """
            SELECT 
                COALESCE(DS.country, 'Unknown') AS country,
                COUNT(DISTINCT FA.value__student_id) AS total_students_attended
            FROM firestore_api.firestore_attendance FA
            JOIN data_warehouse.dim_schedules DSC ON FA.value__registrations_id = DSC.registration_id
            JOIN data_marts.combined_subscriptions CS ON DSC.student_id = CS.value__meta_data_lead_id
            LEFT JOIN data_warehouse.dim_students DS ON DSC.student_id = DS.student_id
            WHERE FA.value__watched__bigint > 0
              AND FA.value__create_at  BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY COALESCE(DS.country, 'Unknown')
            ORDER BY total_students_attended DESC;
        """,
        "Total Students Attended (Leads)": """
            SELECT 
                COUNT(DISTINCT value__student_id) AS total_students_attended
            FROM firestore_api.firestore_attendance
            WHERE value__watched__bigint > 0
              AND value__create_at  BETWEEN '{start_date}' AND '{end_date}';
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
              AND FA.value__create_at  BETWEEN '{start_date}' AND '{end_date}'
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
                  AND FA.value__create_at  BETWEEN '{start_date}' AND '{end_date}'
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
              AND FA.value__create_at  BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY DSC.course_slug, FA.value__lesson_number__bigint
            ORDER BY DSC.course_slug, lesson_number;
        """,
        # Revenue metrics
        "Post Reactivation Revenue": """
            SELECT SUM(converted_amount) AS post_reactivation_revenue
            FROM data_marts.combined_transactions
            WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
              AND converted_amount > 0
              AND reactivated_on IS NOT NULL
              AND payment_date > reactivated_on;
        """,
        "Total Revenue": """
            SELECT SUM(converted_amount) AS total_revenue
            FROM data_marts.combined_transactions
            WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
              AND converted_amount > 0;
        """,
        "Unique Buyers": """
            SELECT COUNT(DISTINCT student_id) AS unique_buyers
            FROM data_marts.combined_transactions
            WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
              AND converted_amount > 0
              AND student_id IS NOT NULL;
        """,
        "Average Order Value (AOV)": """
            SELECT SUM(converted_amount) / NULLIF(COUNT(transaction_id), 0) AS average_order_value
            FROM data_marts.combined_transactions
            WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
              AND converted_amount > 0;
        """,
        "Rev1 Revenue": """
            SELECT SUM(converted_amount) AS rev1_revenue
            FROM data_marts.combined_transactions
            WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
              AND converted_amount > 0
              AND plan_id IS NOT NULL;
        """,
        "Rev2 Revenue": """
            SELECT SUM(converted_amount) AS rev2_revenue
            FROM data_marts.combined_transactions
            WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
              AND converted_amount > 0
              AND description ILIKE '%lifetime%';
        """,
        "Rev3 Revenue": """
            SELECT SUM(converted_amount) AS rev3_revenue
            FROM data_marts.combined_transactions
            WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'
              AND converted_amount > 0
              AND (
                description ILIKE '%course%' OR
                description ILIKE '%toolkit%' OR
                description ILIKE '%hard%'
              );
        """
    }

    # Run and display the global metrics
    g1, g2, g3, g4 = st.columns(4)
    try:
        ql = run_query(metrics_sql["qualified_leads"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        cl = run_query(metrics_sql["cancelled_leads"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        tr = run_query(metrics_sql["Total Revenue"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        ub = run_query(metrics_sql["Unique Buyers"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        g1.metric("Qualified Leads", f"{int(ql.iloc[0,0]) if not ql.empty else 0:,}")
        g2.metric("Cancelled Leads", f"{int(cl.iloc[0,0]) if not cl.empty else 0:,}")
        g3.metric("Total Revenue", f"{float(tr.iloc[0,0]) if not tr.empty else 0:,.2f}")
        g4.metric("Unique Buyers", f"{int(ub.iloc[0,0]) if not ub.empty else 0:,}")
    except Exception as e:
        st.warning(f"Global KPI fetch error: {e}")

    # Revenue split cards
    s1, s2, s3, s4 = st.columns(4)
    try:
        aov = run_query(metrics_sql["Average Order Value (AOV)"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        r1  = run_query(metrics_sql["Rev1 Revenue"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        r2  = run_query(metrics_sql["Rev2 Revenue"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        r3  = run_query(metrics_sql["Rev3 Revenue"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        pr  = run_query(metrics_sql["Post Reactivation Revenue"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        s1.metric("AOV", f"{float(aov.iloc[0,0]) if not aov.empty else 0:,.2f}")
        s2.metric("Rev1", f"{float(r1.iloc[0,0]) if not r1.empty else 0:,.2f}")
        s3.metric("Rev2 (Lifetime)", f"{float(r2.iloc[0,0]) if not r2.empty else 0:,.2f}")
        s4.metric("Rev3 (One‑time)", f"{float(r3.iloc[0,0]) if not r3.empty else 0:,.2f}")
        st.caption(f"Post Reactivation Revenue: {float(pr.iloc[0,0]) if not pr.empty else 0:,.2f}")
    except Exception as e:
        st.warning(f"Revenue metrics fetch error: {e}")

    # Registration & Attendance tables
    try:
        reg_slug = run_query(metrics_sql["Registrations by Course Slug"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        st.markdown("#### Registrations by Course")
        st.dataframe(reg_slug.head(50), use_container_width=True)
        fig = px.bar(reg_slug.head(30), x="course_slug", y="total_registrations", text="total_registrations")
        fig.update_traces(textposition="outside"); st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Registrations by Course error: {e}")

    try:
        reg_month = run_query(metrics_sql["Monthly Registrations (General)"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        st.markdown("#### Monthly Registrations")
        st.dataframe(reg_month, use_container_width=True)
        fig = px.line(reg_month, x="registration_month", y="total_registrations")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Monthly Registrations error: {e}")

    try:
        att_country = run_query(metrics_sql["Attendance CC by Country"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        st.markdown("#### Attendance by Country (Leads with CC)")
        st.dataframe(att_country, use_container_width=True)
        fig = px.bar(att_country.head(25), x="country", y="total_students_attended", text="total_students_attended")
        fig.update_traces(textposition="outside"); st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Attendance by Country error: {e}")

    try:
        total_att = run_query(metrics_sql["Total Students Attended (Leads)"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        st.caption(f"Total Students Attended (any lead): {int(total_att.iloc[0,0]) if not total_att.empty else 0:,}")
    except Exception as e:
        st.warning(f"Total Students Attended error: {e}")

    try:
        lessonwise = run_query(metrics_sql["Lesson-wise Attendance Per Course (Leads)"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        st.markdown("#### Lesson-wise Attendance Per Course")
        st.dataframe(lessonwise.head(100), use_container_width=True)
    except Exception as e:
        st.warning(f"Lesson-wise Attendance error: {e}")

    try:
        mostwatched = run_query(metrics_sql["Most Watched Lesson Per Course (Leads)"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        st.markdown("#### Most Watched Lesson Per Course")
        st.dataframe(mostwatched.head(100), use_container_width=True)
    except Exception as e:
        st.warning(f"Most Watched Lesson error: {e}")

    try:
        avg_watch = run_query(metrics_sql["Average Watch Time Per Lesson Per Course (Leads)"], start_date=start_date.isoformat(), end_date=end_date.isoformat())
        st.markdown("#### Average Watch Time (mins) Per Lesson Per Course")
        st.dataframe(avg_watch.head(100), use_container_width=True)
    except Exception as e:
        st.warning(f"Average Watch Time error: {e}")

    # Download cohort dataset
    st.markdown("### ⬇️ Download Cohort Dataset")
    st.download_button(
        "Download Cohort CSV",
        data=cohort_df.to_csv(index=False).encode("utf-8"),
        file_name="cohort_lead_cc_purchase_activity.csv",
        mime="text/csv",
    )


# =============================
# TAB 6 — Key Metrics (Uploaded Email Cohort)
# =============================
with tab7:
    st.subheader("📊 Key Metrics (Uploaded Email Cohort)")

    emails = (
        lp_df["Customer Email"]
        .dropna()
        .str.strip()
        .str.lower()
        .drop_duplicates()
    )

    if emails.empty:
        st.warning("No valid emails in uploaded file.")
        st.stop()

    try:
        conn = psycopg2.connect(
            host="misreporting.cxgsxkol4p2y.eu-west-1.redshift.amazonaws.com",
            port=5439,
            dbname="misreportingdb",
            user="etluser",
            password="Etluser12345"
        )
        conn.autocommit = False
        cur = conn.cursor()

        # 1) Temp table for emails
        cur.execute("CREATE TEMP TABLE IF NOT EXISTS input_emails (email_address VARCHAR(320));")
        cur.execute("TRUNCATE TABLE input_emails;")
        records = [(e,) for e in emails.tolist()]
        for i in range(0, len(records), 1000):
            chunk = records[i:i+1000]
            args_str = ",".join(cur.mogrify("(%s)", r).decode("utf-8") for r in chunk)
            cur.execute("INSERT INTO input_emails (email_address) VALUES " + args_str)

        # 2) Inline SQL for Tab 6 metrics
        sql_tab7 = """
        WITH ds AS (
            SELECT
                student_id,
                LOWER(TRIM(email_address)) AS email_address,
                created_date AS lead_created_date
            FROM data_warehouse.dim_students
             WHERE ds.created_date BETWEEN '{start_date}' AND '{end_date}'
            and LOWER(TRIM(email_address)) IN (SELECT email_address FROM input_emails)
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
        ),
        assignments AS (
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
        SELECT
            ds.student_id,
            ds.email_address,
            ds.lead_created_date,
            cc.cc_date,
            fp.first_purchase_date,
            DATEDIFF('day', cc.cc_date, fp.first_purchase_date) AS days_cc_to_purchase,
            COALESCE(att.attended_sessions, 0) AS attended_sessions,
            COALESCE(asg.assignments_completed, 0) AS assignments_completed,
            COALESCE(asg.assignments_clicked, 0) AS assignments_clicked,
            COALESCE(ps.prior_subscriptions, 0) AS prior_subscriptions
        FROM ds
        LEFT JOIN cc ON cc.student_id = ds.student_id
        LEFT JOIN first_purchase fp ON fp.student_id = ds.student_id
        LEFT JOIN prior_subs ps ON ps.student_id = ds.student_id
        LEFT JOIN attendance att ON att.student_id = ds.student_id
        LEFT JOIN assignments asg ON asg.student_id = ds.student_id;
        """

        # 3) Run query
        df_tab7 = pd.read_sql(sql_tab7, conn)

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

    # --- Display Metrics ---
    if df_tab7.empty:
        st.info("No data returned for Tab 6 in the selected date range.")
    else:
        avg_days = df_tab7["days_cc_to_purchase"].dropna()
        st.metric("Avg Days CC → Purchase", f"{avg_days.mean():.1f}" if not avg_days.empty else "—")

        avg_att = df_tab7["attended_sessions"].mean()
        st.metric("Avg Attendance Sessions", f"{avg_att:.2f}")

        st.metric("Assignments Completed", f"{int(df_tab7['assignments_completed'].sum()):,}")
        st.metric("Assignments Clicked", f"{int(df_tab7['assignments_clicked'].sum()):,}")

        st.metric("Prior Subscriptions", f"{int(df_tab7['prior_subscriptions'].sum()):,}")

        st.markdown("### Preview Data")
        st.dataframe(df_tab7.head(50), use_container_width=True)

        st.download_button(
            "⬇️ Download Tab 6 Dataset",
            data=df_tab7.to_csv(index=False).encode("utf-8"),
            file_name="tab6_metrics.csv",
            mime="text/csv",
        )

    st.subheader("📊 Key Metrics")

    if 'out' not in locals() or out.empty:
        st.warning("No merged dataset available. Please upload data in Tab 1.")
    else:
        # ---- Time difference CC → Purchase ----
        if {"cc_date", "first_purchase_date"}.issubset(out.columns):
            out["cc_date"] = pd.to_datetime(out["cc_date"], errors="coerce")
            out["first_purchase_date"] = pd.to_datetime(out["first_purchase_date"], errors="coerce")
            out["days_cc_to_purchase"] = (out["first_purchase_date"] - out["cc_date"]).dt.days
            avg_days = out["days_cc_to_purchase"].dropna()
            st.metric("Avg Days CC → Purchase", f"{avg_days.mean():.1f}" if not avg_days.empty else "—")
            st.caption(f"Based on {avg_days.count():,} rows with both CC and purchase dates.")
        else:
            st.info("CC date / First purchase date columns not found in merged dataset.")

        # ---- Attendance ----
        if "attended_sessions" in out.columns:
            avg_att = out["attended_sessions"].mean()
            st.metric("Avg Attendance Sessions", f"{avg_att:.2f}")
            st.caption(f"Total sessions attended: {out['attended_sessions'].sum():,}")
        else:
            st.info("No attendance data available in merged dataset.")

        # ---- Assignment Activity ----
        if {"assignments_completed", "assignments_clicked"}.issubset(out.columns):
            total_completed = out["assignments_completed"].sum()
            total_clicked = out["assignments_clicked"].sum()
            st.metric("Assignments Completed", f"{int(total_completed):,}")
            st.metric("Assignments Clicked", f"{int(total_clicked):,}")
        else:
            st.info("No assignment activity columns available in merged dataset.")

        # ---- Prior Subscription Payments ----
        if "prior_subscriptions" in out.columns:
            total_prior_subs = out["prior_subscriptions"].sum()
            st.metric("Prior Subscriptions", f"{int(total_prior_subs):,}")
            st.caption("Sum of subscriptions before CC date.")
        else:
            st.info("No prior subscription data available in merged dataset.")
