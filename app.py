import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events

st.set_page_config(layout="wide")

# ---------- THEME ----------
st.markdown("""
<style>
.stApp {background-color:#0B1220;}
div[data-testid="metric-container"] {
    background:#1E293B;
    border-radius:12px;
    padding:16px;
}
</style>
""", unsafe_allow_html=True)

st.title("Zomato Performance Intelligence")

# ---------- LOAD ----------
df = pd.read_csv("Zomato_Data.csv")
df = df.drop('Unnamed: 0', axis=1)
df = df.rename(columns={'approx_cost(for two people)':'approx_cost'})
df = df.fillna(0)
df.approx_cost = df.approx_cost.replace('[,]','',regex=True).astype(int)
df.rate = df.rate.replace(['-','NEW'],0)
df.rate = df.rate.replace('[/5]','',regex=True).astype(float)

# ---------- FILTER ----------
location = st.sidebar.selectbox("Location", sorted(df.location.unique()))
filtered_df = df[df.location == location]

# ---------- KPI STRIP (Only Summary) ----------
k1,k2,k3 = st.columns(3)
k1.metric("Total Restaurants", filtered_df.shape[0])
k2.metric("Avg Rating (Location)", round(filtered_df.rate.mean(),2))
k3.metric("Avg Cost (Location)", f"₹ {int(filtered_df.approx_cost.mean())}")

st.markdown("---")

# ---------- HERO CHART ----------
col1, col2 = st.columns([2,1])

with col1:
    cost_df = filtered_df.groupby("name")["approx_cost"].mean().sort_values(ascending=False).head(20).reset_index()

    fig = px.bar(
        cost_df,
        x="name",
        y="approx_cost",
        color="approx_cost",
        color_continuous_scale="Reds"
    )

    fig.update_layout(
        height=500,
        plot_bgcolor="#0B1220",
        paper_bgcolor="#0B1220",
        font=dict(color="white"),
        xaxis_tickangle=-45
    )

    selected = plotly_events(fig, click_event=True)

    st.plotly_chart(fig, use_container_width=True)

if selected:
    selected_name = selected[0]["x"]
else:
    selected_name = cost_df.iloc[0]["name"]

restaurant_df = filtered_df[filtered_df.name == selected_name]

# ---------- SIDE INSIGHT PANEL ----------
with col2:
    st.subheader(selected_name)
    st.metric("Rating", round(restaurant_df.rate.mean(),2))
    st.metric("Votes", int(restaurant_df.votes.mean()))
    st.metric("Type", restaurant_df.rest_type.mode()[0])
    st.metric("Online Order", restaurant_df.online_order.mode()[0])

st.markdown("---")

# ---------- BOTTOM STRIP (No Repetition) ----------
c1,c2 = st.columns(2)

with c1:
    fig2 = px.scatter(
        filtered_df,
        x="votes",
        y="approx_cost",
        size="rate",
        color="rate",
        color_continuous_scale="Tealgrn"
    )
    fig2.update_layout(height=350,
                       plot_bgcolor="#0B1220",
                       paper_bgcolor="#0B1220",
                       font=dict(color="white"),
                       title="Cost vs Popularity")
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    type_df = filtered_df.rest_type.value_counts().head(8).reset_index()
    type_df.columns = ["Type","Count"]

    fig3 = px.bar(
        type_df,
        x="Count",
        y="Type",
        orientation="h",
        color="Count",
        color_continuous_scale="Purples"
    )
    fig3.update_layout(height=350,
                       plot_bgcolor="#0B1220",
                       paper_bgcolor="#0B1220",
                       font=dict(color="white"),
                       title="Dominant Restaurant Types")
    st.plotly_chart(fig3, use_container_width=True)
