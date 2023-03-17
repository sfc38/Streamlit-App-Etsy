# Import libraries

import pandas as pd
import numpy as np
import re
import copy
import calendar
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

# Define functions

def mask_names_inplace(df, col_names):
    
    # create a deep copy of the original list
    df_copy = copy.deepcopy(df)
    # Define a regular expression to replace all characters in a word except the first letter
    regex = re.compile(r'\B\w')

    # Loop through the column names and replace each column with masked values using regex
    for col_name in col_names:
        # Use the .loc accessor to apply the lambda function to each element of the column in place
        df_copy.loc[:, col_name] = df_copy[col_name].apply(lambda name: 
            # If the element is a string, apply the regular expression to mask the name
            regex.sub('*', str(name)) if isinstance(name, str) else 
            # Otherwise, return NaN to handle missing values
            np.nan) 
        
    return df_copy

def add_date_columns(df, date_col_name):
    '''
    Takes a dataframe and the name of a column containing dates as input,
    and creates new columns for sale_date_datetime, year, month, day, day_of_week, and is_weekend.
    '''
    # Convert the date column to a datetime object and create a new column for it
    df['sale_date_datetime'] = pd.to_datetime(df[date_col_name])

    # Extract year, month, day, and day of week components from the sale_date_datetime column
    df['year'] = df['sale_date_datetime'].dt.year
    df['month'] = df['sale_date_datetime'].dt.month
    df['day'] = df['sale_date_datetime'].dt.day
    df['day_of_week'] = df['sale_date_datetime'].dt.dayofweek

    # Create a new column that indicates whether the day is a weekend or not
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

def calculate_monthly_sum(df):
    # Calculate the monthly sum of the 'Number of Items' column
    monthly_sum = df.groupby('month')['Number of Items'].sum()

    # Convert the monthly sum to a DataFrame
    df_monthly_sum = monthly_sum.to_frame().reset_index()

    # Create a DataFrame with all the months
    all_months = pd.DataFrame({'month': range(1, 13)})

    # Merge the two DataFrames using a left join
    df_merged = pd.merge(all_months, df_monthly_sum, on='month', how='left')

    # Replace the missing values with zero
    df_filled = df_merged.fillna(0)
    
    # Rename the 'Number of Items' column to 'Number of Sold Items'
    df_filled = df_filled.rename(columns={'Number of Items': 'Number of Sold Items'})

    # Return the resulting DataFrame
    return df_filled

def plot_monthly_sales(df_monthly_sum):
    
    # Create a bar plot of the monthly sales
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_monthly_sum['month'], df_monthly_sum['Number of Sold Items'])

    # Set the plot title and axis labels
    ax.set_title('Monthly Sales')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Sold Items')

    # Add percentages on the bars
    for container in ax.containers:
        for rect in container:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, 
                    height + 5, 
                    f'{height/df_monthly_sum["Number of Sold Items"].sum():.1%}', 
                    ha='center')
    # Show the plot
    st.pyplot(fig)
    
def plot_sales_by_weekday_weekend(df):
    # Group the data by 'is_weekend' and get the sum of 'Number of Items'
    df_grouped = df.groupby('is_weekend')['Number of Items'].sum()

    # Map the 'is_weekend' values to labels
    labels = ['Weekday', 'Weekend']

    # Create the pie chart
    fig, ax = plt.subplots(figsize=(10, 6))
    wedges, labels, autopct = ax.pie(df_grouped, labels=labels, autopct='%1.1f%%', startangle=90)

    # Add the values next to the percentages
    for i in range(len(autopct)):
        x = autopct[i].get_position()[0]
        y = autopct[i].get_position()[1] + 0.1
        ax.text(x, y, f"({df_grouped[i]})", ha='center', va='center')

    # Add the legend and format the plot
    ax.axis('equal')
    ax.set_title('Number of Sales by Weekday/Weekend')
    ax.legend()

    # Show the plot using Streamlit's st.pyplot() method
    st.pyplot(fig)
    
