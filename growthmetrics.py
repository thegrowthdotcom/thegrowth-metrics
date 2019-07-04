import numpy as np
import pandas as pd
from datetime import datetime
import sys
import time
import csv
import matplotlib.pyplot as plt
import numpy as np


def cohort_period(df):
    df['CohortPeriod'] = np.arange(len(df)) + 1
    return df

# This is the plot with two y axis.
def doubleAxisPlot(title, y1data, y2data, y1label, y2label, xlabel):
    
    #https://matplotlib.org/3.1.0/gallery/style_sheets/style_sheets_reference.html
    #https://matplotlib.org/3.1.0/gallery/text_labels_and_annotations/font_family_rc_sgskip.html
    #https://matplotlib.org/3.1.0/api/_as_gen/matplotlib.pyplot.grid.html
    #https://stackoverflow.com/questions/25973581/how-do-i-format-axis-number-format-to-thousands-with-a-comma-in-matplotlib
    
    t = np.arange(0, len(y1data), 1)
    data1 = y1data.to_numpy()
    data2 = y2data.to_numpy()
    fig, ax1 = plt.subplots()
    ax1.grid(b=True, which='major', color='#c0c0c0', axis='y', linestyle='--', zorder=0)
    ax1.set_title(str(title))
    color = '#3498db'
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['left'].set_visible(False) 
    ax1.set_xlabel(str(xlabel))
    ax1.set_ylabel(str(y1label), color=color)
    ax1.bar(t, y1data, color=color, zorder=3)
    ax1.tick_params(axis='y', labelcolor=color)
    ax2 = ax1.twinx()
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False) 
    color = '#2ecc71'
    ax2.set_ylabel(str(y2label), color=color)
    ax2.plot(t, y2data, color=color, zorder=3)
    ax2.tick_params(axis='y', labelcolor=color)
    fig.tight_layout()
    plt.savefig("output/" + str(title) + ".png", transparent=True, dpi=300, orientation='landscape')
    return

# This is the plot with a single y axis.
def singleAxisPlot(title, ydata, ylabel, xlabel):
    t = np.arange(0, len(ydata), 1)
    data1 = ydata.to_numpy()
    fig, ax1 = plt.subplots()
    ax1.grid(b=True, which='major', color='#c0c0c0', axis='y', linestyle='--', zorder=0)
    ax1.set_title(str(title))
    color = '#3498db'
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(True)
    ax1.spines['left'].set_visible(False) 
    ax1.set_xlabel(str(xlabel))
    ax1.set_ylabel(str(ylabel), color=color)
    ax1.bar(t, ydata, color=color, zorder=3)
    ax1.tick_params(axis='y', labelcolor=color)
    fig.tight_layout()
    plt.savefig("output/" + str(title) + ".png", transparent=True, dpi=300, orientation='landscape')
    return
    
''' 
    Rename paramneters.
    Price -> MRR
    CustomerId -> Subscribers
    
    Write explanations for each term in the comments.
    
    Fix the plots. Add fonts.
    
    Clean up the code.
    
    Do a 2nd version and test if it works with Prophet. That could be a passed argument, like 'predict' or similar, and it predicts half the time it has. So, if it have 10 months, it predicts 5.

    Send filename as argument?
    
    Do a try on load and save and if there is no folders, create them.
'''

def calculateChurn(row, cohorts):
    item = int(row.name)+1
    cohortdf = cohorts.iloc[0:item+1, 0:item]
    months = int(len(cohortdf))-1 
    
    churn = 0
    for i in range(months):
        h = i+1
        try:
            churn = churn + (cohortdf.iloc[item-i, i]-cohortdf.iloc[item-h, i])
        except:
            churn = churn + 0
    return churn*-1

# Calculating the Forever Transaction Indicator (FTI)
def calculateFTI(row, cohorts):
    item = int(row.name)+1
    cohortdf = cohorts.iloc[0:item+1, 0:item]
    months = int(len(cohortdf))

    start = 0
    end = 0
    posTime = 0
    acTime = 0
    for i in range(months):
        h = i+1
        try:
            months = len(cohortdf.columns)-i
            start = cohortdf.iloc[0, i]
            end = cohortdf.iloc[item-i, i]
            posTime = posTime + (start * months)
            acTime = acTime + (end * months)
        except:
            posTime = posTime + 0
            acTime = acTime + 0
    return (acTime/posTime)*100

