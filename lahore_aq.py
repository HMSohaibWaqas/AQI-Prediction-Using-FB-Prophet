# -*- coding: utf-8 -*-
"""Lahore AQ.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bSvQkLDiEw4sRgggNrBPa-aBVirgvD78
"""

import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from matplotlib.dates import DateFormatter
from prophet.plot import plot
from prophet.diagnostics import cross_validation
from prophet.plot import plot_cross_validation_metric

air_quality_data = pd.read_excel('/content/drive/MyDrive/Colab Notebooks/DataSets/Lahore_AQI_Dataset.xlsx')

air_quality_data.shape

air_quality_data.isnull().sum()

air_quality_data.isin([-999]).sum(axis=0)

air_quality_data = air_quality_data.replace(to_replace = -999 , value = np.NaN)
#air_quality_data = air_quality_data.replace('-999', pd.NA, inplace=True)
numeric_cols = air_quality_data.select_dtypes(include='number').columns
air_quality_data[numeric_cols] = air_quality_data[numeric_cols].apply(pd.to_numeric, errors='coerce')
air_quality_data[numeric_cols] = air_quality_data[numeric_cols].fillna(air_quality_data[numeric_cols].mean())

conditions = [
    (air_quality_data['AQI'] >= 0) & (air_quality_data['AQI'] <= 50),
    (air_quality_data['AQI'] >= 51) & (air_quality_data['AQI'] <= 100),
    (air_quality_data['AQI'] >= 101) & (air_quality_data['AQI'] <= 150),
    (air_quality_data['AQI'] >= 151) & (air_quality_data['AQI'] <= 200),
    (air_quality_data['AQI'] >= 201) & (air_quality_data['AQI'] <= 300),
    (air_quality_data['AQI'] >= 301)
]

categories = ['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy', 'Very Unhealthy', 'Hazardous']

# Use numpy.select to assign categories based on conditions
air_quality_data['AQI Category'] = np.select(conditions, categories, default=None)

air_quality_data['Timestamp'] = pd.to_datetime(air_quality_data['Date (LT)'])
air_quality_data['Month'] = air_quality_data['Timestamp'].dt.month
air_quality_data['Year'] = air_quality_data['Timestamp'].dt.year
air_quality_data['Hour'] = air_quality_data['Timestamp'].dt.hour
custom_colors = {
    'Good': 'green',
    'Moderate': 'yellow',
    'Unhealthy for Sensitive Groups': 'orange',
    'Unhealthy': 'red',
    'Very Unhealthy': 'purple',
    'Hazardous': 'maroon'}

# @title Not Used -Diurnal Variation AQI Across Different Months

air_quality_data['Hour'] = air_quality_data['Hour'].astype(int)

monthly_means = air_quality_data.groupby(['Year', 'Month'])['AQI'].mean().reset_index()
month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
               7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

# Map month numbers to month names in the DataFrame
air_quality_data['Month'] = air_quality_data['Month'].map(month_names)
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
custom_colors1 = ['Blue', 'Orange', 'Maroon', 'Green', 'Black', 'Yellow', 'Purple', 'Cyan', 'Magenta', 'Pink', 'Gray', 'Red']

# Plot diurnal variation for each month using seaborn with different colors
plt.figure(figsize=(14, 8))

# Use different color palettes: 'Set1', 'Set2', 'tab10'
for i, palette in enumerate(['Set1', 'Set2', 'tab10']):
    sns.lineplot(x='Hour', y='AQI', hue='Month', data=air_quality_data, palette=custom_colors1, err_style=None, linewidth=4, hue_order=month_order)