def get_orders_by_state(df):
    """
    Returns a DataFrame with the number of orders from the United States
    grouped by state.

    Parameters:
        df (pandas.DataFrame): A DataFrame containing order data, including
        columns 'Order ID' and 'Ship Country'.

    Returns:
        pandas.DataFrame: A DataFrame containing the number of orders from
        the United States grouped by state.
    """
    # Filter data to only include orders from the United States
    df_us = df[df['Ship Country'] == 'United States']

    # Group the data by state and count the number of orders
    orders_by_state = df_us.groupby('Ship State')['Order ID'].nunique().reset_index()
    orders_by_state = orders_by_state.rename(columns={'Order ID': 'Number of Orders'})

    return orders_by_state

def clean_orders_by_state(orders_by_state):
    """
    Cleans the DataFrame containing the number of orders from the United States
    grouped by state by removing invalid US states and territories abbreviations,
    adding missing US states and territories with zero orders, and sorting the
    DataFrame by state.

    Parameters:
        orders_by_state (pandas.DataFrame): A DataFrame containing the number
        of orders from the United States grouped by state, with columns 'Ship
        State' and 'Number of Orders'.

    Returns:
        pandas.DataFrame: A cleaned DataFrame containing the number of orders
        from the United States grouped by state, with columns 'Ship State' and
        'Number of Orders'.
    """
    # Make a deep copy of the input DataFrame to avoid modifying the original
    orders_by_state = copy.deepcopy(orders_by_state)

    # Define a dictionary of valid US states and territories abbreviations
    valid_states = {
        'AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA',
        'GU', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA',
        'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC',
        'ND', 'MP', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX',
        'UT', 'VT', 'VI', 'VA', 'WA', 'WV', 'WI', 'WY'
    }

    # Filter out invalid US states and territories abbreviations
    orders_by_state = orders_by_state[orders_by_state['Ship State'].isin(valid_states)]

    # Add missing US states and territories with zero orders
    missing_states = list(valid_states - set(orders_by_state['Ship State']))
    missing_data = pd.DataFrame({'Ship State': missing_states, 'Number of Orders': [0] * len(missing_states)})
    orders_by_state = pd.concat([orders_by_state, missing_data], ignore_index=True)

    # Sort the DataFrame by state
    orders_by_state = orders_by_state.sort_values(by='Ship State').reset_index(drop=True)

    return orders_by_state
    
def group_orders_by_state(orders_by_state, n=10, state_col='Ship State', orders_col='Number of Orders'):
    """
    Groups the orders by state into the top n states based on the number of orders,
    and groups the remaining states into an 'Others' category.

    Parameters:
        orders_by_state (pandas.DataFrame): A DataFrame containing the number
        of orders from the United States grouped by state, with columns 'Ship
        State' and 'Number of Orders'.
        n (int): The number of top states to include in the grouped orders.
        Defaults to 10.
        state_col (str): The name of the column in the DataFrame that contains
        the state information. Defaults to 'Ship State'.
        orders_col (str): The name of the column in the DataFrame that contains
        the order information. Defaults to 'Number of Orders'.

    Returns:
        pandas.DataFrame: A DataFrame containing the grouped orders, with columns
        specified by the state_col and orders_col parameters.
    """
    # Sort the DataFrame by the number of orders in descending order
    orders_by_state = orders_by_state.sort_values(orders_col, ascending=False)

    # Create a new DataFrame with the top n states and their number of orders
    top_n_states = orders_by_state.head(n)

    # Get the sum of the orders for the remaining states
    other_orders = orders_by_state.iloc[n:, orders_by_state.columns.get_loc(orders_col)].sum()

    # Create a DataFrame for the 'Others' category
    other_states = pd.DataFrame({
        state_col: ['Others'],
        orders_col: [other_orders]
    })

    # Concatenate the top n states and the 'Others' category
    grouped_orders = pd.concat([top_n_states, other_states])

    # Return the grouped orders DataFrame
    return grouped_orders

