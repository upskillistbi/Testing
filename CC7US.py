import streamlit as st
import pandas as pd
import psycopg2
import plotly.graph_objs as go
import datetime
import numpy as np

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="Impact Tracking: Leads vs Qualified CCs", layout="wide")
st.title("📈 Impact Tracking Dashboard (Leads vs Qualified CCs) – US, CC7")

# ---------- DB Connection ----------
def run_query(query, params=None):
    conn = psycopg2.connect(
        host="misreporting.cxgsxkol4p2y.eu-west-1.redshift.amazonaws.com",
        port=5439,
        dbname="misreportingdb",
        user="etluser",
        password="Etluser12345"
    )
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# ---------- Date & Granularity Filters ----------
min_date = datetime.date(2022, 1, 1)
max_date = datetime.date.today()
st.sidebar.header("Filters")
start_date, end_date = st.sidebar.date_input(
    "Select date range:",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)
start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
granularity = st.sidebar.radio("Time Granularity:", ["Day", "Week", "Month"], horizontal=True)
if granularity == "Day":
    time_col_sql = "DATE(ds.created_date)"
elif granularity == "Week":
    time_col_sql = "DATE_TRUNC('week', ds.created_date)"
else:  # Month
    time_col_sql = "DATE_TRUNC('month', ds.created_date)"

# ---------- SQL Query ----------
query = f"""
SELECT
    {time_col_sql} AS time_period,
    COUNT(DISTINCT ds.student_id) AS leads,
    COUNT(DISTINCT cs.value__meta_data_lead_id) AS qualified_ccs
FROM data_warehouse.dim_students ds
LEFT JOIN data_marts.combined_subscriptions cs
    ON ds.student_id = cs.value__meta_data_lead_id
    AND cs.value__meta_data_lead_id IS NOT NULL
WHERE ds.created_date BETWEEN %s AND %s
  AND (LOWER(ds.country) LIKE '%%us%%' OR LOWER(ds.country) LIKE '%%united%%')
  AND LOWER(ds.offer_type) = 'cc7'
GROUP BY 1
ORDER BY 1;
"""
params = [start_date, end_date]
df = run_query(query, params)

# ---------- Data Prep ----------
df['time_period'] = pd.to_datetime(df['time_period'])
df = df.sort_values('time_period')
df['conversion_rate'] = np.where(df['leads'] > 0, df['qualified_ccs'] / df['leads'], 0)

# ---------- Today/Yesterday/Last 7d Stats ----------
if granularity == "Day":
    df = df.sort_values('time_period').reset_index(drop=True)
    if len(df) >= 2:
        last_day = df.iloc[-1]['time_period']
        prev_day = df.iloc[-2]['time_period']
        leads_last = int(df.iloc[-1]['leads'])
        qccs_last = int(df.iloc[-1]['qualified_ccs'])
        conv_last = df.iloc[-1]['conversion_rate'] * 100

        leads_prev = int(df.iloc[-2]['leads'])
        qccs_prev = int(df.iloc[-2]['qualified_ccs'])
        conv_prev = df.iloc[-2]['conversion_rate'] * 100

        leads_delta = leads_last - leads_prev
        qccs_delta = qccs_last - qccs_prev
        conv_delta = conv_last - conv_prev

    else:
        leads_last = qccs_last = conv_last = leads_prev = qccs_prev = conv_prev = leads_delta = qccs_delta = conv_delta = 0
        last_day = prev_day = None

    leads_7d = int(df.tail(7)['leads'].sum())
    cc_7d = int(df.tail(7)['qualified_ccs'].sum())
    conv_7d = (cc_7d / leads_7d * 100) if leads_7d > 0 else 0

    st.header("🚀 Latest 2 Days Campaign Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        f"Leads ({last_day.strftime('%d-%b') if last_day is not None else '-'})", leads_last,
        delta=f"{leads_delta:+}", delta_color="inverse"
    )
    c2.metric(
        f"Qualified CCs ({last_day.strftime('%d-%b') if last_day is not None else '-'})", qccs_last,
        delta=f"{qccs_delta:+}", delta_color="inverse"
    )
    c3.metric(
        f"Conversion Rate ({last_day.strftime('%d-%b') if last_day is not None else '-'})",
        f"{conv_last:.1f}%",
        delta=f"{conv_delta:+.1f}%", delta_color="inverse"
    )
    c4.metric("Conversion Rate (7d avg)", f"{conv_7d:.1f}%")

    if last_day is not None and prev_day is not None:
        st.caption(f"Comparing {last_day.strftime('%d-%b-%Y')} vs {prev_day.strftime('%d-%b-%Y')}")
elif granularity == "Week":
    last = df.tail(1)
    leads_last = int(last['leads'].values[0]) if not last.empty else 0
    qccs_last = int(last['qualified_ccs'].values[0]) if not last.empty else 0
    conv_last = last['conversion_rate'].values[0]*100 if not last.empty else 0
    prev = df.tail(2).head(1)
    conv_prev = prev['conversion_rate'].values[0]*100 if not prev.empty else 0
    conv_change = conv_last - conv_prev
    st.header("📅 Last Week Campaign Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Leads (last week)", leads_last)
    c2.metric("Qualified CCs (last week)", qccs_last)
    c3.metric("Conversion Rate (last week)", f"{conv_last:.1f}%", delta=f"{conv_change:+.1f}% vs prev week")
