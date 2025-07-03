import streamlit as st
import pandas as pd
import psycopg2
import numpy as np
import plotly.express as px

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="Quarterly Impact Tracking Dashboard", layout="wide")
st.title("📈 Quarterly Impact Tracking Dashboard (Leads, CCs, Conversion, Impact Metric)")

# ---------- DB Connection ----------
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

# ---------- Get Data (Tab 1: Country) ----------
sql_country = """
SELECT
    DATE_TRUNC('quarter', ds.created_date) AS quarter,
    LOWER(ds.country) AS country,
    COUNT(DISTINCT ds.student_id) AS leads,
    COUNT(DISTINCT cs.value__meta_data_lead_id) AS qualified_ccs,
    CASE WHEN COUNT(DISTINCT ds.student_id) > 0
         THEN COUNT(DISTINCT cs.value__meta_data_lead_id)::float / COUNT(DISTINCT ds.student_id)
         ELSE 0 END AS conversion_rate
FROM data_warehouse.dim_students ds
LEFT JOIN data_marts.combined_subscriptions cs
    ON ds.student_id = cs.value__meta_data_lead_id
    AND cs.value__meta_data_lead_id IS NOT NULL
WHERE ds.created_date >= '2024-01-01'
GROUP BY 1, 2
ORDER BY 1, 2;
"""




# ---------- Get Data (Tab 2: Country + UTM + Partner) ----------
sql_grouped = """
SELECT
    DATE_TRUNC('quarter', ds.created_date) AS quarter,
    LOWER(ds.country) AS country,
    LOWER(ds.utm_source) AS utm_source,
    LOWER(ds.profile__partner_identifier) AS partner_identifier,
    COUNT(DISTINCT ds.student_id) AS leads,
    COUNT(DISTINCT cs.value__meta_data_lead_id) AS qualified_ccs,
    CASE WHEN COUNT(DISTINCT ds.student_id) > 0
         THEN COUNT(DISTINCT cs.value__meta_data_lead_id)::float / COUNT(DISTINCT ds.student_id)
         ELSE 0 END AS conversion_rate
FROM data_warehouse.dim_students ds
LEFT JOIN data_marts.combined_subscriptions cs
    ON ds.student_id = cs.value__meta_data_lead_id
    AND cs.value__meta_data_lead_id IS NOT NULL
WHERE ds.created_date >= '2024-01-01'
GROUP BY 1, 2, 3, 4
ORDER BY 1, 2, 3, 4;
"""

# ---------- SQL for Cancellations Tab ----------
sql_cxl = """
WITH first_cancel_per_user AS (
    SELECT
        cs.value__meta_data_lead_id AS student_id,
        DATE_TRUNC('quarter', cs.created_at) AS quarter,
        LOWER(ds.country) AS country,
        LOWER(ds.coursepicked) AS course_picked,
        LOWER(cs.data__custom_data__cancellation_reason_code) AS cancellation_reason,
        cs.value__status,
        ROW_NUMBER() OVER (
            PARTITION BY cs.value__meta_data_lead_id, DATE_TRUNC('quarter', cs.created_at)
            ORDER BY cs.cancellation_intiated_on
        ) AS rn
    FROM data_marts.combined_subscriptions cs
    JOIN data_warehouse.dim_students ds
      ON ds.student_id = cs.value__meta_data_lead_id
    WHERE cs.value__meta_data_lead_id IS NOT NULL
      AND cs.created_at >= '2024-01-01'
)
SELECT
    quarter,
    country,
    course_picked,
    cancellation_reason,
    COUNT(DISTINCT student_id) AS qualified_ccs,
    COUNT(DISTINCT CASE WHEN value__status = 'cancelled' THEN student_id END) AS cancelled_ccs
FROM first_cancel_per_user
WHERE rn = 1
GROUP BY 1, 2, 3, 4
ORDER BY 1, 2, 3, 4;
"""
# ============== TAB 3 ==============
tab1, tab2, tab3 = st.tabs([
    "🌎 Country Level", "🌍 Country + UTM + Partner Grouping", "🚩 Cancellations Analysis"
])


