#!/bin/env python3
# covincidence
# Copyright (C) by AD, III 2020. All rights reserved
#
# git clone https://github.com/CSSEGISandData/COVID-19.git
#
# %%
import matplotlib as mpl
# Use MPLBACKEND=TkAgg
#mpl.use('TkAgg')
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd


# %%
# Johns Hopkins data
# https://github.com/CSSEGISandData/COVID-19
pDataFilename = '03-26-2020'
pDataBase = './COVID-19/csse_covid_19_data/'
pDataDaily = 'csse_covid_19_daily_reports/'

pImagesBase = './docs/assets/images/'

# %%
def dfLoadFile1 (fname):
    return pd.read_csv(fname,
                       header=0,
                       names=['state', 'country', 'upd', 'confirmed', 'deaths', 'recovered', 'lat', 'lon']
                       )

def dfLoadFile2 (fname):
    return pd.read_csv(fname,
                       header=0,
                       names=['fips', 'admin2', 'state', 'country', 'upd', 'lat', 'lon', 'confirmed', 'deaths', 'recovered', 'active', 'loc']
                       ). \
        groupby('country').sum()

def dfLoadDay (date):
    pass

def axRotateLabels (ax):
    for label in ax.get_xticklabels():
        label.set_rotation(40)
        label.set_horizontalalignment('right')


# %%
# https://github.com/lorey/list-of-countries
dfCountryData = pd.read_csv('./countries.csv', sep=';', index_col='name')
dfCountryData.loc['US'] = dfCountryData.loc['United States']

# %%
fDataVersion = 1
if fDataVersion == 0:
  dfCOVID = dfLoadFile1(pDataBase + pDataDaily + '03-22-2020.csv')
  dfData = pd.merge(dfCOVID, dfCountryData, how='left', left_on='country', right_on='name')
else:
  dfCOVID = dfLoadFile2(pDataBase + pDataDaily + pDataFilename + '.csv')
  #df = dfMerged.loc[dfMerged['country'].notna(), ['country', 'confirmed', 'recovered', 'deaths', 'population']]
  dfData = dfCOVID.merge(dfCountryData, how='inner', left_index=True, right_on='name')


# %%
dfData['prevalence'] = dfData['active'] / dfData['population'] * 100000
dfData['prevalence_agg'] = dfData['confirmed'] / dfData['population'] * 100000
dfData['deathrate'] = dfData['deaths'] / dfData['population'] * 100000
dfData['recoveredrate'] = dfData['recovered'] / dfData['population'] * 100000
dfData.loc['US','active'] = dfData['confirmed']['US'] - dfData['recovered']['US'] - dfData['deaths']['US']

# %%
# ########################################################################

if False:
  dfA = dfData.sort_values(by=['confirmed'], ascending=False)
else:
  dfA = dfData.sort_values(by=['active'], ascending=False)

ax = dfA.head(20).plot.barh(stacked=True, logx=False,
                            y=['active', 'recovered', 'deaths'],
                            color=('xkcd:bright blue', 'xkcd:leaf green', 'xkcd:reddish gray'),
                            title='Case numbers ('+pDataFilename+')',
                            figsize=(10,8))
# %%
ax.set_xlabel('capita')
ax.set_ylabel('Country')

#plt.show()
plt.subplot(ax)
plt.savefig(pImagesBase + 'cases.svg', format='svg')


# %%
# ########################################################################

dfB = dfData.sort_values(by='prevalence', ascending=False)
ax = dfB.head(30).plot.barh(stacked=False, logx=False,
                            y='prevalence',
                            color='xkcd:bright blue', #('xkcd:bright blue', 'xkcd:leaf green', 'xkcd:reddish gray'),
                            title='Prevalence ('+pDataFilename+')',
                            figsize=(10,8))
# %%
ax.set_xlabel('capita / 100000')
ax.set_ylabel('Country')

#plt.show()
plt.subplot(ax)
plt.savefig(pImagesBase + 'preval-r.svg', format='svg')


# %%
dfB = dfData.sort_values(by='prevalence_agg', ascending=False)
ax = dfB.head(30).plot.barh(stacked=False, logx=False,
                            y='prevalence_agg',
                            color='xkcd:bright blue', #('xkcd:bright blue', 'xkcd:leaf green', 'xkcd:reddish gray'),
                            title='Prevalence::agregate ('+pDataFilename+')',
                            figsize=(10,8))
# %%
ax.set_xlabel('capita / 100000')
ax.set_ylabel('Country')

#plt.show()
plt.subplot(ax)
plt.savefig(pImagesBase + 'preval-agg-r.svg', format='svg')