else:
    last = df.tail(1)
    leads_last = int(last['leads'].values[0]) if not last.empty else 0
    qccs_last = int(last['qualified_ccs'].values[0]) if not last.empty else 0
    conv_last = last['conversion_rate'].values[0]*100 if not last.empty else 0
    prev = df.tail(2).head(1)
    conv_prev = prev['conversion_rate'].values[0]*100 if not prev.empty else 0
    conv_change = conv_last - conv_prev
    st.header("🗓️ Last Month Campaign Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Leads (last month)", leads_last)
    c2.metric("Qualified CCs (last month)", qccs_last)
    c3.metric("Conversion Rate (last month)", f"{conv_last:.1f}%", delta=f"{conv_change:+.1f}% vs prev month")

# ---------- Combined Line Chart with Secondary Axis ----------
st.subheader(f"📊 Leads, Qualified CCs & Conversion Rate by {granularity}")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['time_period'], y=df['leads'],
    mode='lines+markers',
    name='Leads (Registrations)',
    line=dict(color='royalblue', width=3)
))
fig.add_trace(go.Scatter(
    x=df['time_period'], y=df['qualified_ccs'],
    mode='lines+markers',
    name='Qualified CCs',
    line=dict(color='orange', width=3)
))
fig.add_trace(go.Scatter(
    x=df['time_period'],
    y=df['conversion_rate'] * 100,
    mode='lines+markers',
    name='Conversion Rate (%)',
    yaxis='y2',
    line=dict(color='green', width=2, dash='dot')
))
fig.update_layout(
    xaxis=dict(title=granularity),
    yaxis=dict(title='Count', side='left'),
    yaxis2=dict(title='Conversion Rate (%)', overlaying='y', side='right', tickformat='.0f'),
    legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0)', bordercolor='rgba(0,0,0,0)'),
    hovermode='x unified',
    title=f"Leads vs Qualified CCs and Conversion Rate by {granularity}"
)
for i, row in df.iterrows():
    percent = row['conversion_rate'] * 100 if row['leads'] > 0 else 0
    fig.add_annotation(
        x=row['time_period'],
        y=row['qualified_ccs'],
        text=f"{percent:.1f}%",
        showarrow=False,
        yshift=15,
        font=dict(size=10, color="green")
    )
if granularity == "Day":
    fig.update_xaxes(dtick="D1", tickformat="%d-%b")
elif granularity == "Week":
    fig.update_xaxes(dtick="M1", tickformat="%b %d")
else:
    fig.update_xaxes(dtick="M1", tickformat="%b %Y")
st.plotly_chart(fig, use_container_width=True)

# ---------- Show Data Table ----------
with st.expander("🔎 Show Data Table"):
    st.dataframe(df, use_container_width=True)

# ---------- Quick Stats ----------
st.subheader("💡 Quick Stats")
st.markdown(f"- **Total Leads (in range):** {df['leads'].sum():,}")
st.markdown(f"- **Total Qualified CCs (in range):** {df['qualified_ccs'].sum():,}")
st.markdown(f"- **Average Conversion Rate:** {df['conversion_rate'].mean() * 100:.2f}%")
st.caption("Filters: Offer Type = CC7, Country = US/United States, from 2022 onward")

# ---------- Bar Chart: Leads, Qualified CCs, and Conversion Rate by UTM Source ----------
st.subheader("📊 Leads, Qualified CCs & Conversion Rate by UTM Source")

utm_query = f"""
SELECT
    LOWER(ds.utm_source) AS utm_source,
    COUNT(DISTINCT ds.student_id) AS leads,
    COUNT(DISTINCT cs.value__meta_data_lead_id) AS qualified_ccs
FROM data_warehouse.dim_students ds
LEFT JOIN data_marts.combined_subscriptions cs
    ON ds.student_id = cs.value__meta_data_lead_id
    AND cs.value__meta_data_lead_id IS NOT NULL
WHERE ds.created_date BETWEEN %s AND %s
  AND (LOWER(ds.country) LIKE '%%us%%' OR LOWER(ds.country) LIKE '%%united%%')
  AND LOWER(ds.offer_type) = 'cc7'
GROUP BY 1
ORDER BY 2 DESC;
"""
utm_df = run_query(utm_query, params)
utm_df['utm_source'] = utm_df['utm_source'].fillna('unknown')
utm_df['conversion_rate'] = utm_df['qualified_ccs'] / utm_df['leads']

