import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide", page_title="Zomato 2026 Dashboard")

# ------------------ AESTHETIC BACKGROUND ------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1f1c2c, #928dab);
}
section[data-testid="stSidebar"] {
    background: #111827;
}
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 15px;
    backdrop-filter: blur(8px);
}
</style>
""", unsafe_allow_html=True)

st.title("🍽️ Zomato Executive Insights Dashboard")
st.markdown("### Real-Time Restaurant Performance Analysis")

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

# ------------------ SIDEBAR SLICER ------------------
st.sidebar.header("🔎 Filters")

location = st.sidebar.selectbox("Select Location", sorted(df.location.unique()))
filtered_df = df[df.location == location]

restaurant = st.sidebar.selectbox("Select Restaurant", sorted(filtered_df.name.unique()))
restaurant_df = filtered_df[filtered_df.name == restaurant]

# ------------------ KPI CARDS ------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("⭐ Rating", round(restaurant_df.rate.mean(),2))
col2.metric("🗳 Votes", int(restaurant_df.votes.mean()))
col3.metric("💰 Avg Cost", f"₹ {int(restaurant_df.approx_cost.mean())}")
col4.metric("🍴 Rest Type", restaurant_df.rest_type.mode()[0])

st.markdown("---")

# ------------------ MAIN GRID ------------------
colA, colB = st.columns([1.4,1])

# -------- Chart 1: Votes vs Rating (Main Impact Chart) --------
with colA:
    fig1 = px.scatter(
        filtered_df,
        x="votes",
        y="rate",
        size="approx_cost",
        color="rate",
        hover_name="name",
        color_continuous_scale="Tealgrn",
        title="Restaurant Popularity vs Rating"
    )
    fig1.update_layout(height=400)
    st.plotly_chart(fig1, use_container_width=True)

# -------- Chart 2: Cost Distribution --------
with colB:
    top_cost = filtered_df.groupby("name")["approx_cost"].mean().nlargest(8).reset_index()

    fig2 = px.bar(
        top_cost,
        x="approx_cost",
        y="name",
        orientation="h",
        color="approx_cost",
        color_continuous_scale="sunset",
        title="Top 8 Costly Restaurants"
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ------------------ BOTTOM SECTION ------------------
colC, colD = st.columns(2)

# -------- Chart 3: Rating Trend Line --------
with colC:
    rating_dist = filtered_df.groupby("rate")["votes"].mean().reset_index()

    fig3 = px.line(
        rating_dist,
        x="rate",
        y="votes",
        markers=True,
        title="Average Votes per Rating Level",
        color_discrete_sequence=["#FF4B2B"]
    )
    fig3.update_layout(height=300)
    st.plotly_chart(fig3, use_container_width=True)

# -------- Chart 4: Top Restaurant Types --------
with colD:
    type_analysis = filtered_df.rest_type.value_counts().nlargest(10).reset_index()
    type_analysis.columns = ["rest_type", "count"]

    fig4 = px.bar(
        type_analysis,
        x="count",
        y="rest_type",
        orientation="h",
        color="count",
        color_continuous_scale="magma",
        title="Top 10 Restaurant Types"
    )
    fig4.update_layout(height=300)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("### 🚀 2026 Interactive Executive Dashboard | Portfolio Ready")
