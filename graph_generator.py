import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Ticket Sales Graph Generator", layout="wide")
st.markdown("""
<h1 style='text-align: center;'>🎟️ Ticket Sales Graph Generator</h1>

<div style='text-align: center; font-size: 18px;'>
  Upload CSV exports from Fatsoma to generate beautiful, interactive graphs showing ticket sales over time.
</div>

<hr>

<div style='text-align: center; font-size: 16px;'>
  <h3>🛠️ How to Export Your Ticket Sales from Fatsoma</h3>
  <p><strong>Step 1:</strong> Log into <a href='https://business.fatsoma.com/' target='_blank'>Fatsoma</a> and open the first event you want to analyse.</p>
  <p><strong>Step 2:</strong> Scroll down to the <em>Export Customer Information</em> section.</p>
  <p><strong>Step 3:</strong> Select <em>all fields</em>, and enter your email address to receive the report.</p>
  <p><strong>Step 4:</strong> Click <em>Export Data</em>.</p>
  <p><strong>Step 5:</strong> Open your email and download the attached CSV report.</p>
  <p><strong>Step 6:</strong> Upload one or more downloaded CSV files using the uploader below.</p>
  <br>
  <p>Note, you can add one event, or combine multiple events to get a broader sense of sales data!</p>
</div>

<hr>
""", unsafe_allow_html=True)


# Allow multiple file uploads
uploaded_files = st.file_uploader("📁 Upload one or more CSV files", type="csv", accept_multiple_files=True)

if uploaded_files:
    # Combine all files
    df_list = []
    for file in uploaded_files:
        try:
            temp_df = pd.read_csv(file)
            df_list.append(temp_df)
        except Exception as e:
            st.warning(f"⚠️ Could not read {file.name}: {e}")

    if df_list:
        df = pd.concat(df_list, ignore_index=True)

        # Check for required column
        if 'Order Date' not in df.columns:
            st.error("❌ One or more files do not contain the required 'Order Date' column.")
        else:
            # Clean and process
            df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
            df = df.dropna(subset=['Order Date'])  # Remove invalid dates
            df['quantity'] = 1

            # Optional: drop duplicates
            df = df.drop_duplicates()

            # TICKET SALES BY HOUR (Using Plotly)
            st.subheader("⏰ Ticket Sales by Hour of Day")
            df['hour'] = df['Order Date'].dt.hour
            hourly_sales = df.groupby('hour')['quantity'].sum().reindex(range(24), fill_value=0).reset_index()
            hourly_sales.columns = ['hour', 'tickets_sold']
            hourly_sales['hour_label'] = hourly_sales['hour'].apply(lambda x: f"{x:02d}:00")

            fig1 = px.bar(
                hourly_sales,
                x='hour_label',
                y='tickets_sold',
                labels={'hour_label': 'Hour (24h)', 'tickets_sold': 'Tickets Sold'},
                title='Ticket Sales by Hour of Day',
                text='tickets_sold',
            )

            fig1.update_traces(marker_color='#1f77b4', textposition='outside')
            fig1.update_layout(
                xaxis_tickangle=-45,
                xaxis=dict(tickmode='linear'),
                yaxis=dict(tickformat=',d'),
                bargap=0.2,
                height=600,
                margin=dict(t=60, b=160)
            )

            st.plotly_chart(fig1, use_container_width=True)
            st.divider()



            # TICKET SALES OVER TIME (with Plotly)
            st.subheader("📅 Ticket Sales Over Time")
            df['date'] = df['Order Date'].dt.date
            daily_sales = df.groupby('date')['quantity'].sum().reset_index()
            daily_sales['date'] = pd.to_datetime(daily_sales['date'])

            fig2 = px.line(
                daily_sales,
                x='date',
                y='quantity',
                markers=True,
                labels={'date': 'Date', 'quantity': 'Tickets Sold'},
                title='Ticket Sales Over Time'
            )
            fig2.update_layout(
                height=600,
                margin=dict(t=60, b=120),
                xaxis=dict(tickformat='%d/%m/%y', rangeslider_visible=True)
            )

            st.plotly_chart(fig2, use_container_width=True)
            st.divider()

            # DOWNLOAD OPTIONS
            st.subheader("⬇️ Download Graph Data as CSV")
            st.download_button(
                label="Download Hourly Sales CSV",
                data=hourly_sales.to_csv().encode(),
                file_name="hourly_sales.csv",
                mime="text/csv"
            )
            st.download_button(
                label="Download Daily Sales CSV",
                data=daily_sales.to_csv(index=False).encode(),
                file_name="daily_sales.csv",
                mime="text/csv"
            )