# ================== TAB 1 ==================
with tab1:
    df = run_query(sql_country)
    df['quarter'] = pd.to_datetime(df['quarter'])
    group_cols = ['country']
    df = df.sort_values(group_cols + ['quarter'])

    df['growth_vs_prev_qtr'] = df.groupby(group_cols)['conversion_rate'].diff().fillna(np.nan)

    def historic_avg(x):
        return x.expanding().mean().shift(1)
    df['hist_avg_conv'] = df.groupby(group_cols)['conversion_rate'].transform(historic_avg)
    df['growth_vs_hist_avg'] = df['conversion_rate'] - df['hist_avg_conv']

    df['total_leads_in_qtr'] = df.groupby('quarter')['leads'].transform('sum')
    df['total_ccs_in_qtr'] = df.groupby('quarter')['qualified_ccs'].transform('sum')
    df['cc_share_of_total'] = df['qualified_ccs'] / df['total_ccs_in_qtr']
    df['lead_share_of_total'] = df['leads'] / df['total_leads_in_qtr']

    df['impact_metric'] = df['growth_vs_prev_qtr']

    show_cols = group_cols + [
        'quarter', 'leads', 'qualified_ccs', 'conversion_rate',
        'growth_vs_prev_qtr', 'growth_vs_hist_avg',
        'cc_share_of_total', 'lead_share_of_total', 'impact_metric'
    ]

    df_show = df[show_cols].copy()
    df_show['year'] = df_show['quarter'].dt.year
    df_show['quarter_num'] = df_show['quarter'].dt.quarter
    df_show['conversion_rate'] = df_show['conversion_rate'].map('{:.1%}'.format)
    df_show['growth_vs_prev_qtr'] = df_show['growth_vs_prev_qtr'].map('{:+.1%}'.format)
    df_show['growth_vs_hist_avg'] = df_show['growth_vs_hist_avg'].map('{:+.1%}'.format)
    df_show['cc_share_of_total'] = df_show['cc_share_of_total'].map('{:.1%}'.format)
    df_show['lead_share_of_total'] = df_show['lead_share_of_total'].map('{:.1%}'.format)
    df_show['impact_metric_display'] = df['impact_metric'].map('{:+.1%}'.format)

    df_show_recent = df_show[df_show['quarter'] >= pd.to_datetime('2024-01-01')].copy()
    df_show_recent = df_show_recent.reset_index(drop=True)

    # --- Country Search Bar ---
    search_country = st.text_input("🔎 Search Country", "")
    if search_country:
        mask = (
            df_show_recent['country'].notnull() &
            df_show_recent['country'].str.contains(search_country.strip().lower(), na=False)
        )
        df_show_recent = df_show_recent[mask]

    # --- Color-coded Table with st.dataframe ---
    def highlight_impact_column(s):
        colors = []
        for val in s:
            try:
                float_val = float(val.replace('%', '').replace('+', '').replace('nan', '0')) / 100
            except:
                float_val = 0
            if float_val > 0.01:
                colors.append('background-color: #d4edda')   # green
            elif float_val < -0.01:
                colors.append('background-color: #f8d7da')   # red
            else:
                colors.append('background-color: #ececec')   # gray
        return colors

    st.subheader("📊 Quarterly Impact Table (2024+ Only, Filtered by Country)")
    st.dataframe(
        df_show_recent.style.apply(
            highlight_impact_column, subset=['impact_metric_display'], axis=0
        ),
        use_container_width=True
    )

    # --- Chart 1: Conversion Rate Trend by Top Countries (max 5) ---
    # Get Top 5 countries by leads in latest quarter
    latest_qtr = df_show_recent['quarter'].max()
    df_latest = df_show_recent[df_show_recent['quarter'] == latest_qtr]
    top_countries = df_latest.sort_values('leads', ascending=False).head(5)['country'].tolist()

    plot_countries = df_show_recent['country'].unique() if search_country else top_countries
    df_chart = df_show_recent[df_show_recent['country'].isin(plot_countries)].copy()
    # Convert conversion_rate to float for chart
    df_chart['conversion_rate_float'] = df_chart['conversion_rate'].str.replace('%', '').astype(float) / 100

    st.subheader(f"📈 Conversion Rate Trend: Top Countries ({', '.join(plot_countries).upper()})")
    fig1 = px.line(
        df_chart,
        x="quarter",
        y="conversion_rate_float",
        color="country",
        markers=True,
        labels={"conversion_rate_float": "Conversion Rate", "quarter": "Quarter"},
        title="Conversion Rate by Country Over Time"
    )
    fig1.update_traces(mode="lines+markers")
    fig1.update_layout(yaxis_tickformat=".1%", yaxis_range=[0, 1.05])
    st.plotly_chart(fig1, use_container_width=True)

    # --- Chart 2: Impact Metric (Growth vs Prev Qtr, Latest Quarter Only) ---
    st.subheader(f"🚦 Conversion Rate Growth vs Previous Qtr (Top 10 Countries, {latest_qtr.strftime('%b %Y')})")
    top_countries_10 = df_latest.sort_values('leads', ascending=False).head(10)
    fig3 = px.bar(
        top_countries_10,
        x="country",
        y="growth_vs_prev_qtr",
        labels={"growth_vs_prev_qtr": "Growth vs Prev Qtr", "country": "Country"},
        color="growth_vs_prev_qtr",
        color_continuous_scale=["#f8d7da", "#ececec", "#d4edda"],
        title="Impact Metric by Country"
    )
    fig3.update_layout(yaxis_tickformat="+.1%")
    st.plotly_chart(fig3, use_container_width=True)

    st.caption(
        "Type a country to search above. "
        "Impact Metric: Green = conversion ↑ vs prev quarter, Red = ↓, Gray = stable (<1% abs change)."
    )

    st.markdown("""
    ---
    ### 📖 **Metric Formulas Explained**

    - **leads**  
      > Number of unique students (student_id) who registered in this segment and quarter.  
      > **Formula:**  
      > `leads = count of unique student_id`

    - **qualified_ccs**  
      > Number of unique students (student_id) who gave a credit card (qualified) in this segment and quarter.  
      > **Formula:**  
      > `qualified_ccs = count of unique student_id who gave a credit card`

    - **conversion_rate**  
      > Percentage of leads who gave a credit card.  
      > **Formula:**  
      > `conversion_rate = qualified_ccs / leads`

    - **growth_vs_prev_qtr**  
      > Change in conversion rate compared to the previous quarter for the same segment.  
      > **Formula:**  
      > `growth_vs_prev_qtr = conversion_rate (this quarter) - conversion_rate (previous quarter)`

    - **growth_vs_hist_avg**  
      > Change in conversion rate compared to the historic average (all previous quarters) for the same segment.  
      > **Formula:**  
      > `growth_vs_hist_avg = conversion_rate (this quarter) - average conversion_rate (all previous quarters)`

    - **cc_share_of_total**  
      > What % of all qualified CCs in this quarter came from this segment.  
      > **Formula:**  
      > `cc_share_of_total = qualified_ccs / total qualified_ccs in this quarter`

    - **lead_share_of_total**  
      > What % of all leads in this quarter came from this segment.  
      > **Formula:**  
      > `lead_share_of_total = leads / total leads in this quarter`

    - **impact_metric**  
      > Same as `growth_vs_prev_qtr`. Indicates whether the conversion rate is improving (green), declining (red), or stable (gray) compared to last quarter.

    ---
    """)


    # ================== TAB 1, Section A: Country + Offer Type ==================
    sql_tab1_a = """
    SELECT
        DATE_TRUNC('quarter', ds.created_date) AS quarter,
        EXTRACT(YEAR FROM ds.created_date) AS year,
        LOWER(ds.country) AS country,
        LOWER(ds.offer_type) AS offer_type,
        COUNT(DISTINCT ds.student_id) AS leads,
        COUNT(DISTINCT cs.value__meta_data_lead_id) AS qualified_ccs
    FROM data_warehouse.dim_students ds
    LEFT JOIN data_marts.combined_subscriptions cs
        ON ds.student_id = cs.value__meta_data_lead_id
        AND cs.value__meta_data_lead_id IS NOT NULL
    WHERE ds.created_date >= '2024-01-01'
    GROUP BY 1,2,3,4
    ORDER BY 1,3,4
    """
    df_tab1_a = run_query(sql_tab1_a)
    df_tab1_a['quarter'] = pd.to_datetime(df_tab1_a['quarter'])
    group_cols_a = ['country', 'offer_type']
    df_tab1_a = df_tab1_a.sort_values(['year', 'quarter'] + group_cols_a)

    # Calculated impact metrics
    df_tab1_a['conversion_rate'] = np.where(
        df_tab1_a['leads'] > 0, df_tab1_a['qualified_ccs'] / df_tab1_a['leads'], np.nan
    )
    df_tab1_a['growth_vs_prev_qtr'] = df_tab1_a.groupby(group_cols_a)['conversion_rate'].diff()
    df_tab1_a['hist_avg_conv'] = df_tab1_a.groupby(group_cols_a)['conversion_rate'].transform(lambda x: x.expanding().mean().shift(1))
    df_tab1_a['growth_vs_hist_avg'] = df_tab1_a['conversion_rate'] - df_tab1_a['hist_avg_conv']
    df_tab1_a['total_leads_in_qtr'] = df_tab1_a.groupby('quarter')['leads'].transform('sum')
    df_tab1_a['total_ccs_in_qtr'] = df_tab1_a.groupby('quarter')['qualified_ccs'].transform('sum')
    df_tab1_a['cc_share_of_total'] = np.where(
        df_tab1_a['total_ccs_in_qtr'] > 0,
        df_tab1_a['qualified_ccs'] / df_tab1_a['total_ccs_in_qtr'],
        np.nan
    )
    df_tab1_a['lead_share_of_total'] = np.where(
        df_tab1_a['total_leads_in_qtr'] > 0,
        df_tab1_a['leads'] / df_tab1_a['total_leads_in_qtr'],
        np.nan
    )

    # Format for display
    show_cols_a = [
        'year', 'quarter', 'country', 'offer_type', 'leads', 'qualified_ccs',
        'conversion_rate', 'growth_vs_prev_qtr', 'growth_vs_hist_avg',
        'cc_share_of_total', 'lead_share_of_total'
    ]
    df_tab1_a_show = df_tab1_a[show_cols_a].copy()
    for c in ['conversion_rate','growth_vs_prev_qtr','growth_vs_hist_avg','cc_share_of_total','lead_share_of_total']:
        df_tab1_a_show[c] = df_tab1_a_show[c].map('{:.1%}'.format)

    st.subheader("📋 Country + Offer Type: Quarterly Metrics")
    st.dataframe(df_tab1_a_show, use_container_width=True)

    # ---- Charts for Section A ----
    # Trend chart: Conversion Rate over time for Top 6 groups
    top_a = df_tab1_a_show.groupby(['country','offer_type'])['leads'].sum().sort_values(ascending=False).head(6).index.tolist()
    df_a_chart = df_tab1_a[df_tab1_a[['country','offer_type']].apply(tuple, axis=1).isin(top_a)]
    df_a_chart['conversion_rate_float'] = df_a_chart['conversion_rate']

    st.subheader("📈 Conversion Rate Trend: Top Country+Offer Groups")
    fig_a1 = px.line(
        df_a_chart,
        x="quarter", y="conversion_rate_float",
        color=df_a_chart[['country','offer_type']].apply(lambda x: f"{x[0]} ({x[1]})", axis=1),
        markers=True, labels={"conversion_rate_float":"Conversion Rate"},
        title="Conversion Rate Over Time (Top Groups)"
    )
    fig_a1.update_traces(mode="lines+markers")
    fig_a1.update_layout(yaxis_tickformat=".1%", yaxis_range=[0, 1.05])
    st.plotly_chart(fig_a1, use_container_width=True)

    # Bar chart: Growth vs Previous Quarter (Latest Quarter)
    latest_qtr_a = df_tab1_a['quarter'].max()
    latest_a = df_tab1_a[df_tab1_a['quarter']==latest_qtr_a].copy()
    latest_a['label'] = latest_a[['country','offer_type']].apply(lambda x: f"{x[0]} ({x[1]})", axis=1)
    latest_a = latest_a.sort_values('leads',ascending=False).head(10)
    st.subheader(f"🚦 Growth vs Previous Qtr (Top 10 Groups, {latest_qtr_a.strftime('%b %Y')})")
    fig_a2 = px.bar(
        latest_a, x='label', y='growth_vs_prev_qtr',
        labels={'growth_vs_prev_qtr':"Growth vs Prev Qtr", 'label':"Country + Offer"},
        color='growth_vs_prev_qtr',
        color_continuous_scale=["#f8d7da", "#ececec", "#d4edda"]
    )
    fig_a2.update_layout(yaxis_tickformat="+.1%")
    st.plotly_chart(fig_a2, use_container_width=True)


    # ================== TAB 1, Section B: Country + Offer + UTM + Partner ==================
    sql_tab1_b = """
    SELECT
        DATE_TRUNC('quarter', ds.created_date) AS quarter,
        EXTRACT(YEAR FROM ds.created_date) AS year,
        LOWER(ds.country) AS country,
        LOWER(ds.offer_type) AS offer_type,
        LOWER(ds.utm_source) AS utm_source,
        LOWER(ds.profile__partner_identifier) AS partner_identifier,
        COUNT(DISTINCT ds.student_id) AS leads,
        COUNT(DISTINCT cs.value__meta_data_lead_id) AS qualified_ccs
    FROM data_warehouse.dim_students ds
    LEFT JOIN data_marts.combined_subscriptions cs
        ON ds.student_id = cs.value__meta_data_lead_id
        AND cs.value__meta_data_lead_id IS NOT NULL
    WHERE ds.created_date >= '2024-01-01'
    GROUP BY 1,2,3,4,5,6
    ORDER BY 1,3,4,5,6
    """
    df_tab1_b = run_query(sql_tab1_b)
    df_tab1_b['quarter'] = pd.to_datetime(df_tab1_b['quarter'])
    group_cols_b = ['country', 'offer_type', 'utm_source', 'partner_identifier']
    df_tab1_b = df_tab1_b.sort_values(['year', 'quarter'] + group_cols_b)

    df_tab1_b['conversion_rate'] = np.where(
        df_tab1_b['leads'] > 0, df_tab1_b['qualified_ccs'] / df_tab1_b['leads'], np.nan
    )
    df_tab1_b['growth_vs_prev_qtr'] = df_tab1_b.groupby(group_cols_b)['conversion_rate'].diff()
    df_tab1_b['hist_avg_conv'] = df_tab1_b.groupby(group_cols_b)['conversion_rate'].transform(lambda x: x.expanding().mean().shift(1))
    df_tab1_b['growth_vs_hist_avg'] = df_tab1_b['conversion_rate'] - df_tab1_b['hist_avg_conv']
    df_tab1_b['total_leads_in_qtr'] = df_tab1_b.groupby('quarter')['leads'].transform('sum')
    df_tab1_b['total_ccs_in_qtr'] = df_tab1_b.groupby('quarter')['qualified_ccs'].transform('sum')
    df_tab1_b['cc_share_of_total'] = np.where(
        df_tab1_b['total_ccs_in_qtr'] > 0,
        df_tab1_b['qualified_ccs'] / df_tab1_b['total_ccs_in_qtr'],
        np.nan
    )
    df_tab1_b['lead_share_of_total'] = np.where(
        df_tab1_b['total_leads_in_qtr'] > 0,
        df_tab1_b['leads'] / df_tab1_b['total_leads_in_qtr'],
        np.nan
    )

    show_cols_b = [
        'year', 'quarter', 'country', 'offer_type', 'utm_source', 'partner_identifier',
        'leads', 'qualified_ccs', 'conversion_rate', 'growth_vs_prev_qtr',
        'growth_vs_hist_avg', 'cc_share_of_total', 'lead_share_of_total'
    ]
    df_tab1_b_show = df_tab1_b[show_cols_b].copy()
    for c in ['conversion_rate','growth_vs_prev_qtr','growth_vs_hist_avg','cc_share_of_total','lead_share_of_total']:
        df_tab1_b_show[c] = df_tab1_b_show[c].map('{:.1%}'.format)

    st.subheader("📋 Country + Offer + UTM + Partner: Quarterly Metrics")
    st.dataframe(df_tab1_b_show, use_container_width=True)

    # Charts for Section B
    # Line: Conversion rate trend for top 6 (by leads) groupings
    top_b = df_tab1_b_show.groupby(['country','offer_type','utm_source','partner_identifier'])['leads'].sum().sort_values(ascending=False).head(6).index.tolist()
    df_b_chart = df_tab1_b[df_tab1_b[group_cols_b].apply(tuple, axis=1).isin(top_b)]
    df_b_chart['conversion_rate_float'] = df_b_chart['conversion_rate']

    st.subheader("📈 Conversion Rate Trend: Top Detailed Groups")
    fig_b1 = px.line(
        df_b_chart,
        x="quarter", y="conversion_rate_float",
        color=df_b_chart[group_cols_b].apply(lambda x: f"{x[0]} ({x[1]}, {x[2]}, {x[3]})", axis=1),
        markers=True, labels={"conversion_rate_float":"Conversion Rate"},
        title="Conversion Rate Over Time (Top Groups)"
    )
    fig_b1.update_traces(mode="lines+markers")
    fig_b1.update_layout(yaxis_tickformat=".1%", yaxis_range=[0, 1.05])
    st.plotly_chart(fig_b1, use_container_width=True)

    # Bar chart: Growth vs Previous Quarter (Latest Quarter)
    latest_qtr_b = df_tab1_b['quarter'].max()
    latest_b = df_tab1_b[df_tab1_b['quarter']==latest_qtr_b].copy()
    latest_b['label'] = latest_b[group_cols_b].apply(lambda x: f"{x[0]} ({x[1]}, {x[2]}, {x[3]})", axis=1)
    latest_b = latest_b.sort_values('leads',ascending=False).head(10)
    st.subheader(f"🚦 Growth vs Previous Qtr (Top 10 Detailed Groups, {latest_qtr_b.strftime('%b %Y')})")
    fig_b2 = px.bar(
        latest_b, x='label', y='growth_vs_prev_qtr',
        labels={'growth_vs_prev_qtr':"Growth vs Prev Qtr", 'label':"Country + Offer + UTM + Partner"},
        color='growth_vs_prev_qtr',
        color_continuous_scale=["#f8d7da", "#ececec", "#d4edda"]
    )
    fig_b2.update_layout(yaxis_tickformat="+.1%")
    st.plotly_chart(fig_b2, use_container_width=True)

