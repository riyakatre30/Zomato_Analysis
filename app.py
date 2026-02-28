import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide", page_title="Zomato Executive Dashboard")

# ---------- CUSTOM CSS (Company Look) ----------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
div[data-testid="metric-container"] {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #2a2e39;
}
</style>
""", unsafe_allow_html=True)

st.title("🍽️ Zomato Executive Analytics Dashboard")

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

# ---------- GLOBAL FILTERS ----------
colf1, colf2 = st.columns(2)

with colf1:
    location = st.selectbox("📍 Select Location", sorted(df.location.unique()))

filtered_df = df[df.location == location]

with colf2:
    restaurant = st.selectbox("🍴 Select Restaurant", filtered_df.name.unique())

restaurant_df = filtered_df[filtered_df.name == restaurant]

# ---------- KPI SECTION ----------
col1, col2, col3, col4 = st.columns(4)

col1.metric("⭐ Rating", round(restaurant_df.rate.mean(),2))
col2.metric("🗳 Votes", int(restaurant_df.votes.mean()))
col3.metric("💰 Avg Cost", f"₹ {int(restaurant_df.approx_cost.mean())}")
col4.metric("🛵 Online Order", restaurant_df.online_order.mode()[0])

# ---------- MAIN GRID (NO SCROLL FIT SCREEN) ----------
colA, colB, colC = st.columns([1.2,1.2,1])

# ---------- Chart 1: Cost Distribution ----------
with colA:
    fig1 = px.bar(
        filtered_df.groupby("name")["approx_cost"].mean().nlargest(8).reset_index(),
        x="name",
        y="approx_cost",
        color="approx_cost",
        template="plotly_dark",
        title="Top Costly Restaurants"
    )
    fig1.update_layout(height=300, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig1, use_container_width=True)

# ---------- Chart 2: Votes vs Rating ----------
with colB:
    fig2 = px.scatter(
        filtered_df,
        x="votes",
        y="rate",
        size="approx_cost",
        color="online_order",
        hover_name="name",
        template="plotly_dark",
        title="Votes vs Rating Impact"
    )
    fig2.update_layout(height=300, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Chart 3: Restaurant Type Pie ----------
with colC:
    fig3 = px.pie(
        filtered_df,
        names="rest_type",
        template="plotly_dark",
        title="Restaurant Type Share"
    )
    fig3.update_layout(height=300, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig3, use_container_width=True)

# ---------- Bottom Row ----------
colD, colE = st.columns(2)

# Rating Distribution Line
with colD:
    fig4 = px.histogram(
        filtered_df,
        x="rate",
        nbins=20,
        template="plotly_dark",
        title="Rating Distribution"
    )
    fig4.update_layout(height=250)
    st.plotly_chart(fig4, use_container_width=True)

# Online Order Impact
with colE:
    online_analysis = filtered_df.groupby("online_order")["rate"].mean().reset_index()

    fig5 = px.bar(
        online_analysis,
        x="online_order",
        y="rate",
        color="rate",
        template="plotly_dark",
        title="Online Order vs Rating"
    )
    fig5.update_layout(height=250)
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("### 🚀 Executive Level Interactive Dashboard | 2026 Portfolio Ready")