# Create a separate legend outside the plot area
handles, labels = plt.gca().get_legend_handles_labels()
unique_labels = month_order  # Get unique month names
plt.legend(handles[:len(unique_labels)], unique_labels, title='Month', bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

# Set x-axis ticks to show all hours from 0 to 23
plt.xticks(range(24))

plt.title('Diurnal Variation of AQI Across Different Months (2019-2023)')
plt.xlabel('Hour of the Day')
plt.ylabel('Average AQI Concentration')
plt.show()

# @title Diurnal Variation Across Months
air_quality_data['Timestamp'] = pd.to_datetime(air_quality_data['Timestamp'])

# Extract the Month from the Timestamp
air_quality_data['Month'] = air_quality_data['Timestamp'].dt.month_name()

# Diurnal Variation of AQI for all months
plt.figure(figsize=(12, 8))

# Group the data by Hour and Month, and calculate the mean AQI for each hour
hourly_aqi_variation_all_months = air_quality_data.groupby(['Hour', 'Month'])['AQI'].mean().unstack()

# Reorder the months for proper plotting
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
hourly_aqi_variation_all_months = hourly_aqi_variation_all_months.reindex(month_order, axis=1)

# Custom colors
custom_colors1 = ['Blue', 'Orange', 'Maroon', 'Green', 'Black', 'Yellow', 'Purple', 'Cyan', 'Magenta', 'Pink', 'Gray', 'Red']

# Plot the trend lines for all months with custom colors
for i, month in enumerate(month_order):
    sns.lineplot(data=hourly_aqi_variation_all_months[month], label=month, marker='o', color=custom_colors1[i])

plt.title('Diurnal Variation of Mean AQI for All Months')
plt.xlabel('Hour of the Day')
plt.ylabel('Mean AQI')
plt.xticks(range(24), labels=[f'{hour}' for hour in range(24)])  # Display hours on the x-axis

# Adjust legend position
plt.legend(title='Month', bbox_to_anchor=(1, 1), loc='upper left')

plt.show()

# @title Hourly Diurnal
air_quality_data['Hour'] = air_quality_data['Hour'].astype(int)

# Plot the hourly variation of AQI
plt.figure(figsize=(12, 6))
sns.lineplot(x='Hour', y='AQI', data=air_quality_data, errorbar=None, palette='viridis')

plt.title('Hourly Variation of AQI (2019-2023)')
plt.xlabel('Hour of the Day')
plt.ylabel('Average AQI Concentration')
plt.xticks(range(24))  # Show all hours on the x-axis

plt.show()

# @title Monthly Diurnal Foe Each Year Seperately
air_quality_data['Year'] = air_quality_data['Timestamp'].dt.year
air_quality_data['Month'] = air_quality_data['Timestamp'].dt.month_name()

# Diurnal Variation of AQI for all months and years
plt.figure(figsize=(15, 10))

# Group the data by Year, Hour, and Month, and calculate the mean AQI for each hour
hourly_aqi_variation_all_years = air_quality_data.groupby(['Year', 'Hour', 'Month'])['AQI'].mean().reset_index()

# Reorder the months for proper plotting
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Custom colors
custom_colors1 = ['Blue', 'Orange', 'Maroon', 'Green', 'Black', 'Yellow', 'Purple', 'Cyan', 'Magenta', 'Pink', 'Gray', 'Red']

# Get unique years in the dataset
unique_years = air_quality_data['Year'].unique()

# Create subplots for each year
for year in unique_years:
    plt.figure(figsize=(12, 8))

    # Filter data for the current year
    subset_data = hourly_aqi_variation_all_years[hourly_aqi_variation_all_years['Year'] == year]

    # Plot the trend lines for all months with custom colors
    for i, month in enumerate(month_order):
        sns.lineplot(data=subset_data[subset_data['Month'] == month], x='Hour', y='AQI', label=month, marker='o', color=custom_colors1[i])

    plt.title(f'Diurnal Variation of Mean AQI for {year}')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Mean AQI')
    plt.xticks(range(24), labels=[f'{hour}' for hour in range(24)])  # Display hours on the x-axis

    # Adjust legend position
    plt.legend(title='Month', bbox_to_anchor=(1, 1), loc='upper left')
    plt.show()

# @title Quarter Wise Diurnal Graph
air_quality_data['Timestamp'] = pd.to_datetime(air_quality_data['Timestamp'])

# Extract the quarter and month from the timestamp
air_quality_data['Quarter'] = air_quality_data['Timestamp'].dt.quarter
air_quality_data['Month'] = air_quality_data['Timestamp'].dt.strftime('%B')

# Diurnal Variation of AQI for each quarter
quarters = sorted(air_quality_data['Quarter'].unique())

plt.figure(figsize=(15, 8))

# Plot the trend lines for each quarter
for quarter in quarters:
    # Filter data for the specific quarter
    quarter_data = air_quality_data[air_quality_data['Quarter'] == quarter]

    # Group the data by Hour and calculate the mean AQI for each hour
    hourly_aqi_variation = quarter_data.groupby('Hour')['AQI'].mean()

    # Get the month names for the legend
    month_names = ', '.join(quarter_data['Month'].unique())

    # Plot the trend line for the quarter
    sns.lineplot(x=hourly_aqi_variation.index, y=hourly_aqi_variation, label=f'Q{quarter} - {month_names}', marker='o')

plt.title('Diurnal Variation of AQI for Each Quarter')
plt.xlabel('Hour of the Day')
plt.ylabel('Mean AQI')
plt.xticks(range(24), labels=[f'{hour}' for hour in range(24)])  # Display hours on the x-axis
plt.legend(title='Quarter and Month', loc='upper left', bbox_to_anchor=(1, 1))

plt.show()

# @title Summer Vacation Quarter
air_quality_data['Timestamp'] = pd.to_datetime(air_quality_data['Timestamp'])

# Extract the quarter and month from the timestamp
air_quality_data['Quarter'] = (air_quality_data['Timestamp'].dt.month - 1) // 3 + 1
air_quality_data['Month'] = air_quality_data['Timestamp'].dt.strftime('%B')

# Define custom quarters
custom_quarters = {
    1: ['June', 'July', 'August'],
    2: ['September', 'October', 'November'],
    3: ['December', 'January', 'February'],
    4: ['March', 'April', 'May']
}

plt.figure(figsize=(15, 8))

# Plot the trend lines for each custom quarter
for quarter, months in custom_quarters.items():
    # Filter data for the specific quarter
    quarter_data = air_quality_data[air_quality_data['Month'].isin(months)]

    # Group the data by Hour and calculate the mean AQI for each hour
    hourly_aqi_variation = quarter_data.groupby('Hour')['AQI'].mean()

    # Get the month names for the legend
    month_names = ', '.join(months)

    # Plot the trend line for the custom quarter
    sns.lineplot(x=hourly_aqi_variation.index, y=hourly_aqi_variation, label=f'Q{quarter} - {month_names}', marker='o')

plt.title('Diurnal Variation of AQI for Each Custom Quarter')
plt.xlabel('Hour of the Day')
plt.ylabel('Mean AQI')
plt.xticks(range(24), labels=[f'{hour}' for hour in range(24)])  # Display hours on the x-axis
plt.legend(title='Custom Quarter and Month', loc='upper left', bbox_to_anchor=(1, 1))

plt.show()

# @title Diurnal Variation Daily
air_quality_data['Timestamp'] = pd.to_datetime(air_quality_data['Timestamp'])

# Identify the day of the week
air_quality_data['DayOfWeek'] = air_quality_data['Timestamp'].dt.day_name()

# Diurnal Variation of AQI for the whole week
plt.figure(figsize=(12, 8))

# Group the data by Hour, DayOfWeek, and calculate the mean AQI for each hour
hourly_aqi_variation = air_quality_data.groupby(['Hour', 'DayOfWeek'])['AQI'].mean().unstack()

# Reorder the weekdays for proper plotting
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
hourly_aqi_variation = hourly_aqi_variation.reindex(weekday_order, axis=1)

# Plot the trend lines for each day of the week
for day in weekday_order:
    sns.lineplot(data=hourly_aqi_variation[day], label=day, marker='o')

plt.title('Diurnal Variation of AQI for the Whole Week')
plt.xlabel('Hour of the Day')
plt.ylabel('Mean AQI')
plt.xticks(range(24), labels=[f'{hour}' for hour in range(24)])  # Display hours on the x-axis
plt.legend(title='Day of the Week')

plt.show()

# @title Distribution of AQI Across year
# Plot boxplot for PM2.5 distribution across the years
plt.figure(figsize=(12, 8))
sns.boxplot(x='Year', y='AQI', data=air_quality_data)
plt.title('Distribution of AQI Across the Years (2019-2023)')
plt.xlabel('Year')
plt.ylabel('AQI Concentration')
plt.show()

# @title Distribution of AQI Seperately
plt.figure(figsize=(12, 8))
# Use the dodge parameter to separate box plots for different AQI Categories
sns.boxplot(x='Year', y='AQI', data=air_quality_data, hue='AQI Category', palette=custom_colors, dodge=True)
# Adjust the legend position
plt.legend(title='AQI Category', bbox_to_anchor=(1, 1), loc='upper left')
plt.title('Distribution of AQI Across the Years (2019-2023)')
plt.xlabel('Year')
plt.ylabel('AQI')
plt.show()

# @title AQI Catefgory Percentage Across 2019-2023
plt.figure(figsize=(17, 12))

# Calculate the percentage of AQI category counts for each year
percentage_data = air_quality_data.groupby(['Year', 'AQI Category']).size().reset_index(name='Count')
percentage_data['Percentage'] = percentage_data.groupby('Year')['Count'].transform(lambda x: (x / x.sum()) * 100)

# Countplot for AQI categories across the years with percentage labels
plt.subplot(3, 1, 1)
ax1 = sns.barplot(x='Year', y='Percentage', hue='AQI Category', data=percentage_data, palette=custom_colors)
plt.title('AQI Category Percentage Across the Years')

# Display percentage labels on the bars
for p in ax1.patches:
    ax1.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height() ), ha='center', va='bottom')

