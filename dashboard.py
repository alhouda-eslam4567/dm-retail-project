# ===================================================================
# DATA MINING FINAL PROJECT - INTERACTIVE DASHBOARD
# Retail Analytics Dashboard | Streamlit Application
# Student: Houda (Elhoda Eslam) | ID: 230105958
# ===================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ===================================================================
# PAGE CONFIGURATION
# ===================================================================
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================================================================
# LOAD DATA
# ===================================================================
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard_ready_data.csv", index_col=0)
    return df

df = load_data()

# ===================================================================
# SIDEBAR FILTERS
# ===================================================================
st.sidebar.title("🔍 Filters")

# Cluster filter
clusters = sorted(df['Cluster'].unique())
selected_clusters = st.sidebar.multiselect(
    "Select Customer Segments",
    options=clusters,
    default=clusters,
    help="Choose which customer clusters to display"
)

# VIP filter
show_vip_only = st.sidebar.checkbox("Show VIP Customers Only", False)

# Anomaly filter
show_anomaly_only = st.sidebar.checkbox("Show Anomaly Customers Only", False)

# Apply filters
filtered = df.copy()
filtered = filtered[filtered['Cluster'].isin(selected_clusters)]

if show_vip_only:
    filtered = filtered[filtered['IsVIP'] == 1]

if show_anomaly_only:
    filtered = filtered[filtered['IsAnomaly'] == 1]

# ===================================================================
# MAIN TITLE
# ===================================================================
st.title("📊 Retail Customer Analytics Dashboard")
st.markdown("---")

# ===================================================================
# TOP KPIs
# ===================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Total Customers", f"{len(filtered):,}")

with col2:
    avg_spending = filtered['Monetary'].mean()
    st.metric("💰 Avg Spending", f"${avg_spending:,.2f}")

with col3:
    vip_percent = (filtered['IsVIP'].sum() / len(filtered) * 100) if len(filtered) > 0 else 0
    st.metric("⭐ VIP Percentage", f"{vip_percent:.1f}%")

with col4:
    anomaly_percent = (filtered['IsAnomaly'].sum() / len(filtered) * 100) if len(filtered) > 0 else 0
    st.metric("⚠️ Anomaly Percentage", f"{anomaly_percent:.1f}%")

st.markdown("---")

# ===================================================================
# CHARTS SECTION
# ===================================================================
st.subheader("📈 Customer Analytics Visualizations")

row1_col1, row1_col2 = st.columns(2)

# Chart 1: Cluster Distribution (Bar Chart)
with row1_col1:
    cluster_counts = filtered['Cluster'].value_counts().reset_index()
    cluster_counts.columns = ['Cluster', 'Count']
    
    cluster_labels = {
        0: "Cluster 0: High-Value",
        1: "Cluster 1: At-Risk",
        2: "Cluster 2: New/Low",
        3: "Cluster 3: Regular"
    }
    cluster_counts['Cluster Name'] = cluster_counts['Cluster'].map(cluster_labels)
    
    fig1 = px.bar(
        cluster_counts,
        x='Cluster Name',
        y='Count',
        title="Customer Distribution by Segment",
        color='Cluster Name',
        color_discrete_sequence=px.colors.qualitative.Set2,
        text='Count'
    )
    fig1.update_traces(textposition='outside')
    fig1.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Anomaly Distribution (Pie Chart)
with row1_col2:
    anomaly_counts = filtered['IsAnomaly'].value_counts().reset_index()
    anomaly_counts.columns = ['Status', 'Count']
    anomaly_counts['Status'] = anomaly_counts['Status'].map({0: 'Normal Customer', 1: 'Anomaly'})
    
    fig2 = px.pie(
        anomaly_counts,
        values='Count',
        names='Status',
        title="Anomaly Detection Results",
        color='Status',
        color_discrete_map={'Normal Customer': '#2ecc71', 'Anomaly': '#e74c3c'}
    )
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig2, use_container_width=True)

# Row 2 Charts
row2_col1, row2_col2 = st.columns(2)

