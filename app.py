import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Zomato Analytics", layout="wide")

# -----------------------------
# Custom Styling
# -----------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #1e1e2f, #111827);
}
.metric-card {
    background-color: #1f2937;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    color: white;
}
h1 {
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
# KPI Cards
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("⭐ Rating", round(rest_df['rate'].mean(),2))
col2.metric("🗳 Votes", int(rest_df['votes'].sum()))
col3.metric("💰 Avg Cost", int(rest_df['approx_cost'].mean()))
col4.metric("🍴 Most Popular Type", 
            filtered_df['rest_type'].mode()[0] if not filtered_df['rest_type'].mode().empty else "N/A")

# -----------------------------
# Charts Layout
# -----------------------------
c1, c2 = st.columns(2)

# 1️⃣ Top 10 Expensive Restaurants (Location Wise)
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
    color_continuous_scale='tealgrn',
    title="Top 10 Costly Restaurants"
)
fig1.update_layout(height=400)

c1.plotly_chart(fig1, use_container_width=True)

# 2️⃣ Rating Distribution (Location Wise)
fig2 = px.histogram(
    filtered_df,
    x="rate",
    nbins=20,
    color_discrete_sequence=["#00C6FF"],
    title="Rating Distribution"
)
fig2.update_layout(height=400)

c2.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Bottom Section
# -----------------------------
c3, c4 = st.columns(2)

# 3️⃣ Restaurant Type Popularity
rest_type_count = (
    filtered_df['rest_type']
    .value_counts()
    .nlargest(10)
    .reset_index()
)
rest_type_count.columns = ['rest_type', 'count']

fig3 = px.bar(
    rest_type_count,
    x='rest_type',
    y='count',
    color='count',
    color_continuous_scale='blues',
    title="Most Popular Restaurant Types"
)
fig3.update_layout(xaxis_tickangle=-45, height=400)

c3.plotly_chart(fig3, use_container_width=True)

# 4️⃣ Votes vs Rating (Restaurant Highlighted)
fig4 = px.bar(
    filtered_df,
    x="name",
    y="votes",
    color="rate",
    title="Votes by Restaurant (Color = Rating)"
)
fig4.update_layout(showlegend=False, height=400)

c4.plotly_chart(fig4, use_container_width=True)