# Adjust the legend position
plt.legend(title='AQI Category', bbox_to_anchor=(1, 1), loc='upper left')

plt.tight_layout()
plt.show()

hazardous_percentage_data = air_quality_data[air_quality_data['AQI Category'] == 'Hazardous'].groupby('Year').size()
total_records_by_year = air_quality_data.groupby('Year').size()
percentage_hazardous = (hazardous_percentage_data / total_records_by_year) * 100

# Create a bar plot for the percentage of Hazardous AQI category across the years
plt.figure(figsize=(10, 6))
sns.barplot(x=percentage_hazardous.index, y=percentage_hazardous.values, color='red')
plt.title('Percentage of Hazardous AQI Category Across the Years')
plt.xlabel('Year')
plt.ylabel('Percentage')

# Add annotations on top of each bar
for x, y in zip(range(len(percentage_hazardous)), percentage_hazardous.values):
    plt.text(x, y , f'{y:.2f}%', ha='center', va='bottom')

plt.show()

# @title AQI Category Percentage For Each Year
unique_years = air_quality_data['Year'].unique()

plt.figure(figsize=(15, 5 * len(unique_years)))

for i, year in enumerate(unique_years, start=1):
    plt.subplot(len(unique_years), 2, i)

    counts_by_year = air_quality_data[air_quality_data['Year'] == year].groupby('AQI Category').size()

    # Check if counts_by_year is not empty before plotting
    if not counts_by_year.empty:
        total_counts = counts_by_year.sum()

        # Calculate the percentage of each AQI category
        percentages = (counts_by_year / total_counts) * 100

        # Plot bars for each category
        bars = plt.bar(x=percentages.index, height=percentages, color=[custom_colors[cat] for cat in percentages.index])

        # Add annotation on top of each bar
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.2f}%', ha='center', va='bottom')

        plt.title(f'AQI Category Percentage for Year {year}')
        plt.xlabel('AQI Category')  # Empty string to remove x-axis label
        plt.ylabel('Percentage')

        # Remove x-axis ticks and labels
        plt.xticks([])