bar1 = go.Figure()
bar1.add_trace(go.Bar(
    x=utm_df['utm_source'],
    y=utm_df['leads'],
    name='Leads',
    marker_color='royalblue'
))
bar1.add_trace(go.Bar(
    x=utm_df['utm_source'],
    y=utm_df['qualified_ccs'],
    name='Qualified CCs',
    marker_color='orange'
))
bar1.add_trace(go.Scatter(
    x=utm_df['utm_source'],
    y=utm_df['conversion_rate']*100,
    name='Conversion Rate (%)',
    mode='lines+markers',
    yaxis='y2',
    line=dict(color='green', dash='dot')
))
bar1.update_layout(
    barmode='group',
    yaxis=dict(title='Count'),
    yaxis2=dict(title='Conversion Rate (%)', overlaying='y', side='right', tickformat='.0f'),
    title='Leads, Qualified CCs & Conversion Rate by UTM Source'
)
st.plotly_chart(bar1, use_container_width=True)

# ---------- Bar Chart: Leads, Qualified CCs, and Conversion Rate by Partner Identifier ----------
st.subheader("📊 Leads, Qualified CCs & Conversion Rate by Partner Identifier")
# --- Color-coded Table: UTM Source ---
def color_utm_table(val, column):
    if column == 'conversion_rate':
        # Green = good, Red = bad (higher is better)
        color = f"background-color: {'#d4edda' if val > 0.4 else ('#f8d7da' if val < 0.2 else '#fff3cd')}"
        return color
    elif column == 'leads':
        color = f"background-color: {'#cfe2ff' if val > 25 else ''}"
        return color
    elif column == 'qualified_ccs':
        color = f"background-color: {'#ffe5b4' if val > 10 else ''}"
        return color
    else:
        return ""
        
def utm_highlight(s):
    return [
        color_utm_table(v, col)
        for v, col in zip(s, s.index)
    ]

st.markdown("#### 📋 Data Table: Leads, Qualified CCs & Conversion Rate by UTM Source")
utm_table = utm_df.copy()
utm_table['conversion_rate'] = utm_table['conversion_rate'] * 100
utm_table = utm_table.rename(columns={"leads": "Leads", "qualified_ccs": "Qualified CCs", "conversion_rate": "Conversion Rate (%)"})
styled_utm = utm_table.style.apply(utm_highlight, axis=1)
st.dataframe(styled_utm, use_container_width=True)

partner_query = f"""
SELECT
    LOWER(ds.profile__partner_identifier) AS partner_identifier,
    COUNT(DISTINCT ds.student_id) AS leads,
    COUNT(DISTINCT cs.value__meta_data_lead_id) AS qualified_ccs
FROM data_warehouse.dim_students ds
LEFT JOIN data_marts.combined_subscriptions cs
    ON ds.student_id = cs.value__meta_data_lead_id
    AND cs.value__meta_data_lead_id IS NOT NULL
WHERE ds.created_date BETWEEN %s AND %s
  AND (LOWER(ds.country) LIKE '%%us%%' OR LOWER(ds.country) LIKE '%%united%%')
  AND LOWER(ds.offer_type) = 'cc7'
GROUP BY 1
ORDER BY 2 DESC;
"""
partner_df = run_query(partner_query, params)
partner_df['partner_identifier'] = partner_df['partner_identifier'].fillna('unknown')
partner_df['conversion_rate'] = partner_df['qualified_ccs'] / partner_df['leads']
# --- Color-coded Table: Partner Identifier ---
def color_partner_table(val, column):
    if column == 'conversion_rate':
        color = f"background-color: {'#d4edda' if val > 0.4 else ('#f8d7da' if val < 0.2 else '#fff3cd')}"
        return color
    elif column == 'leads':
        color = f"background-color: {'#cfe2ff' if val > 25 else ''}"
        return color
    elif column == 'qualified_ccs':
        color = f"background-color: {'#ffe5b4' if val > 10 else ''}"
        return color
    else:
        return ""
        
def partner_highlight(s):
    return [
        color_partner_table(v, col)
        for v, col in zip(s, s.index)
    ]

st.markdown("#### 📋 Data Table: Leads, Qualified CCs & Conversion Rate by Partner Identifier")
partner_table = partner_df.copy()
partner_table['conversion_rate'] = partner_table['conversion_rate'] * 100
partner_table = partner_table.rename(columns={"leads": "Leads", "qualified_ccs": "Qualified CCs", "conversion_rate": "Conversion Rate (%)"})
styled_partner = partner_table.style.apply(partner_highlight, axis=1)
st.dataframe(styled_partner, use_container_width=True)

bar2 = go.Figure()
bar2.add_trace(go.Bar(
    x=partner_df['partner_identifier'],
    y=partner_df['leads'],
    name='Leads',
    marker_color='royalblue'
))
bar2.add_trace(go.Bar(
    x=partner_df['partner_identifier'],
    y=partner_df['qualified_ccs'],
    name='Qualified CCs',
    marker_color='orange'
))
bar2.add_trace(go.Scatter(
    x=partner_df['partner_identifier'],
    y=partner_df['conversion_rate']*100,
    name='Conversion Rate (%)',
    mode='lines+markers',
    yaxis='y2',
    line=dict(color='green', dash='dot')
))
bar2.update_layout(
    barmode='group',
    yaxis=dict(title='Count'),
    yaxis2=dict(title='Conversion Rate (%)', overlaying='y', side='right', tickformat='.0f'),
    title='Leads, Qualified CCs & Conversion Rate by Partner Identifier'
)
st.plotly_chart(bar2, use_container_width=True)