# ================== TAB 2 ==================
with tab2:
    df2 = run_query(sql_grouped)
    df2['quarter'] = pd.to_datetime(df2['quarter'])
    group_cols2 = ['country', 'utm_source', 'partner_identifier']
    df2 = df2.sort_values(group_cols2 + ['quarter'])

    df2['growth_vs_prev_qtr'] = df2.groupby(group_cols2)['conversion_rate'].diff().fillna(np.nan)
    df2['hist_avg_conv'] = df2.groupby(group_cols2)['conversion_rate'].transform(lambda x: x.expanding().mean().shift(1))
    df2['growth_vs_hist_avg'] = df2['conversion_rate'] - df2['hist_avg_conv']

    df2['total_leads_in_qtr'] = df2.groupby('quarter')['leads'].transform('sum')
    df2['total_ccs_in_qtr'] = df2.groupby('quarter')['qualified_ccs'].transform('sum')
    df2['cc_share_of_total'] = df2['qualified_ccs'] / df2['total_ccs_in_qtr']
    df2['lead_share_of_total'] = df2['leads'] / df2['total_leads_in_qtr']

    df2['impact_metric'] = df2['growth_vs_prev_qtr']

    show_cols2 = group_cols2 + [
        'quarter', 'leads', 'qualified_ccs', 'conversion_rate',
        'growth_vs_prev_qtr', 'growth_vs_hist_avg',
        'cc_share_of_total', 'lead_share_of_total', 'impact_metric'
    ]

    df2_show = df2[show_cols2].copy()
    df2_show['year'] = df2_show['quarter'].dt.year
    df2_show['quarter_num'] = df2_show['quarter'].dt.quarter
    df2_show['conversion_rate'] = df2_show['conversion_rate'].map('{:.1%}'.format)
    df2_show['growth_vs_prev_qtr'] = df2_show['growth_vs_prev_qtr'].map('{:+.1%}'.format)
    df2_show['growth_vs_hist_avg'] = df2_show['growth_vs_hist_avg'].map('{:+.1%}'.format)
    df2_show['cc_share_of_total'] = df2_show['cc_share_of_total'].map('{:.1%}'.format)
    df2_show['lead_share_of_total'] = df2_show['lead_share_of_total'].map('{:.1%}'.format)
    df2_show['impact_metric_display'] = df2['impact_metric'].map('{:+.1%}'.format)

    df2_show_recent = df2_show[df2_show['quarter'] >= pd.to_datetime('2024-01-01')].copy()
    df2_show_recent = df2_show_recent.reset_index(drop=True)

    st.subheader("📊 Quarterly Grouped Impact Table (2024+)")
    st.dataframe(
        df2_show_recent.style.apply(
            highlight_impact_column, subset=['impact_metric_display'], axis=0
        ),
        use_container_width=True
    )

    st.markdown("""
    ---
    **Grouping:** quarter, country, utm_source, partner_identifier  
    All impact/coversion metrics calculated at this group level.  
    Use table filters/search to slice further!
    ---
    """)