# Add legend outside the subplots
#plt.legend(labels=percentages.index, bbox_to_anchor=(1.05, 1), loc='#')

# Adjust layout
plt.tight_layout()
plt.show()

# @title AQI Category Month Wise
unique_years = air_quality_data['Year'].unique()
plt.figure(figsize=(18, 12))
for i, year in enumerate(unique_years, start=1):
    plt.subplot(len(unique_years), 1, i)
    subset_data = air_quality_data[air_quality_data['Year'] == year]
    ax = sns.countplot(x='Month', hue='AQI Category', data=subset_data,  palette=custom_colors)
    plt.title(f'AQI Category Counts for Year {year}')
    plt.xlabel('Month')
    plt.ylabel('Count')
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height() + 1), ha='center', va='bottom')

plt.tight_layout()
plt.show()

unique_years = air_quality_data['Year'].unique()
plt.figure(figsize=(18, 12))

# Define the order of months
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

for i, year in enumerate(unique_years, start=1):
    plt.subplot(len(unique_years), 1, i)
    subset_data = air_quality_data[air_quality_data['Year'] == year]

    # Calculate the percentage of AQI categories for each month
    total_records_by_month = subset_data.groupby('Month').size()
    percentage_data = subset_data.groupby(['Month', 'AQI Category']).size() / total_records_by_month * 100
    percentage_data = percentage_data.reset_index(name='Percentage')

    # Plot the stacked bar chart for AQI category percentages
    ax = sns.barplot(x='Month', y='Percentage', hue='AQI Category', data=percentage_data, palette=custom_colors, order=month_order)

    plt.title(f'AQI Category Percentages for Year {year}')
    plt.xlabel('Month')
    plt.ylabel('Percentage')

    # Display percentage labels on the bars
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.1f}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom')

    # Hide the legend
    ax.legend().set_visible(False)

