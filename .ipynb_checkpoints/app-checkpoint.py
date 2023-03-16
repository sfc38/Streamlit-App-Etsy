import streamlit as st
import pandas as pd
import my_functions
import matplotlib.pyplot as plt

# Set the page title and favicon
st.set_page_config(page_title="My App")

# Add content to the app
st.title("Welcome to My App")
st.write('''This app is designed to take your 
         store data and provide you with 
         valuable insights into your business. 
         By displaying interactive plots, 
         it helps you gain a deeper understanding of your operations.''')

st.markdown("Please upload your Etsy data.")
# Create upload button
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

# If a file was uploaded
if uploaded_file is not None:
    # Load file into dataframe
    df = pd.read_csv(uploaded_file)
else:
    # Read the CSV file and store it as a DataFrame
    df = pd.read_csv('EtsySoldOrders2022_masked.csv')
    
# List of column names to mask
col_names = ['Buyer User ID', 'Full Name', 'First Name', 'Last Name']
# Mask the data
df_masked = my_functions.mask_names_inplace(df, col_names)

# # Add a checkbox to hide and unhide the data
# hide_data = st.checkbox("Hide data")

# # Add a checkbox to hide and unhide the data
# all_data = st.checkbox("Show all data")

# Create a layout of two columns
col1, col2= st.columns([0.5,1])

# Add a checkbox to each column
hide_data = col1.checkbox("Hide/Unhide DataFrame")
load_entire_df = col2.checkbox("Display All")


# Display the data based on checkbox desicion
if not hide_data:
    if load_entire_df:
        st.write(df_masked)
    else:
        st.write(df_masked.head())
else:
    st.write('Data hidden')



# Create a title
st.title('Monthly Sales')

# Create new columns for sale_date_datetime, year, month, day, day_of_week, and is_weekend
my_functions.add_date_columns(df, 'Sale Date')

# Call the function to calculate the monthly sum and fill missing months with zero
df_monthly_sum = my_functions.calculate_monthly_sum(df)

# Plot the monthly sales
my_functions.plot_monthly_sales(df_monthly_sum)

# fig, ax = plt.subplots(figsize=(10, 6))
# ax.bar(df_monthly_sum['month'], df_monthly_sum['Number of Sold Items'])
# ax.set_title('Monthly Sales')
# ax.set_xlabel('Month')
# ax.set_ylabel('Number of Sold Items')
# st.pyplot(fig)
