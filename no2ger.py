#%%
import streamlit as st
import pandas as pd
from datetime import datetime, date
import numpy as np
import plotly.express as px
st.set_page_config(layout="wide", page_title= 'Diverse grafer', page_icon= "lightning")
st.title('Grafer over prisdifferanse NO2 og Tyskland')

prices = pd.read_csv('noger.csv')
prices.rename(columns= {'Datetime (UTC)': 'date'}, inplace=True)
prices['date'] = pd.to_datetime(prices['date'], format='%Y-%m-%d %H:%M:%S')

@st.cache
def load_data2(ttl= 86400):
    df_15 = pd.read_csv('no2_2015.csv')
    df_16 = pd.read_csv('no2_2016.csv')
    df_17 = pd.read_csv('no2_2017.csv')
    df_18 = pd.read_csv('no2_2018.csv')
    df_19 = pd.read_csv('no2_2019.csv')
    df_20 = pd.read_csv('no2_2020.csv')
    df_21 = pd.read_csv('no2_2021.csv')
    df_22 = pd.read_csv('no2_2022.csv')
    pdList = [df_15, df_16, df_17, df_18, df_19, df_20, df_21, df_22 ]
    df = pd.concat(pdList)
    df = df.reset_index().drop('index', axis = 1)
    df['date'] =  df['MTU (UTC)'].str[:16]
    df = df.rename(columns={'Day-ahead Price [EUR/MWh]':'price_no2'})[['date','price_no2']]
    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y %H:%M')
    return df

df = load_data2()
df_prices = pd.merge(df, prices, on = 'date')
df_long = pd.melt(df_prices, id_vars='date', value_vars=['price_no2', 'price_nor', 'price_ger'])
df_long = df_long[(df_long['variable'] == 'price_no2') | (df_long['variable'] == 'price_ger') ]

fig_price =px.line(df_long, y='value', x='date', color='variable', template='plotly_white')
fig_price.add_vline(x='2021-03-31 00:00:00', line_width=3, line_dash="dash", line_color="green")
fig_price.update_traces(opacity=0.5)
st.write('Priser i EUR/MWH, vertikal linje for kommersiell start av Nordlink')
st.plotly_chart(fig_price, use_container_width=True)
# %%
df_prices['no2_ger'] = df_prices['price_no2']-df_prices['price_ger']
df_prices['year'] = df_prices['date'].dt.year
df_prices['date_hour'] = df_prices['date'].dt.strftime('%d-%m-%H')
df_prices_diff = df_prices[['no2_ger','year','date_hour']]
df_price_wide = pd.pivot_table(df_prices_diff, index= 'date_hour', columns= 'year',values = 'no2_ger')
df_price_wide = df_price_wide.reset_index(drop = True)
## Sort columns by value independently of each other https://stackoverflow.com/questions/43280322/sort-all-columns-of-a-pandas-dataframe-independently-using-sort-values
df_price_wide = pd.DataFrame(np.sort(df_price_wide.values, axis=0), index=df_price_wide.index, columns=df_price_wide.columns)
df_price_wide['index'] = range(len(df_price_wide))
df_prices_diff = pd.melt(df_price_wide, id_vars='index', value_vars=[2015, 2016,2017,2018,2019,2020,2021,2022])
df_prices_diff.rename(columns={'value': 'no2_ger'}, inplace=True)
fig_diff =px.line(df_prices_diff, y='no2_ger', x='index', color='year', template='plotly_white')
fig_diff.update_traces(opacity=0.5)
st.plotly_chart(fig_diff, use_container_width=True)
# %%
df_prices_diff[df_prices_diff['no2_ger'] == 0]['year'].value_counts()
df_prices_diff[(df_prices_diff['no2_ger'] < 1) & (df_prices_diff['no2_ger'] > -1)]['year'].value_counts()
diff = df_prices_diff[df_prices_diff['no2_ger'] == 0]['year'].value_counts()
diff =pd.DataFrame(diff).rename(columns={'year':'timer uten prisforskjell'})
st.header('Antall timer med prislikhet mellom NO2 og GER')
st.dataframe(diff)
