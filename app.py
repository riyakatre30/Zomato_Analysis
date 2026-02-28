import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Zomato Analytics", layout="wide")

# ----------------- STYLING -----------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}
div[data-testid="metric-container"] {
    background-color: #1e293b;
    border: 1px solid #334155;
    padding: 15px;
    border-radius: 12px;
}
h1, h2, h3 {
    color: #f8fafc;
}
</style>
""", unsafe_allow_html=True)

st.title("🍽 Zomato Restaurant Analytics")

# ----------------- LOAD DATA -----------------
@st.cache_data
def load_data():
    file_path = "data/Zomato_Data.csv"
    if not os.path.exists(file_path):
        st.error("Dataset not found. Check file path.")
        st.stop()

    df = pd.read_csv(file_path)
    df = df.drop('Unnamed: 0', axis=1)
    df = df.rename(columns={'approx_cost(for two people)': 'approx_cost'})
    df = df.fillna(0)

    df.approx_cost = df.approx_cost.replace('[,]', '', regex=True).astype('int64')
    df.rate = df.rate.replace('-', 0)
    df.rate = df.rate.replace('NEW', 0)
    df.rate = df.rate.replace('[/5]', '', regex=True).astype('float64')

    return df

df = load_data()

# ----------------- SIDEBAR FILTER -----------------
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

# ----------------- KPI CARDS -----------------
col1, col2, col3 = st.columns(3)

col1.metric("💰 Avg Cost", int(rest_df['approx_cost'].mean()))
col2.metric("⭐ Rating", round(rest_df['rate'].mean(),2))
col3.metric("🗳 Total Votes", int(rest_df['votes'].sum()))

st.divider()

# ----------------- MAIN VISUAL SECTION -----------------

c1, c2 = st.columns(2)

# 1️⃣ Location Wise Top Costly Restaurants
top_cost = (
    filtered_df.groupby('name')['approx_cost']
    .mean()
    .nlargest(10)
    .reset_index()
)

fig1 = px.bar(
    top_cost,
    x='approx_cost',
    y='name',
    orientation='h',
    color='approx_cost',
    color_continuous_scale='viridis'
)

fig1.update_layout(
    title="Top 10 Costly Restaurants (Location Wise)",
    height=450,
    template="plotly_dark"
)

c1.plotly_chart(fig1, use_container_width=True)

# 2️⃣ Restaurant Type Popularity
rest_type = (
    filtered_df['rest_type']
    .value_counts()
    .nlargest(10)
    .reset_index()
)

rest_type.columns = ['rest_type', 'count']

fig2 = px.bar(
    rest_type,
    x='rest_type',
    y='count',
    color='count',
    color_continuous_scale='teal'
)

fig2.update_layout(
    title="Most Popular Restaurant Types",
    xaxis_tickangle=-45,
    height=450,
    template="plotly_dark"
)

c2.plotly_chart(fig2, use_container_width=True)

st.divider()

# ----------------- BOTTOM SECTION -----------------

c3, c4 = st.columns(2)

# 3️⃣ Name Wise Average Cost (Selected Location)
name_cost = (
    filtered_df.groupby('name')['approx_cost']
    .mean()
    .sort_values(ascending=False)
    .head(15)
    .reset_index()
)

fig3 = px.bar(
    name_cost,
    x='name',
    y='approx_cost',
    color='approx_cost',
    color_continuous_scale='plasma'
)

fig3.update_layout(
    title="Restaurant Name Wise Average Cost",
    xaxis_tickangle=-45,
    height=450,
    template="plotly_dark"
)

c3.plotly_chart(fig3, use_container_width=True)

# 4️⃣ Online Order Availability
online = (
    filtered_df['online_order']
    .value_counts()
    .reset_index()
)

online.columns = ['online_order', 'count']

fig4 = px.bar(
    online,
    x='online_order',
    y='count',
    color='count',
    color_continuous_scale='blues'
)

fig4.update_layout(
    title="Online Order Availability",
    height=450,
    template="plotly_dark"
)

c4.plotly_chart(fig4, use_container_width=True)
