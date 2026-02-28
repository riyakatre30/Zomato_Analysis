import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide", page_title="Zomato Analysis")

# ------------------ PREMIUM THEME ------------------
st.markdown("""
<style>
.stApp {
    background-color: #0B1220;
    color: #FFFFFF;
}
section[data-testid="stSidebar"] {
    background-color: #111827;
}
div[data-testid="metric-container"] {
    background: #111827;
    border-radius: 10px;
    padding: 15px;
    border: 1px solid #1f2937;
}
h1, h2, h3 {
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)

st.title(" Zomato  Dashboard")


# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "Zomato_Data.csv")
    df = pd.read_csv(file_path)

    df = df.drop('Unnamed: 0', axis=1)
    df = df.rename(columns={'approx_cost(for two people)': 'approx_cost'})
    df = df.fillna(0)

    df.approx_cost = df.approx_cost.replace('[,]', '', regex=True).astype('int64')
    df.rate = df.rate.replace(['-', 'NEW'], 0)
    df.rate = df.rate.replace('[/5]', '', regex=True).astype('float64')

    return df

df = load_data()

# ------------------ SIDEBAR FILTERS ------------------
st.sidebar.header("Filters")

location = st.sidebar.selectbox("Select Location", sorted(df.location.unique()))
filtered_df = df[df.location == location]

restaurant = st.sidebar.selectbox("Select Restaurant", sorted(filtered_df.name.unique()))
restaurant_df = filtered_df[filtered_df.name == restaurant]

# ------------------ KPI ROW ------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric(" Rating", round(restaurant_df.rate.mean(),2))
col2.metric(" Votes", int(restaurant_df.votes.mean()))
col3.metric(" Avg Cost (2 People)", f"₹ {int(restaurant_df.approx_cost.mean())}")
col4.metric(" Restaurant Type", restaurant_df.rest_type.mode()[0])

st.markdown("---")

# ------------------ MAIN GRID ------------------
colA, colB = st.columns([1.4,1])

# -------- Restaurant-wise Cost Comparison --------
with colA:
    cost_df = filtered_df.groupby("name")["approx_cost"].mean().sort_values(ascending=False).head(12).reset_index()

    fig1 = px.bar(
        cost_df,
        x="name",
        y="approx_cost",
        title="Top 12 Restaurants by Average Cost",
        color_discrete_sequence=["#E23744"]
    )
    fig1.update_layout(
        height=400,
        xaxis_tickangle=-45,
        plot_bgcolor="#0B1220",
        paper_bgcolor="#0B1220",
        font=dict(color="white")
    )
    st.plotly_chart(fig1, use_container_width=True)

# -------- Votes vs Rating --------
with colB:
    fig2 = px.scatter(
        filtered_df,
        x="votes",
        y="rate",
        size="approx_cost",
        hover_name="name",
        color_discrete_sequence=["#2DD4BF"]
    )
    fig2.update_layout(
        height=400,
        plot_bgcolor="#0B1220",
        paper_bgcolor="#0B1220",
        font=dict(color="white"),
        title="Votes vs Rating Analysis"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ------------------ BOTTOM SECTION ------------------
colC, colD = st.columns(2)

# -------- Rating Distribution --------
with colC:
    fig3 = px.histogram(
        filtered_df,
        x="rate",
        nbins=20,
        color_discrete_sequence=["#6366F1"]
    )
    fig3.update_layout(
        height=300,
        plot_bgcolor="#0B1220",
        paper_bgcolor="#0B1220",
        font=dict(color="white"),
        title="Rating Distribution"
    )
    st.plotly_chart(fig3, use_container_width=True)

# -------- Top Restaurant Types --------
with colD:
    type_df = filtered_df.rest_type.value_counts().head(10).reset_index()
    type_df.columns = ["rest_type", "count"]

    fig4 = px.bar(
        type_df,
        x="count",
        y="rest_type",
        orientation="h",
        color_discrete_sequence=["#F59E0B"]
    )
    fig4.update_layout(
        height=300,
        plot_bgcolor="#0B1220",
        paper_bgcolor="#0B1220",
        font=dict(color="white"),
        title="Top 10 Restaurant Types"
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("### 2026 Executive Analytics | Portfolio Ready")