# Load the data
df = pd.read_csv('data/sampledata.csv', sep=',', index_col = False)
df['Time'] = pd.to_datetime(df['Time'], errors='coerce') # We ensure that the ts column is a datetime col.
df['Time'] = df['Time'].dt.strftime('%Y/%m')
df['Time'] = pd.to_datetime(df['Time'], errors='coerce')

category = 'Price'
df = df[['CustomerId', 'Time', category]]

# Analyse the data
g = df.groupby(['Time']).agg({'CustomerId': 'count', category: 'sum'}).reset_index()
df.set_index('CustomerId', inplace=True)
df['CohortGroup'] = df.groupby(level=0)['Time'].min().apply(lambda x: x.strftime('%Y-%m'))
df.reset_index(inplace=True)
cohorts = df.groupby(['CohortGroup', 'Time']).agg({'CustomerId': pd.Series.nunique, category: np.sum})
cohorts.rename(columns={'CustomerId': 'TotalCustomers'}, inplace=True)
cohorts = cohorts.reset_index()
cohorts = cohorts.groupby(['CohortGroup']).apply(cohort_period)
cohort_group_size = cohorts.groupby(['CohortGroup'])['TotalCustomers'].first()
cohorts.set_index(['CohortGroup', 'CohortPeriod'], inplace=True)
subsList = cohort_group_size.values
newSubscribers = pd.DataFrame(subsList, columns=['NewSubscribers']) 
churnSubscribers = cohorts['TotalCustomers'].unstack(0)
churnSubscribers.reset_index()

# Merge the frames
subscriberdf = g.join(newSubscribers)

# Create the summarizing dataframe
subscriberdf['churnedSubscribers'] = subscriberdf.apply(calculateChurn, cohorts=churnSubscribers, axis=1)
subscriberdf['churnrate'] = (subscriberdf['churnedSubscribers']/subscriberdf['CustomerId'])*100 # TODO: 3 months rolling...?   
subscriberdf['ARPU'] = subscriberdf['Price']/subscriberdf['CustomerId']
subscriberdf['ALT'] = 100/subscriberdf['churnrate']
subscriberdf['ELTV'] = subscriberdf['ARPU']*subscriberdf['ALT']
subscriberdf['growthrate'] = ((subscriberdf['CustomerId']/subscriberdf['CustomerId'].shift(1))-1)*100
subscriberdf['FTI'] = subscriberdf.apply(calculateFTI, cohorts=churnSubscribers, axis=1)
subscriberdf = subscriberdf.fillna(0)
subscriberdf['churnedSubscribers']  = subscriberdf['churnedSubscribers'].astype(int)
subscriberdf['ALT']  = subscriberdf['ALT'].astype(int)
subscriberdf['FTI']  = subscriberdf['FTI'].astype(int)

# Remove the last month since that will, by definition, be incomplete since we don't have churn rates.
subscriberdf = subscriberdf.head(len(subscriberdf)-1)

# Save the dataframe as a csv so you can use it in other apps.
subscriberdf.to_csv("output/summary.csv")

# Plot the results
singleAxisPlot('Acquisition', subscriberdf['CustomerId'], '# of new subscribers', 'Time (months)')
singleAxisPlot('Forever Transaction Indicator', subscriberdf['FTI'], 'FTI', 'Time (months)')
doubleAxisPlot('Retention', subscriberdf['churnedSubscribers'], subscriberdf['churnrate'], '# of churned subscribers', 'Churn rate (%)', 'Time (months)')
doubleAxisPlot('Monetization', subscriberdf['ARPU'], subscriberdf['ELTV'], 'Average Revenue Per User', 'Estimated Life Time Value', 'Time (months)')
doubleAxisPlot('Growth', subscriberdf['growthrate'], subscriberdf['Price'], 'Subscriber Growth Rate (month by month)', 'Monthly Recurring Revenue', 'Time (months)')
