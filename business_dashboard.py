import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Business Performance Dashboard", layout="wide")

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("Amazon Sale Report.csv")
    df.columns = df.columns.str.strip()
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df.dropna(subset=['Amount'])

df = load_data()

st.sidebar.header("Filter Data")

# Category filter
categories = df['Category'].dropna().unique()
selected_category = st.sidebar.multiselect("Select Category", categories, default=categories)

# Fulfilment filter
fulfilments = df['Fulfilment'].dropna().unique()
selected_fulfilment = st.sidebar.multiselect("Select Fulfilment Method", fulfilments, default=fulfilments)

# City dropdown
unique_cities = df['ship-city'].dropna().unique()
default_city = "Neemuch" if "Neemuch" in unique_cities else unique_cities[0]
selected_city = st.sidebar.selectbox("Select a City to View Details", sorted(unique_cities), index=list(sorted(unique_cities)).index(default_city))

# Apply filters to main dashboard
filtered_df = df[
    (df['Category'].isin(selected_category)) &
    (df['Fulfilment'].isin(selected_fulfilment))
]

st.title("Amazon Business Performance Dashboard")

# Total Metric
total_orders = filtered_df.shape[0]
total_revenue = filtered_df['Amount'].sum()
cancel_orders = filtered_df[filtered_df['Status'].str.lower() == 'cancelled'].shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("Total Orders", total_orders)
col2.metric("Total Revenue", f"₹{total_revenue:,.2f}")
col3.metric("Cancelled Orders", cancel_orders)

# tab sections
tab1, tab2, tab3, tab4 = st.tabs([
    "Order Summary",
    "Revenue Analysis",
    "Fulfilment",
    "Shipping Summary"
])

# tab1 for order status overview
with tab1:
    st.subheader("Order Status Overview")
    status_counts = filtered_df['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig = px.pie(status_counts, names='Status', values='Count', title="Order Status Distribution")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sales by Category")
    cat_sales = filtered_df.groupby('Category')['Amount'].sum().sort_values(ascending=False).reset_index()
    fig2 = px.bar(cat_sales, x='Category', y='Amount', title="Sales by Product Category", color='Category')
    st.plotly_chart(fig2, use_container_width=True)

# tab2 for total Revenue over time analysis
with tab2:
    st.subheader("Total Revenue Over Time")
    revenue_by_date = filtered_df.groupby('Date')['Amount'].sum().reset_index()
    fig3 = px.line(revenue_by_date, x='Date', y='Amount', title="Revenue Over Time")
    st.plotly_chart(fig3, use_container_width=True)

# tab3 for fulfilment
with tab3:
    st.subheader("Fulfilment Methods")
    fulfil = filtered_df['Fulfilment'].value_counts().reset_index()
    fulfil.columns = ['Fulfilment', 'Count']
    fig4 = px.bar(fulfil, x='Fulfilment', y='Count', title="Fulfilment Method Usage", color='Fulfilment')
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Shipping Service Level Distribution")
    ssl = filtered_df['ship-service-level'].value_counts().reset_index()
    ssl.columns = ['Service Level', 'Count']
    fig5 = px.pie(ssl, names='Service Level', values='Count', title="Shipping Service Levels")
    st.plotly_chart(fig5, use_container_width=True)

# tab4 for Shipping Summary 
with tab4:
    st.subheader("Shipping Summary by City")

    city_df = df[df['ship-city'] == selected_city]
    order_count = city_df.shape[0]
    total_sales = city_df['Amount'].sum()

    col4, col5 = st.columns(2)
    col4.metric(label=f"Orders from {selected_city}", value=order_count)
    col5.metric(label=f"Sales from {selected_city}", value=f"₹{total_sales:,.2f}")

    st.subheader("Top Cities by Order Count")
    city_summary = df['ship-city'].value_counts().reset_index()
    city_summary.columns = ['City', 'Orders']
    st.dataframe(city_summary)
