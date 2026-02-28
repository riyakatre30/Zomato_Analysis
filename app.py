import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide", page_title="Zomato BI Dashboard")

# ---------- PREMIUM CSS ----------
st.markdown("""
<style>
.stApp {
    background-color: #0F172A;
}
section[data-testid="stSidebar"] {
    background-color: #111827;
}
div[data-testid="metric-container"] {
    background: #1E293B;
    border-radius: 12px;
    padding: 18px;
    border: 1px solid #334155;
}
h1, h2, h3 {
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🍽️ Zomato Business Intelligence Dashboard")
st.caption("Executive Restaurant Performance Overview")

# ---------- LOAD DATA ----------
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

# ---------- SIDEBAR ----------
st.sidebar.header("Filters")
location = st.sidebar.selectbox("Location", sorted(df.location.unique()))
filtered_df = df[df.location == location]

restaurant = st.sidebar.selectbox("Restaurant", sorted(filtered_df.name.unique()))
restaurant_df = filtered_df[filtered_df.name == restaurant]

# ---------- KPI ROW ----------
k1, k2, k3, k4 = st.columns(4)

k1.metric("⭐ Rating", round(restaurant_df.rate.mean(),2))
k2.metric("🗳 Votes", int(restaurant_df.votes.mean()))
k3.metric("💰 Avg Cost (2 People)", f"₹ {int(restaurant_df.approx_cost.mean())}")
k4.metric("🍴 Type", restaurant_df.rest_type.mode()[0])

st.markdown("---")

# ---------- MAIN GRID ----------
col1, col2 = st.columns([1.5,1])

# -------- Chart 1: Name-wise Cost --------
with col1:
    cost_df = filtered_df.groupby("name")["approx_cost"].mean().sort_values(ascending=False).head(10).reset_index()

    cost_df["Highlight"] = cost_df["name"].apply(lambda x: "Selected" if x == restaurant else "Others")

    fig1 = px.bar(
        cost_df,
        x="name",
        y="approx_cost",
        color="Highlight",
        color_discrete_map={
            "Selected": "#F43F5E",
            "Others": "#334155"
        },
        title="Top 10 Restaurants by Cost"
    )

    fig1.update_layout(
        height=380,
        xaxis_tickangle=-45,
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="white"),
        legend_title=""
    )

    st.plotly_chart(fig1, use_container_width=True)

# -------- Chart 2: Votes vs Rating --------
with col2:
    fig2 = px.scatter(
        filtered_df,
        x="votes",
        y="rate",
        size="approx_cost",
        color_discrete_sequence=["#22D3EE"],
        hover_name="name",
        title="Popularity vs Rating"
    )

    fig2.update_layout(
        height=380,
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="white")
    )

    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ---------- BOTTOM SECTION ----------
b1, b2 = st.columns(2)

# -------- Rating Distribution --------
with b1:
    fig3 = px.histogram(
        filtered_df,
        x="rate",
        nbins=20,
        color_discrete_sequence=["#A78BFA"],
        title="Rating Distribution"
    )

    fig3.update_layout(
        height=300,
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="white")
    )

    st.plotly_chart(fig3, use_container_width=True)

# -------- Top Restaurant Types --------
with b2:
    type_df = filtered_df.rest_type.value_counts().head(8).reset_index()
    type_df.columns = ["rest_type", "count"]

    fig4 = px.bar(
        type_df,
        x="count",
        y="rest_type",
        orientation="h",
        color_discrete_sequence=["#38BDF8"],
        title="Top Restaurant Types"
    )

    fig4.update_layout(
        height=300,
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="white")
    )

    st.plotly_chart(fig4, use_container_width=True)

st.markdown("### 2026 BI Portfolio Project")