# %%
if False:
  # separate death & recovery rate
  dfC = dfData.sort_values(by='deathrate', ascending=False)
  # %%
  ax = dfC.head(30).plot.barh(stacked=False, logx=True,
                              y='deathrate',
                              color='xkcd:reddish gray', #('xkcd:bright blue', 'xkcd:leaf green', 'xkcd:reddish gray'),
                              title='Fatalities rate ('+pDataFilename+')',
                              figsize=(10,8))
  ax.set_xlabel('capita / 100000')
  ax.set_ylabel('Country')

  #plt.show()
  plt.subplot(ax)
  plt.savefig(pImagesBase + 'deaths-rl.svg', format='svg')


  # %%
  dfC = dfData.sort_values(by='recoveredrate', ascending=False)
  # %%
  ax = dfC.head(30).plot.barh(stacked=False, logx=True,
                              y='recoveredrate',
                              color='xkcd:leaf green', #, 'xkcd:reddish gray'), #('xkcd:bright blue', 'xkcd:leaf green', 'xkcd:reddish gray'),
                              title='Recovered rate ('+pDataFilename+')',
                              figsize=(10,12))
  ax.set_xlabel('capita / 100000')
  ax.set_ylabel('Country')

  #plt.show()
  plt.subplot(ax)
  plt.savefig(pImagesBase + 'recov-rl.svg', format='svg')

else:
  # combined death & recovery rate

  dfC = dfData.sort_values(by='deathrate', ascending=False)
  # %%
  ax = dfC.head(30).plot.barh(stacked=False, logx=True,
                              y=['deathrate', 'recoveredrate'],
                              color=('xkcd:reddish gray', 'xkcd:leaf green'),
                              title='Fatalities / Recovered rate ('+pDataFilename+')',
                              figsize=(10,10))
  ax.set_xlabel('capita / 100000')
  ax.set_ylabel('Country')

  #plt.show()
  plt.subplot(ax)
  plt.savefig(pImagesBase + 'deaths-recov-rl.svg', format='svg')


# %%
#dfC = dfData.sort_values(by='recoveredrate', ascending=False)
# %%


# %%
def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        width = rect.get_width()
        ax.annotate('{}'.format(width),
                    xy=(rect.get_y() + rect.get_height() / 2, width),
                    xytext=(3, 0),  # 3 points horizontal offset
                    textcoords="offset points",
                    ha='left', va='center')

#autolabel(ax)
#ax.set_yticks(dfB['deaths'])


# ############################################################################

# locator = mdates.AutoDateLocator(minticks=7)
# formatter = mdates.ConciseDateFormatter(locator)

# https://github.com/coviddata/covid-api
dftlCases = pd.read_csv('covid-api/docs/v1/countries/cases.csv', index_col=0)

dftlCasesPop = dftlCases.merge(dfCountryData['population'], how='inner', left_index=True, right_on='name')
dftlCasesPop = dftlCasesPop.apply(lambda data: data / dftlCasesPop['population'][data.index] * 100000)
dftlCasesPop = dftlCasesPop.iloc[:,0:-1]

df = dftlCasesPop.loc[['Belgium','Germany','France','Italy','Spain','South Korea','China','United States']].T

ax = df.plot.line(
                  logy=False,
                  marker='o',
                  title='Confirmed cases per 100.000 capita',
                  figsize=(13,8)
                 )

# ax.xaxis.set_major_locator(locator)
# ax.xaxis.set_major_formatter(formatter)
axRotateLabels(ax)
ax.minorticks_on()
ax.grid(axis='x', which='both', linestyle=':', color='xkcd:light gray')
ax.legend(title='Countries')
ax.set_ylabel('cases · population${}^{-1}$ · 100000')

#plt.show()
plt.subplot(ax)
plt.savefig(pImagesBase + 'tl-cases-r.svg', format='svg')

ax = df.plot.line(
                  logy=True,
                  marker='o',
                  title='Confirmed cases per 100.000 capita (log-y)',
                  figsize=(13,8)
                 )

# ax.xaxis.set_major_locator(locator)
# ax.xaxis.set_major_formatter(formatter)
axRotateLabels(ax)
ax.minorticks_on()
ax.grid(axis='x', which='both', linestyle=':', color='xkcd:light gray')
ax.legend(title='Countries')
ax.set_ylabel('cases · population${}^{-1}$ · 100000')

# %%
plt.subplot(ax)
plt.savefig(pImagesBase + 'tl-cases-rl.svg', format='svg')
plt.show()


pass