def plot_orders_by_state_bar(orders_by_state):
    """
    Generates a bar plot of the number of orders from the United States
    grouped by state, sorted in descending order of the number of orders.

    Parameters:
        orders_by_state (pandas.DataFrame): A DataFrame containing the number
        of orders from the United States grouped by state, with columns 'Ship
        State' and 'Number of Orders'.
    """
    # Sort the DataFrame by the number of orders in descending order
    orders_by_state = orders_by_state.sort_values('Number of Orders', ascending=False)

    # Set the plot size
    fig, ax = plt.subplots(figsize=(10, 5))

    # Create a bar plot of the number of orders by state
    ax.bar(orders_by_state['Ship State'], orders_by_state['Number of Orders'])

    # Set the title and axis labels
    ax.set_title('Number of Orders by State')
    ax.set_xlabel('State')
    ax.set_ylabel('Number of Orders')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=90)

    # Show the plot using Streamlit's st.pyplot() method
    st.pyplot(fig)

def plot_orders_by_state_bar_with_percentage(orders_by_state):
    """
    Creates a bar plot of the number of orders by state and adds percentages
    to the bars.

    Parameters:
        orders_by_state (pandas.DataFrame): A DataFrame containing the number
        of orders from the United States grouped by state, with columns 'Ship
        State' and 'Number of Orders'.

    Returns:
        None
    """
    # Sort the DataFrame by the number of orders in descending order
    orders_by_state = orders_by_state.sort_values('Number of Orders', ascending=False)

    # Set the plot size
    fig, ax = plt.subplots(figsize=(10, 5))

    # Create a bar plot of the number of orders by state
    bar_plot = ax.bar(orders_by_state['Ship State'], orders_by_state['Number of Orders'])

    # Set the title and axis labels
    ax.set_title('Number of Orders by State')
    ax.set_xlabel('State')
    ax.set_ylabel('Number of Orders')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=90)

    for bar in bar_plot:
        value = bar.get_height()
        percent = str(round((value / sum(orders_by_state['Number of Orders'])) * 100, 1)) + '%'
        fontsize = (15 / len(bar_plot)) + 5
        
        rotation = 0
        if len(bar_plot) > 31:
            rotation = 90
        
        ax.text(bar.get_x() + bar.get_width()/2., value + 5, percent, ha='center', fontsize=fontsize, rotation=rotation)

    # Show the plot using Streamlit's st.pyplot() method
    st.pyplot(fig)
    
def get_clean_sales_data_by_date(df):
    # Group by sale_date_datetime and sum Number of Items
    grouped_df = df.groupby('sale_date_datetime')['Number of Items'].sum().reset_index()

    # Rename columns
    grouped_df = grouped_df.rename(columns={'sale_date_datetime': 'Date', 'Number of Items': 'Total Quantity Sold'})

    # Create a DataFrame with all dates in the date range
    date_range = pd.date_range(start=grouped_df['Date'].min(), end=grouped_df['Date'].max(), freq='D')
    date_df = pd.DataFrame({'Date': date_range})

    # Merge the date_df with the grouped_df, filling any missing dates with zero
    merged_df = pd.merge(date_df, grouped_df, how='left', on='Date').fillna(0)
    
    return merged_df
    
def filter_dataframe_by_date(df, start_date, end_date):
    # Convert start and end dates to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filter the dataframe by date range
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    return filtered_df

def plot_line_chart_plotly(df, x_col, y_col):
    # Create a line plot of Total Quantity Sold by Date
    fig = px.line(df, x=x_col, y=y_col)

    # Set the title and axis labels
    fig.update_layout(title=f'{y_col} by {x_col}', xaxis_title=x_col, yaxis_title=y_col)
    
    # Set the figure size
    fig.update_layout(width=700, height=450)

    # Display the plot using Plotly's Streamlit figure renderer
    st.plotly_chart(fig)

