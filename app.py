import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Zomato Analytics Dashboard", layout="wide")

st.title(" Zomato  Analytics Dashboard")
st.markdown("Interactive analysis between categorical and numeric features")

# -------------------- Load Data --------------------
@st.cache_data
def load_data():
    df = pd.read_csv("zomato.csv")
    
    df = df.drop(['url','address','book_table','phone','dish_liked',
                  'cuisines','reviews_list','menu_item',
                  'listed_in(type)','listed_in(city)'], axis=1)

    df = df.rename(columns={'approx_cost(for two people)': 'approx_cost'})
    df = df.fillna(0)

    df.approx_cost = df.approx_cost.replace('[,]', '', regex=True).astype('int64')
    df.rate = df.rate.replace(['-', 'NEW'], 0)
    df.rate = df.rate.replace('[/5]', '', regex=True).astype('float64')

    return df

df = load_data()

# -------------------- Sidebar Filters --------------------
st.sidebar.header("🔎 Filters")

location = st.sidebar.selectbox("Select Location", df['location'].unique())

filtered_df = df[df['location'] == location]

# -------------------- Top Metrics --------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Restaurants", filtered_df.shape[0])
col2.metric("Average Cost", round(filtered_df['approx_cost'].mean(), 2))
col3.metric("Average Rating", round(filtered_df['rate'].mean(), 2))
col4.metric("Average Votes", round(filtered_df['votes'].mean(), 2))

st.markdown("---")

# -------------------- Location Wise Cost --------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Top 10 Expensive Restaurants")
    top_cost = filtered_df.groupby('name')['approx_cost'].mean().nlargest(10).reset_index()
    fig1 = px.bar(top_cost, x='name', y='approx_cost',
                  color='approx_cost',
                  title="Top 10 Restaurant by Cost")
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("⭐ Rating Distribution")
    fig2 = px.histogram(filtered_df, x='rate',
                        nbins=20,
                        title="Rating Distribution",
                        color_discrete_sequence=['orange'])
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# -------------------- Votes vs Rating --------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Votes vs Rating")
    fig3 = px.scatter(filtered_df,
                      x='votes',
                      y='rate',
                      size='approx_cost',
                      color='online_order',
                      hover_name='name',
                      title="Votes vs Rating (Bubble Analysis)")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("🛵 Online Order Impact on Rating")
    online_analysis = filtered_df.groupby('online_order')['rate'].mean().reset_index()
    fig4 = px.bar(online_analysis,
                  x='online_order',
                  y='rate',
                  color='online_order',
                  title="Average Rating by Online Order")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# -------------------- Cost vs Rating --------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("💵 Cost vs Rating")
    fig5 = px.scatter(filtered_df,
                      x='approx_cost',
                      y='rate',
                      color='rate',
                      title="Cost vs Rating Relationship")
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    st.subheader("🏆 Top 10 Highest Rated Restaurants")
    top_rated = filtered_df.groupby('name')['rate'].mean().nlargest(10).reset_index()
    fig6 = px.bar(top_rated,
                  x='name',
                  y='rate',
                  color='rate',
                  title="Top Rated Restaurants")
    fig6.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# -------------------- Data Preview --------------------
st.subheader("📋 Dataset Preview")
st.dataframe(filtered_df.head(20))

st.markdown("### 🚀 Built with Streamlit & Plotly | Interactive Restaurant Analytics")
