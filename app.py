import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Zomato Analytics", layout="wide")

# -----------------------------
# Custom Styling
# -----------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #1e1e2f, #111827);
}
div[data-testid="metric-container"] {
    background-color: #1f2937;
    border: 1px solid #374151;
    padding: 15px;
    border-radius: 12px;
}
h1 {
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🍽 Zomato Restaurant Analytics Dashboard")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Zomato_Data.csv")
    df = df.drop('Unnamed: 0', axis=1)
    df = df.rename(columns={'approx_cost(for two people)': 'approx_cost'})
    df = df.fillna(0)

    df.approx_cost = df.approx_cost.replace('[,]', '', regex=True).astype('int64')
    df.rate = df.rate.replace('-', 0)
    df.rate = df.rate.replace('NEW', 0)
    df.rate = df.rate.replace('[/5]', '', regex=True).astype('float64')

    return df

df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔎 Filter Panel")

location = st.sidebar.selectbox(
    "Select Location",
    sorted(df['location'].unique())
)

filtered_df = df[df['location'] == location]

restaurant = st.sidebar.selectbox(
    "Select Restaurant",
    sorted(filtered_df['name'].unique())
)

rest_df = filtered_df[filtered_df['name'] == restaurant]

# -----------------------------
# KPI Cards
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("⭐ Rating", round(rest_df['rate'].mean(), 2))
col2.metric("🗳 Votes", int(rest_df['votes'].sum()))
col3.metric("💰 Avg Cost", int(rest_df['approx_cost'].mean()))

st.divider()

# -----------------------------
# GRAPH SECTION (Side by Side)
# -----------------------------
g1, g2 = st.columns(2)

# 1️⃣ Top 10 Costly Restaurants (Vertical Bar)
top_cost = (
    filtered_df.groupby('name')['approx_cost']
    .mean()
    .nlargest(10)
    .reset_index()
)

fig1 = px.bar(
    top_cost,
    x='name',
    y='approx_cost',
    color='approx_cost',
    color_continuous_scale='tealgrn',
)

fig1.update_layout(
    title="Top 10 Costly Restaurants",
    xaxis_title="Restaurant Name",
    yaxis_title="Average Cost",
    xaxis_tickangle=-45,
    height=450,
    template="plotly_dark"
)

g1.plotly_chart(fig1, use_container_width=True)

# 2️⃣ Most Popular Restaurant Types
rest_type_count = (
    filtered_df['rest_type']
    .value_counts()
    .nlargest(10)
    .reset_index()
)

rest_type_count.columns = ['rest_type', 'count']

fig2 = px.bar(
    rest_type_count,
    x='rest_type',
    y='count',
    color='count',
    color_continuous_scale='blues',
)

fig2.update_layout(
    title="Most Popular Restaurant Types",
    xaxis_title="Restaurant Type",
    yaxis_title="Count",
    xaxis_tickangle=-45,
    height=450,
    template="plotly_dark"
)

g2.plotly_chart(fig2, use_container_width=True)
