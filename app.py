import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Zomato Analytics Dashboard", layout="wide")

st.title(" Zomato Analytics Dashboard")
st.markdown("### Interactive Categorical vs Numeric Analysis")

# -------------------- Load Data --------------------
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

# -------------------- Sidebar Filters --------------------
st.sidebar.header("🔎 Filter Data")

location = st.sidebar.selectbox("Select Location", sorted(df['location'].unique()))
online_order = st.sidebar.selectbox("Online Order", ["All"] + list(df['online_order'].unique()))

filtered_df = df[df['location'] == location]

if online_order != "All":
    filtered_df = filtered_df[filtered_df['online_order'] == online_order]

# -------------------- KPI Section --------------------
st.markdown("## 📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Restaurants", filtered_df.shape[0])
col2.metric("Average Cost", f"₹ {round(filtered_df['approx_cost'].mean(),2)}")
col3.metric("Average Rating", round(filtered_df['rate'].mean(),2))
col4.metric("Average Votes", round(filtered_df['votes'].mean(),2))

st.markdown("---")

# -------------------- Charts Row 1 --------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Top 10 Expensive Restaurants")
    top_cost = filtered_df.groupby('name')['approx_cost'].mean().nlargest(10).reset_index()
    fig1 = px.bar(top_cost,
                  x='name',
                  y='approx_cost',
                  color='approx_cost',
                  title="Top 10 Restaurant by Cost",
                  template="plotly_dark")
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("⭐ Rating Distribution")
    fig2 = px.histogram(filtered_df,
                        x='rate',
                        nbins=20,
                        color_discrete_sequence=['orange'],
                        template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# -------------------- Charts Row 2 --------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Votes vs Rating (Bubble)")
    fig3 = px.scatter(filtered_df,
                      x='votes',
                      y='rate',
                      size='approx_cost',
                      color='online_order',
                      hover_name='name',
                      template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("🛵 Online Order Impact on Rating")
    online_analysis = filtered_df.groupby('online_order')['rate'].mean().reset_index()
    fig4 = px.bar(online_analysis,
                  x='online_order',
                  y='rate',
                  color='rate',
                  template="plotly_dark")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# -------------------- Charts Row 3 --------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("💵 Cost vs Rating Relationship")
    fig5 = px.scatter(filtered_df,
                      x='approx_cost',
                      y='rate',
                      color='rate',
                      template="plotly_dark")
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    st.subheader("🏆 Top 10 Highest Rated Restaurants")
    top_rated = filtered_df.groupby('name')['rate'].mean().nlargest(10).reset_index()
    fig6 = px.bar(top_rated,
                  x='name',
                  y='rate',
                  color='rate',
                  template="plotly_dark")
    fig6.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# -------------------- Category Analysis --------------------
st.subheader("📌 Restaurant Type Distribution")

type_analysis = filtered_df['rest_type'].value_counts().nlargest(10).reset_index()
type_analysis.columns = ['rest_type', 'count']

fig7 = px.pie(type_analysis,
              names='rest_type',
              values='count',
              template="plotly_dark")
st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")

# -------------------- Correlation Heatmap --------------------
st.subheader("🔥 Correlation Between Numeric Features")

corr = filtered_df[['approx_cost', 'rate', 'votes']].corr()

fig8 = px.imshow(corr,
                 text_auto=True,
                 template="plotly_dark",
                 color_continuous_scale='reds')
st.plotly_chart(fig8, use_container_width=True)

st.markdown("### 🚀 Built with Streamlit & Plotly | Live Interactive Dashboard")
