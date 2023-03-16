import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


def mask_names_inplace(df, col_names):
    # Define a regular expression to replace all characters in a word except the first letter
    regex = re.compile(r'\B\w')

    # Loop through the column names and replace each column with masked values using regex
    for col_name in col_names:
        # Use the .loc accessor to apply the lambda function to each element of the column in place
        df.loc[:, col_name] = df[col_name].apply(lambda name: 
            # If the element is a string, apply the regular expression to mask the name
            regex.sub('*', str(name)) if isinstance(name, str) else 
            # Otherwise, return NaN to handle missing values
            np.nan)
    
    return df

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