plt.tight_layout()
plt.show()

# @title Same AQI Category Line Graph
unique_years = air_quality_data['Year'].unique()

plt.figure(figsize=(18, 12))

for i, aqi_category in enumerate(air_quality_data['AQI Category'].unique(), start=1):
    plt.subplot(len(air_quality_data['AQI Category'].unique()), 1, i)

    counts_by_year = air_quality_data[air_quality_data['AQI Category'] == aqi_category].groupby('Year').size()
    total_records_by_year = air_quality_data.groupby('Year').size()

    # Check if counts_by_year is not empty before plotting
    if not counts_by_year.empty:
        percentage_by_year = (counts_by_year / total_records_by_year) * 100
        percentage_by_year.plot(marker='o', linestyle='-', color=custom_colors[aqi_category], label=f'AQI Category: {aqi_category}')

        plt.title(f'AQI Category: {aqi_category} Percentages Across the Years')
        plt.xlabel('Year')
        plt.ylabel('Percentage')
        plt.legend()

        # Add annotations on top of each point
        for x, y in zip(percentage_by_year.index, percentage_by_year):
            plt.annotate(f'{y:.2f}%', (x, y), textcoords="offset points", xytext=(0,10), ha='center')

plt.tight_layout()
plt.show()

# @title 100 Limit Exceed
total_records_by_year = air_quality_data.groupby('Year').size()
crosses_100_count_by_year = air_quality_data[air_quality_data['AQI'] > 100].groupby('Year').size()

# Calculate the percentage of times AQI crosses the 100 limit for each year
percentage_crosses_100_by_year = (crosses_100_count_by_year / total_records_by_year) * 100

# Plot the bar graph with percentage and annotations
plt.figure(figsize=(12, 6))
bars = sns.barplot(x=percentage_crosses_100_by_year.index, y=percentage_crosses_100_by_year.values, color='red')

# Add annotations on top of each bar
for bar in bars.patches:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.2f}%', ha='center', va='bottom')

