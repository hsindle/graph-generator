import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("🎟️ Ticket Sales Graph Generator")

# File uploader
uploaded_file = st.file_uploader("Upload your ticket sales CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Convert Order Date to datetime
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    df = df.dropna(subset=['Order Date'])

    # Add quantity column (1 ticket per row)
    df['quantity'] = 1

    # Hourly Sales Graph
    st.subheader("⏰ Ticket Sales by Hour of Day")
    df['hour'] = df['Order Date'].dt.hour
    hourly_sales = df.groupby('hour')['quantity'].sum()

    fig1, ax1 = plt.subplots()
    hourly_sales.plot(kind='bar', ax=ax1)
    ax1.set_xlabel("Hour")
    ax1.set_ylabel("Tickets Sold")
    ax1.set_title("Ticket Sales by Hour of Day")
    st.pyplot(fig1)

    # Daily Sales Graph
    st.subheader("📅 Ticket Sales Over Time")
    df['date'] = df['Order Date'].dt.date
    daily_sales = df.groupby('date')['quantity'].sum()

    fig2, ax2 = plt.subplots()
    daily_sales.plot(kind='line', marker='o', ax=ax2)
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Tickets Sold")
    ax2.set_title("Ticket Sales Over Time")
    st.pyplot(fig2)

    # Downloads
    st.download_button("📥 Download Hourly Sales Data", hourly_sales.to_csv().encode(), "hourly_sales.csv", "text/csv")
    st.download_button("📥 Download Daily Sales Data", daily_sales.to_csv().encode(), "daily_sales.csv", "text/csv")
