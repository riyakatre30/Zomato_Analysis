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
h1, h2, h3 {
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
# KPI CARDS (Restaurant Level)
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("⭐ Rating", round(rest_df['rate'].mean(), 2))
col2.metric("🗳 Total Votes", int(rest_df['votes'].sum()))
col3.metric("💰 Avg Cost for Two", int(rest_df['approx_cost'].mean()))

st.divider()

# -----------------------------
# 📍 LOCATION LEVEL ANALYSIS
# -----------------------------
st.subheader("📍 Location Wise Cost Analysis")

loc_col1, loc_col2 = st.columns(2)

# Location Wise Avg Cost Ranking
loc_cost = (
    df.groupby('location')['approx_cost']
    .mean()
    .sort_values(ascending=False)
    .reset_index()
    .head(10)
)

fig_loc = px.bar(
    loc_cost,
    x='location',
    y='approx_cost',
    color='approx_cost',
    color_continuous_scale='tealgrn'
)

fig_loc.update_layout(
    title="Top 10 Most Expensive Locations",
    xaxis_tickangle=-45,
    height=420,
    template="plotly_dark"
)

loc_col1.plotly_chart(fig_loc, use_container_width=True)

# Location Summary Cards
avg_loc_cost = int(filtered_df['approx_cost'].mean())
total_rest = filtered_df['name'].nunique()
top_rest_type = (
    filtered_df['rest_type'].mode()[0]
    if not filtered_df['rest_type'].mode().empty else "N/A"
)

with loc_col2:
    st.metric("📊 Avg Cost in Selected Location", avg_loc_cost)
    st.metric("🏬 Total Restaurants", total_rest)
    st.metric("🍴 Most Popular Type", top_rest_type)

st.divider()

# -----------------------------
# 🍽 RESTAURANT LEVEL ANALYSIS
# -----------------------------
st.subheader("🍽 Restaurant Level Cost Comparison")

res_col1, res_col2 = st.columns(2)

# Top 10 Costly Restaurants in Selected Location
top_cost = (
    filtered_df.groupby('name')['approx_cost']
    .mean()
    .nlargest(10)
    .reset_index()
)

fig_res = px.bar(
    top_cost,
    x='name',
    y='approx_cost',
    color='approx_cost',
    color_continuous_scale='plasma'
)

fig_res.update_layout(
    title="Top 10 Costly Restaurants in Selected Location",
    xaxis_tickangle=-45,
    height=420,
    template="plotly_dark"
)

res_col1.plotly_chart(fig_res, use_container_width=True)

# Selected Restaurant Detail Card Section
with res_col2:
    st.metric("📌 Selected Restaurant", restaurant)
    st.metric("⭐ Rating", round(rest_df['rate'].mean(), 2))
    st.metric("🗳 Votes", int(rest_df['votes'].sum()))
    st.metric("💰 Avg Cost", int(rest_df['approx_cost'].mean()))
