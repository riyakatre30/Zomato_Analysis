import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Zomato Pro Dashboard", layout="wide")

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
.metric-card {
    background-color: #1f2c38;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 2px 2px 15px rgba(0,0,0,0.4);
}
</style>
""", unsafe_allow_html=True)

# ------------------ LOAD DATA ------------------
df = pd.read_csv("zomato.csv")

# Cleaning
df = df.dropna(subset=["rate"])
df["rate"] = df["rate"].str.replace("/5", "")
df["rate"] = pd.to_numeric(df["rate"], errors="coerce")

df["approx_cost(for two people)"] = df["approx_cost(for two people)"].astype(str).str.replace(",", "")
df["approx_cost(for two people)"] = pd.to_numeric(df["approx_cost(for two people)"], errors="coerce")

# ------------------ SIDEBAR FILTER ------------------
st.sidebar.header("🔎 Filters")

location = st.sidebar.selectbox("Select Location", df["location"].dropna().unique())

filtered_loc = df[df["location"] == location]

restaurant = st.sidebar.selectbox("Select Restaurant", filtered_loc["name"].unique())

filtered = filtered_loc[filtered_loc["name"] == restaurant]

# ------------------ TITLE ------------------
st.title("🍽️ Zomato Restaurant Analytics Dashboard")

# ------------------ KPI CARDS ------------------
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"""
<div class="metric-card">
<h3>⭐ Rating</h3>
<h2>{round(filtered['rate'].mean(),2)}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="metric-card">
<h3>🗳 Votes</h3>
<h2>{int(filtered['votes'].sum())}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="metric-card">
<h3>💰 Avg Cost</h3>
<h2>₹ {int(filtered['approx_cost(for two people)'].mean())}</h2>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class="metric-card">
<h3>📦 Online Order</h3>
<h2>{filtered['online_order'].iloc[0]}</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ------------------ MAIN VISUAL SECTION ------------------
left, right = st.columns([1.3,1])

# -------- Left Side Charts --------
with left:

    # Name Wise Cost
    cost_fig = px.bar(
        filtered_loc.sort_values("approx_cost(for two people)", ascending=False).head(10),
        x="approx_cost(for two people)",
        y="name",
        orientation="h",
        color="approx_cost(for two people)",
        color_continuous_scale="Tealgrn"
    )
    cost_fig.update_layout(
        title="Top 10 Restaurants by Cost (Location Wise)",
        template="plotly_dark",
        height=350
    )
    st.plotly_chart(cost_fig, use_container_width=True)

    # Rating Distribution
    rating_fig = px.histogram(
        filtered_loc,
        x="rate",
        nbins=10,
        color_discrete_sequence=["#ff4b5c"]
    )
    rating_fig.update_layout(
        title="Rating Distribution",
        template="plotly_dark",
        height=300
    )
    st.plotly_chart(rating_fig, use_container_width=True)

# -------- Right Side Charts --------
with right:

    # Restaurant Type Distribution
    type_data = filtered_loc["rest_type"].value_counts().head(6).reset_index()
    type_data.columns = ["rest_type", "count"]

    donut = px.pie(
        type_data,
        names="rest_type",
        values="count",
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.Agsunset
    )
    donut.update_layout(
        title="Top Restaurant Types",
        template="plotly_dark",
        height=320
    )
    st.plotly_chart(donut, use_container_width=True)

    # Location Wise Avg Cost
    loc_cost = df.groupby("location")["approx_cost(for two people)"].mean().sort_values(ascending=False).head(10).reset_index()

    loc_fig = px.bar(
        loc_cost,
        x="approx_cost(for two people)",
        y="location",
        orientation="h",
        color="approx_cost(for two people)",
        color_continuous_scale="Bluered"
    )
    loc_fig.update_layout(
        title="Top Locations by Avg Cost",
        template="plotly_dark",
        height=320
    )
    st.plotly_chart(loc_fig, use_container_width=True)
