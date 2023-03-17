import streamlit as st
import pandas as pd
import my_functions
import matplotlib.pyplot as plt

container1 = st.container()
container2 = st.container()
container3 = st.container()
container4 = st.container()
container5 = st.container()
container6 = st.container()

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
        
with container5:
    
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