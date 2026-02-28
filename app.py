import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Zomato Analytics", layout="wide")

# -----------------------------
# Smoky Gradient Background
# -----------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #2c3e50, #3a3f47, #4b5563);
}
.metric-container {
    background: rgba(255,255,255,0.08);
    padding: 12px;
    border-radius: 12px;
    text-align: center;
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
# Top KPI Cards
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("⭐ Rating", round(rest_df['rate'].mean(), 2))
col2.metric("🗳 Total Votes", int(rest_df['votes'].sum()))
col3.metric("💰 Avg Cost", int(rest_df['approx_cost'].mean()))
col4.metric("🍴 Top Rest Type",
            filtered_df['rest_type'].mode()[0]
            if not filtered_df['rest_type'].mode().empty else "N/A")

st.markdown("---")

# -----------------------------
# SIDE BY SIDE GRAPHS
# -----------------------------
left, right = st.columns(2)

# 📍 Location Wise Cost
with left:
    st.subheader("📍 Top 10 Expensive Locations")

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
        y='approx_cost'
    )

    fig_loc.update_traces(
        marker=dict(
            color=loc_cost['approx_cost'],
            colorscale=[
                [0, "#1f2937"],
                [0.5, "#374151"],
                [1, "#d1d5db"]
            ]
        )
    )

    fig_loc.update_layout(
        height=350,
        xaxis_tickangle=-40,
        template="plotly_dark",
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_loc, use_container_width=True)


# 🍽 Restaurant Wise Cost
with right:
    st.subheader("🍽 Top 10 Costly Restaurants (Selected Location)")

    top_cost = (
        filtered_df.groupby('name')['approx_cost']
        .mean()
        .nlargest(10)
        .reset_index()
    )

    fig_res = px.bar(
        top_cost,
        x='name',
        y='approx_cost'
    )

    fig_res.update_traces(
        marker=dict(
            color=top_cost['approx_cost'],
            colorscale=[
                [0, "#0f172a"],
                [0.5, "#334155"],
                [1, "#e5e7eb"]
            ]
        )
    )

    fig_res.update_layout(
        height=350,
        xaxis_tickangle=-40,
        template="plotly_dark",
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_res, use_container_width=True)

st.markdown("---")

# -----------------------------
# Bottom Small Cards (Location Summary)
# -----------------------------
c1, c2, c3 = st.columns(3)

c1.metric("📊 Total Restaurants", filtered_df['name'].nunique())
c2.metric("💵 Avg Location Cost", int(filtered_df['approx_cost'].mean()))
c3.metric("⭐ Avg Location Rating", round(filtered_df['rate'].mean(), 2))