plt.title('Percentage of Times AQI Crosses 100 Limit Each Year')
plt.xlabel('Year')
plt.ylabel('Percentage')
plt.show()

# @title Smooth Trend of AQI Values
filtered_data = air_quality_data.dropna(subset=['AQI'])

# Smoothed trend line using a Generalized Additive Model (GAM)
lowess = sm.nonparametric.lowess

plt.figure(figsize=(15, 8))

# Plot the scatter plot of AQI values with blue dots
sns.scatterplot(x='Timestamp', y='AQI', data=filtered_data, alpha=0.5, color='blue', label='AQI Values')

# Plot the smoothed trend line in red
smoothed_values = lowess(filtered_data['AQI'], pd.to_numeric(filtered_data['Timestamp']), frac=0.05)
sns.lineplot(x=filtered_data['Timestamp'], y=smoothed_values[:, 1], color='red', label='Smoothed Trend')

plt.title('Smoothed Trend of AQI Values')
plt.xlabel('Date')
plt.ylabel('AQI')

# Format the x-axis ticks as dates
date_formatter = DateFormatter("%Y-%m")
plt.gca().xaxis.set_major_formatter(date_formatter)

# Adjust x-axis limits to match your data range
plt.xlim(air_quality_data['Timestamp'].min(), air_quality_data['Timestamp'].max())

plt.legend()
plt.show()

# @title Pie Chart
category_counts = air_quality_data.groupby('AQI Category').size()

# Define colors for each category
category_colors = {
    'Good': 'green',
    'Moderate': 'yellow',
    'Unhealthy for Sensitive Groups': 'orange',
    'Unhealthy': 'red',
    'Very Unhealthy': 'purple',
    'Hazardous': 'maroon'
}

# Map colors to the categories
colors = [category_colors[category] for category in category_counts.index]

# Plot a pie chart
plt.figure(figsize=(8, 8))
plt.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', colors=colors)
plt.title('Distribution of AQI Categories (2019-2023)')

plt.show()

date_time = pd.to_datetime(air_quality_data['Date (LT)'])
data = pd.DataFrame()
data['ds'] = pd.to_datetime(date_time)
data['y'] = air_quality_data['AQI']

m = Prophet()
m.fit(data)
future = m.make_future_dataframe(periods=365)
forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(15)

m.plot(forecast)

m.plot_components(forecast)

lockdowns = pd.DataFrame([
    {'holiday': 'lockdown_1', 'ds': '2020-03-13', 'lower_window': 0, 'ds_upper': '2020-09-15'},
    {'holiday': 'lockdown_2', 'ds': '2020-11-26', 'lower_window': 0, 'ds_upper': '2020-12-04'},
    {'holiday': 'Winter_Vacations_2020', 'ds': '2020-12-25', 'lower_window': 0, 'ds_upper': '2021-01-13'},
    {'holiday': 'Summer_Vacations_2021', 'ds': '2021-07-01', 'lower_window': 0, 'ds_upper': '2021-07-31'},
    {'holiday': 'Winter_Vacations_2021', 'ds': '2021-12-23', 'lower_window': 0, 'ds_upper': '2022-01-06'},
    {'holiday': 'Summer_Vacations_2022', 'ds': '2022-06-01', 'lower_window': 0, 'ds_upper': '2022-07-31'},
    {'holiday': 'Winter_Vacations_2022', 'ds': '2022-12-25', 'lower_window': 0, 'ds_upper': '2023-01-08'},
    {'holiday': 'Summer_Vacations_2023', 'ds': '2023-06-01', 'lower_window': 0, 'ds_upper': '2023-08-20'},

])
for t_col in ['ds', 'ds_upper']:
    lockdowns[t_col] = pd.to_datetime(lockdowns[t_col])
lockdowns['upper_window'] = (lockdowns['ds_upper'] - lockdowns['ds']).dt.days

m = Prophet(holidays=lockdowns)
forecast = m.fit(data).predict(future)
fig = m.plot_components(forecast)