# Chart 3: VIP Distribution (Pie Chart)
with row2_col1:
    vip_counts = filtered['IsVIP'].value_counts().reset_index()
    vip_counts.columns = ['Status', 'Count']
    vip_counts['Status'] = vip_counts['Status'].map({0: 'Regular Customer', 1: 'VIP Customer'})
    
    fig3 = px.pie(
        vip_counts,
        values='Count',
        names='Status',
        title="VIP vs Regular Customers",
        color='Status',
        color_discrete_map={'Regular Customer': '#3498db', 'VIP Customer': '#f1c40f'}
    )
    fig3.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Scatter Plot - Recency vs Monetary
with row2_col2:
    fig4 = px.scatter(
        filtered,
        x='Recency',
        y='Monetary',
        color='Cluster',
        size='Frequency',
        hover_data=['AvgOrderValue', 'IsVIP', 'IsAnomaly'],
        title="Recency vs Monetary Spending (Size = Frequency)",
        labels={'Recency': 'Days Since Last Purchase', 'Monetary': 'Total Spending ($)'},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig4.update_layout(legend_title_text='Customer Segment')
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ===================================================================
# CUSTOMER TABLE
# ===================================================================
st.subheader("📋 Customer Data Table")

# Prepare table for display
display_cols = ['Recency', 'Frequency', 'Monetary', 'AvgOrderValue', 'Cluster', 'IsVIP', 'IsAnomaly']
display_names = {
    'Recency': 'Days Since Last Purchase',
    'Frequency': '# Purchases',
    'Monetary': 'Total Spending ($)',
    'AvgOrderValue': 'Avg Order Value ($)',
    'Cluster': 'Segment',
    'IsVIP': 'VIP Status',
    'IsAnomaly': 'Anomaly'
}

table_data = filtered[display_cols].copy()
table_data['IsVIP'] = table_data['IsVIP'].map({0: 'No', 1: 'Yes'})
table_data['IsAnomaly'] = table_data['IsAnomaly'].map({0: 'No', 1: 'Yes'})
table_data['Monetary'] = table_data['Monetary'].apply(lambda x: f"${x:,.2f}")
table_data['AvgOrderValue'] = table_data['AvgOrderValue'].apply(lambda x: f"${x:,.2f}")

st.dataframe(
    table_data,
    column_config={
        "Recency": st.column_config.NumberColumn("Days Since Last Purchase"),
        "Frequency": st.column_config.NumberColumn("# Purchases"),
        "Monetary": st.column_config.TextColumn("Total Spending"),
        "AvgOrderValue": st.column_config.TextColumn("Avg Order Value"),
        "Cluster": st.column_config.SelectboxColumn("Segment", options=[0,1,2,3]),
        "IsVIP": st.column_config.TextColumn("VIP"),
        "IsAnomaly": st.column_config.TextColumn("Anomaly")
    },
    use_container_width=True,
    height=400
)

st.markdown("---")

# ===================================================================
# BUSINESS INSIGHTS PANEL
# ===================================================================
st.subheader("💡 Business Insights Panel")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("**📌 Insight 1: Customer Segmentation**\n\n"
            "4 distinct segments identified:\n"
            "- 🟢 High-Value: Recent & frequent buyers\n"
            "- 🟡 At-Risk: Previously active, now inactive\n"
            "- 🔵 New/Low: New or infrequent customers\n"
            "- 🟣 Regular: Consistent moderate buyers\n\n"
            "**Action:** Launch targeted campaigns per segment")

with col2:
    st.success("**📌 Insight 2: VIP Identification**\n\n"
               f"⭐ VIP customers form {vip_percent:.1f}% of base\n"
               "These customers drive majority of revenue\n\n"
               "**Action:** Implement loyalty program with exclusive benefits")

with col3:
    st.warning("**📌 Insight 3: Anomaly Detection**\n\n"
               f"⚠️ {anomaly_percent:.1f}% show unusual patterns\n"
               "Includes potential fraud OR high-value VIPs\n\n"
               "**Action:** Investigate each anomaly case individually")

st.markdown("---")

# ===================================================================
# FOOTER
# ===================================================================
st.caption(f"Data Mining Final Project | Student: Houda (Elhoda Eslam) | ID: 230105958 | Data last updated")