with tab3:
    df3 = run_query(sql_cxl)
    df3['quarter'] = pd.to_datetime(df3['quarter'])
    group_cols3 = ['country', 'cancellation_reason', 'course_picked']
    df3 = df3.sort_values(group_cols3 + ['quarter'])

    # Add derived metrics (all denominators now 'qualified_ccs')
    df3['cancellation_rate'] = df3['cancelled_ccs'] / df3['qualified_ccs']
    df3['change_vs_prev_qtr'] = df3.groupby(group_cols3)['cancellation_rate'].diff()
    df3['hist_avg_cxl'] = df3.groupby(group_cols3)['cancellation_rate'].transform(lambda x: x.expanding().mean().shift(1))
    df3['change_vs_hist_avg'] = df3['cancellation_rate'] - df3['hist_avg_cxl']
    df3['total_cxl_in_qtr'] = df3.groupby('quarter')['cancelled_ccs'].transform('sum')
    df3['share_of_cxl'] = df3['cancelled_ccs'] / df3['total_cxl_in_qtr']

    # Format for display
    display_cols3 = group_cols3 + [
        'quarter', 'qualified_ccs', 'cancelled_ccs', 'cancellation_rate',
        'change_vs_prev_qtr', 'change_vs_hist_avg', 'share_of_cxl'
    ]
    df3_show = df3[display_cols3].copy()
    df3_show['cancellation_rate'] = df3_show['cancellation_rate'].map('{:.1%}'.format)
    df3_show['change_vs_prev_qtr'] = df3_show['change_vs_prev_qtr'].map('{:+.1%}'.format)
    df3_show['change_vs_hist_avg'] = df3_show['change_vs_hist_avg'].map('{:+.1%}'.format)
    df3_show['share_of_cxl'] = df3_show['share_of_cxl'].map('{:.1%}'.format)

    st.subheader("🚩 Quarterly Cancellations Table (2024+)")
    st.dataframe(df3_show, use_container_width=True)

    # Chart: Top Cancellation Reasons (latest quarter)
    latest_qtr3 = df3_show['quarter'].max()
    top_cxl = df3_show[df3_show['quarter'] == latest_qtr3].groupby('cancellation_reason')['cancelled_ccs'].sum().sort_values(ascending=False).head(10)
    st.subheader(f"🔝 Top 10 Cancellation Reasons ({latest_qtr3.strftime('%b %Y')})")
    fig_cxl = px.bar(
        x=top_cxl.index,
        y=top_cxl.values,
        labels={'x': 'Cancellation Reason', 'y': 'Cancellations'},
        title="Top 10 Cancellation Reasons"
    )
    st.plotly_chart(fig_cxl, use_container_width=True)



