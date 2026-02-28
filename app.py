import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events
import os

st.set_page_config(layout="wide", page_title="Zomato Interactive BI")

# ---------- THEME ----------
st.markdown("""
<style>
.stApp {background-color: #0F172A;}
section[data-testid="stSidebar"] {background-color: #111827;}
div[data-testid="metric-container"] {
    background: #1E293B;
    border-radius: 10px;
    padding: 15px;
}
h1,h2,h3 {color:white;}
</style>
""", unsafe_allow_html=True)

st.title("🍽 Zomato Interactive Intelligence")

# ---------- LOAD ----------
@st.cache_data
def load_data():
    df = pd.read_csv("Zomato_Data.csv")
    df = df.drop('Unnamed: 0', axis=1)
    df = df.rename(columns={'approx_cost(for two people)': 'approx_cost'})
    df = df.fillna(0)
    df.approx_cost = df.approx_cost.replace('[,]', '', regex=True).astype(int)
    df.rate = df.rate.replace(['-', 'NEW'], 0)
    df.rate = df.rate.replace('[/5]', '', regex=True).astype(float)
    return df

df = load_data()

# ---------- SIDEBAR ----------
location = st.sidebar.selectbox("Select Location", sorted(df.location.unique()))
filtered_df = df[df.location == location]

# ---------- MAIN BIG COST CHART ----------
st.subheader("Restaurant Cost Comparison (Click to Select)")

cost_df = filtered_df.groupby("name")["approx_cost"].mean().sort_values(ascending=False).head(15).reset_index()

fig = px.bar(
    cost_df,
    x="name",
    y="approx_cost",
    color_discrete_sequence=["#F43F5E"]
)

fig.update_layout(
    height=450,
    plot_bgcolor="#0F172A",
    paper_bgcolor="#0F172A",
    font=dict(color="white"),
    xaxis_tickangle=-45
)

selected_points = plotly_events(fig, click_event=True)

if selected_points:
    selected_name = selected_points[0]['x']
else:
    selected_name = cost_df.iloc[0]['name']

restaurant_df = filtered_df[filtered_df.name == selected_name]

st.markdown("---")

# ---------- KPI SECTION ----------
k1,k2,k3,k4 = st.columns(4)

k1.metric("Selected Restaurant", selected_name)
k2.metric("⭐ Rating", round(restaurant_df.rate.mean(),2))
k3.metric("🗳 Votes", int(restaurant_df.votes.mean()))
k4.metric("🍴 Type", restaurant_df.rest_type.mode()[0])

st.markdown("---")

# ---------- SECOND ROW ----------
col1,col2 = st.columns(2)

# Scatter Highlight
with col1:
    filtered_df["Highlight"] = filtered_df["name"].apply(
        lambda x: "Selected" if x == selected_name else "Others"
    )

    fig2 = px.scatter(
        filtered_df,
        x="votes",
        y="rate",
        size="approx_cost",
        color="Highlight",
        color_discrete_map={
            "Selected": "#22D3EE",
            "Others": "#334155"
        },
        hover_name="name",
        title="Popularity vs Rating"
    )

    fig2.update_layout(
        height=350,
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="white")
    )

    st.plotly_chart(fig2, use_container_width=True)

# Restaurant Type Distribution
with col2:
    type_df = filtered_df.rest_type.value_counts().head(8).reset_index()
    type_df.columns = ["rest_type","count"]

    fig3 = px.bar(
        type_df,
        x="count",
        y="rest_type",
        orientation="h",
        color_discrete_sequence=["#A78BFA"],
        title="Top Restaurant Types"
    )

    fig3.update_layout(
        height=350,
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="white")
    )

    st.plotly_chart(fig3, use_container_width=True)

st.markdown("### 2026 Interactive BI Dashboard")
