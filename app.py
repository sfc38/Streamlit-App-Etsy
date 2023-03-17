import streamlit as st
import pandas as pd
import my_functions
import matplotlib.pyplot as plt
import datetime

# Use a with statement to create the sidebar
with st.sidebar:
    # Add a title to the sidebar
    st.title("Welcome to My App")

container1 = st.container()
container2 = st.container()
container3 = st.container()
container4 = st.container()
container5 = st.container()
container6 = st.container()
container7 = st.container()

# Open the file and read its contents
with open('text1.txt', 'r') as f:
    text = f.read()

with container1:
    # Add content to the app
    st.title("Etsy Orders Data Analysis App")
    st.write(text) 

    # Create upload button
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
      
with container2:
    # If a file was uploaded
    if uploaded_file is None:
        # Read the CSV file and store it as a DataFrame
        df = pd.read_csv('EtsySoldOrders2022_masked.csv')
        
        # If no file is uploaded, show a message that sample data is being used
        st.warning("No file uploaded. Using sample data.")
    else: 
        # Load file into dataframe
        df = pd.read_csv(uploaded_file)
        
        # List of column names to mask
        col_names = ['Buyer User ID', 'Full Name', 'First Name', 'Last Name', 'Buyer']
        
        # Mask the data
        df = my_functions.mask_names_inplace(df, col_names)
    
with container3:
    # Create a checkbox that toggles the display of the entire DataFrame
    if st.checkbox("Check to display the entire DataFrame."):
        st.write(df)
    else:
        st.write(df.head())
        
with container4:
    # Create a header
    st.header("Daily Quantity of Items Sold")
    
    # Preparing the Data for Plotting
    my_functions.add_date_columns(df, 'Sale Date')
    grouped_df = my_functions.get_clean_sales_data_by_date(df)
    
    # Get the minimum and maximum dates from the "Date" column of the DataFrame
    min_date = pd.to_datetime(grouped_df['Date']).min()
    max_date = pd.to_datetime(grouped_df['Date']).max()
    
    # Set the default start date to the minimum date and the default end date to the maximum date
    default_start_date = min_date.date()
    default_end_date = max_date.date()

    # Create two columns to hold the date inputs
    start_column, end_column = st.columns(2)
    
    # Add a date input for the start date
    with start_column:
        start_date = st.date_input("Select start date", default_start_date, min_value=min_date, max_value=max_date)
    
    # Add a date input for the end date
    with end_column:
        end_date = st.date_input("Select end date", default_end_date, min_value=min_date, max_value=max_date)

    filtered_df = my_functions.filter_dataframe_by_date(grouped_df, start_date, end_date)
    
    my_functions.plot_line_chart_plotly(filtered_df, 'Date', 'Total Quantity Sold')

        
with container5:
    # Create a header
    st.header("Number of Sold Items Plots")
    
    # Create two tabs
    tabs = st.tabs(["Number of Sold Items by Month", "Number of Sold Items by Weekend/Weekday"])

    # Add content to the tabs
    with tabs[0]:
        # Create new columns for sale_date_datetime, year, month, day, day_of_week, and is_weekend
        my_functions.add_date_columns(df, 'Sale Date')

        # Call the function to calculate the monthly sum and fill missing months with zero
        df_monthly_sum = my_functions.calculate_monthly_sum(df)

        # Plot the monthly sales
        my_functions.plot_monthly_sales(df_monthly_sum)

    with tabs[1]:
        # plot number of sales by Weekend/Weekday
        my_functions.plot_sales_by_weekday_weekend(df)
        
with container6:
    
    # Add a header to the container
    st.header("Plot Top n States")
    
    # Add a slider to the container
    slider_value = st.slider("Select a value", 0, 56, 10)
    
    # Display the selected value
    st.write("You selected:", slider_value)
    
    orders_by_state = my_functions.get_orders_by_state(df)
    orders_by_state = my_functions.clean_orders_by_state(orders_by_state)
    grouped_orders = my_functions.group_orders_by_state(orders_by_state, slider_value)
    my_functions.plot_orders_by_state_bar_with_percentage(grouped_orders)