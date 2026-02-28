import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Zomato Analytics", layout="wide")

# -----------------------------
# SAME DARK STYLE (AS BEFORE)
# -----------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #1e1e2f, #111827);
}
div[data-testid="metric-container"] {
    background-color: #1f2937;
    border: 1px solid #374151;
    padding: 10px;
    border-radius: 10px;
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
# Sidebar
# -----------------------------
st.sidebar.header("🔎 Filters")

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

# =============================
# 🔥 TOP KPI CARDS
# =============================
k1, k2, k3, k4 = st.columns(4)

k1.metric("⭐ Rating", round(rest_df['rate'].mean(), 2))
k2.metric("🗳 Total Votes", int(rest_df['votes'].sum()))
k3.metric("💰 Avg Cost", int(rest_df['approx_cost'].mean()))

top_type = (
    filtered_df['rest_type'].mode()[0]
    if not filtered_df['rest_type'].mode().empty else "N/A"
)

k4.metric("🍴 Popular Type", top_type)

st.divider()

# =============================
# 🔥 MAIN GRAPHS SIDE BY SIDE
# =============================
left, right = st.columns(2)

# -------- Location Graph --------
with left:

    st.subheader("📍 Location Wise Avg Cost")

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
        color_discrete_sequence=['#3b82f6']   # clean blue
    )

    fig_loc.update_layout(
        height=350,
        xaxis_tickangle=-40,
        template="plotly_dark"
    )

    st.plotly_chart(fig_loc, use_container_width=True)

    # small cards under graph
    c1, c2 = st.columns(2)
    c1.metric("Avg Cost (Selected Location)",
              int(filtered_df['approx_cost'].mean()))
    c2.metric("Total Restaurants",
              filtered_df['name'].nunique())


# -------- Restaurant Graph --------
with right:

    st.subheader("🍽 Top Costly Restaurants")

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
        color_discrete_sequence=['#10b981']  # clean green
    )

    fig_res.update_layout(
        height=350,
        xaxis_tickangle=-40,
        template="plotly_dark"
    )

    st.plotly_chart(fig_res, use_container_width=True)

    r1, r2 = st.columns(2)
    r1.metric("Selected Restaurant", restaurant)
    r2.metric("Restaurant Avg Cost",
              int(rest_df['approx_cost'].mean()))
