import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Zomato Analytics", layout="wide")

# -------------------- CLEAN LIGHT STYLE --------------------
st.markdown("""
<style>
.stApp {
    background-color: #f4f6f9;
}

div[data-testid="metric-container"] {
    background-color: white;
    border-radius: 10px;
    padding: 12px;
    border: 1px solid #e5e7eb;
}

h1, h2, h3 {
    color: #1f2937;
}

.block-container {
    padding-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

st.title("Zomato Restaurant Analytics Dashboard")

# -------------------- LOAD DATA --------------------
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

# -------------------- SIDEBAR --------------------
st.sidebar.header("Filters")

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

# ============================
# 🔷 TOP KPI CARDS (CLEAR)
# ============================
k1, k2, k3, k4 = st.columns(4)

k1.metric("Rating", round(rest_df['rate'].mean(), 2))
k2.metric("Total Votes", int(rest_df['votes'].sum()))
k3.metric("Average Cost for Two", int(rest_df['approx_cost'].mean()))

top_type = (
    filtered_df['rest_type'].mode()[0]
    if not filtered_df['rest_type'].mode().empty else "N/A"
)

k4.metric("Most Popular Type (Location)", top_type)

st.divider()

# ============================
# 🔷 MAIN GRAPHS SIDE BY SIDE
# ============================
left, right = st.columns(2)

# ---------------- LOCATION GRAPH ----------------
with left:

    st.subheader("Location Wise Average Cost")

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
        color_discrete_sequence=['#2563eb']
    )

    fig_loc.update_layout(
        height=340,
        xaxis_tickangle=-40,
        template="simple_white"
    )

    st.plotly_chart(fig_loc, use_container_width=True)

    # Small compact cards
    c1, c2 = st.columns(2)
    c1.metric("Avg Cost (Selected Location)",
              int(filtered_df['approx_cost'].mean()))
    c2.metric("Total Restaurants",
              filtered_df['name'].nunique())


# ---------------- RESTAURANT GRAPH ----------------
with right:

    st.subheader("Top Costly Restaurants (Selected Location)")

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
        color_discrete_sequence=['#10b981']
    )

    fig_res.update_layout(
        height=340,
        xaxis_tickangle=-40,
        template="simple_white"
    )

    st.plotly_chart(fig_res, use_container_width=True)

    r1, r2 = st.columns(2)
    r1.metric("Selected Restaurant",
              restaurant)
    r2.metric("Restaurant Avg Cost",
              int(rest_df['approx_cost'].mean()))
