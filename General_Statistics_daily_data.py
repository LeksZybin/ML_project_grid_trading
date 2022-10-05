#!/usr/bin/env python
# coding: utf-8

# In[278]:


import os
import pandas as pd
import numpy as np
from tqdm import tqdm #loading bar
import zipfile
import plotly.express as px 

os.getcwd()


# In[194]:


zipname = "market_data_day.zip"

#Get unique currency pairs from filenames
with zipfile.ZipFile(zipname, 'r') as f:
    file_names = f.namelist()
    
pair_names = set([item.split("_")[1] for item in file_names])
pair_names = [x for x in pair_names if "USDT" in x]
pair_names


# In[198]:


#Read csv files and merge them into a df based on the type of currency. Store dfs in a list.
zip_file = zipfile.ZipFile(zipname)
market_data = []
names = []
for name in tqdm(pair_names):
    for info in zip_file.infolist():
        if name in info.filename:
            #PREPARE DATA
            df =  pd.read_csv(zip_file.open(info.filename), skiprows = 1, parse_dates=['date'], index_col=['date'])
            df = df.sort_index()
            #ADD_STATISTICS
            #df['...'] = ...
            df['return'] = df['open'].pct_change() ###
            df['volatility_30d'] = df['return'].rolling(30).std()*(365**0.5)
            df['volatility_90d'] = df['return'].rolling(90).std()*(365**0.5)
            df['volatility_300d'] = df['return'].rolling(300).std()*(365**0.5)
            
            #Create a key for the table in a dictionary
            names.append(name)
            
    market_data.append(df)
market_data_dictionary = dict(zip(names, market_data))


# In[201]:


market_data_dictionary['ETHUSDT']


# In[286]:


#How to join tables: https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
#Concatenate tables

#Concatenate 
def without_keys(d, keys):
    return {k: d[k] for k in d.keys() - keys}

df = pd.DataFrame(market_data_dictionary['BTCUSDT']['volatility_300d'])
new_name = "_".join(['V300d','BTCUSDT'])
df.rename(columns = { 'volatility_300d' : new_name }, inplace = True)

market_data_dictionary_wo_btc = without_keys(market_data_dictionary, ['BTCUSDT','LUNAUSDT'])

for crypto, table in market_data_dictionary_wo_btc.items():
        df2 =  pd.DataFrame(table['volatility_300d'])
        new_name = "_".join(['V300d',crypto])
        df2.rename(columns = { 'volatility_300d' : new_name }, inplace = True)
        df = pd.concat([df, df2], axis=0)
        


# In[287]:


df


# In[288]:


fig = px.line(df, x=df.index, y=df.columns[0:10])


# In[289]:


fig.show()

