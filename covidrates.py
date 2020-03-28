#!/bin/env python3
cName = 'covidrates'
cVersion = '1.0.0'
cCopyright = 'Copyright (C) by XA, III 2020. All rights reserved.'
#
# How to set it up:
#  $ git clone https://github.com/CSSEGISandData/COVID-19.git
#  $ git clone https://github.com/coviddata/covid-api.git
#  $ wget https://raw.githubusercontent.com/lorey/list-of-countries/master/csv/countries.csv
#  $ python3 ./covidrates.py
#
# %%
import matplotlib as mpl
# Use MPLBACKEND=TkAgg
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

import sys
import getopt


# %%
# Johns Hopkins data
# https://github.com/CSSEGISandData/COVID-19
pDataFilename = '03-27-2020'
pDataBase = './COVID-19/csse_covid_19_data/'
pDataDaily = 'csse_covid_19_daily_reports/'

pImagesBase = './docs/assets/images/'


def usage ():
    print(f"""\
{cName} {cVersion} -- Covid-19 data visualization
{cCopyright}

+ Usage:
    {cName} {{ -h | -a | -cprCd }}

    -a      -- show all graphics

    -c      -- cases diagram
    -p      -- prevalence diagrams
    -r      -- rates diagrams
    -C      -- cases timeline
    -d      -- fatalities v cases
""")
    pass


fAll = False
fOptions = {
        'cases': False,
        'prevalence': False,
        'rates': False,
        'tl_cases': False,
        'deathrate': False,
        'dummy': False
        }

try:
    optlist, args = getopt.gnu_getopt(sys.argv[1:], 'hacprCd')
except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)

for o, a in optlist:
    if o == '-h':
        usage()
        sys.exit(2)
    elif o == '-a':
        fAll = True
    elif o == '-c':
        fOptions['cases'] = True
    elif o == '-p':
        fOptions['prevalence'] = True
    elif o == '-r':
        fOptions['rates'] = True
    elif o == '-C':
        fOptions['tl_cases'] = True
    elif o == '-d':
        fOptions['deathrate'] = True


if fAll:
    for k in fOptions.keys():
        fOptions[k] = True


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
#
dfData.loc['US','active'] = dfData['confirmed']['US'] - dfData['recovered']['US'] - dfData['deaths']['US']
#dfData.loc['United States','active'] = dfData.loc['US','active']


# %%
# ########################################################################
if fOptions['cases']:

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

if fOptions['prevalence']:

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
if fOptions['rates']:

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

if fOptions['deathrate']:

    dfD = dfData[dfData.notna()['confirmed']]
    maxCases = dfD['population'].max()
    ax = dfD.plot.scatter(
                    x='confirmed',
                    y='deaths',
                    s=dfD['population'] / maxCases * 750,
                    logx=True, logy=True,
                    title='Confirmed cases versus fatalities',
                    figsize=(13,8)
    )

    ax.set_xlabel('confirmed cases')
    ax.set_ylabel('fatalities')
    ax.grid(which='major', linestyle=':', color='xkcd:light gray')
    ax.set_xlim(xmin=1)
    ax.set_ylim(ymin=1)

    X = np.linspace(1,maxCases)
    ax.plot(X, 0.001 * X, linestyle=':', color='xkcd:sky blue')
    ax.plot(X, 0.004 * X, linestyle='-', color='xkcd:leaf green')
    ax.plot(X, 0.01 * X, linestyle='-', color='#4040FF')
    ax.plot(X, 0.025 * X, linestyle=':', color='xkcd:grey')
    ax.plot(X, 0.04 * X, linestyle='-', color='#FF4040')
    ax.plot(X, 0.11 * X, linestyle=':', color='xkcd:light purple')

    for c in dfD.index:
        cData = dfD.loc[c]
        x = cData['confirmed']
        y = cData['deaths']
        rnd = np.random.random() * 40 - 20
        ax.text(x, y, c, rotation=20+rnd, size=9)



    # %%
    plt.subplot(ax)
    plt.savefig(pImagesBase + 'cases-deaths-ll.svg', format='svg')




# ############################################################################

# locator = mdates.AutoDateLocator(minticks=7)
# formatter = mdates.ConciseDateFormatter(locator)

if fOptions['tl_cases']:
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
