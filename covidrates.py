#!/usr/bin/env python3
cName = 'covidrates'
cVersion = '2.1.0'
cCopyright = 'Copyright (C) by XA, III - IV 2020. All rights reserved.'
#
# * How to set it up:
#
#   #1 clone [JHUCSSE] repository
#    $ git clone -b wed-data https://github.com/CSSEGISandData/COVID-19.git
#
#   #2 clone [CovidData] repository
#    $ git clone https://github.com/coviddata/coviddata.git
#
#   #3 retrieve GeoNmes [CountryDataGN] database
#    $ wget https://download.geonames.org/export/dump/countryInfo.txt
#
#   #*
#    $ python3 ./covidrates.py -h
#
# %%
import matplotlib as mpl
# Use MPLBACKEND=TkAgg
try:
    from matplotlib import pyplot as plt
except:
    mpl.use('Agg')
    from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

import sys
import getopt
import datetime

# %%
pDataJHUData = './COVID-19/'
pDataJHUWDBase = pDataJHUData + '/data/'
pDataJHUBase = pDataJHUData + '/csse_covid_19_data/'
pDataJHUDaily = 'csse_covid_19_daily_reports/'

pDataCovidDataBase = './coviddata/'

pImagesBase = './docs/assets/images/'


def usage ():
    print(f"""\
{cName} {cVersion} -- Covid-19 data visualization
{cCopyright}

+ Usage:
    {cName} {{ -h | -[aX] | -[cprCdg] }}

    -a      -- show all graphics
    -X      -- create, but don't show

    -c      -- cases diagram
    -p      -- prevalence diagrams
    -r      -- rates diagrams
    -C      -- cases timeline
    -d      -- fatalities v cases

    -g      -- growth rates of confirmed cases
""")
    pass


fAll = False
fOptions = {
        'cases': False,
        'prevalence': False,
        'rates': False,
        'tl_cases': False,
        'deathrate': False,
        'gr_cases': False,
        'noshow': False
        }

try:
    optlist, args = getopt.gnu_getopt(sys.argv[1:], 'haXcprCdg')
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
    elif o == '-X':
        fOptions['noshow'] = True
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
    elif o == '-g':
        fOptions['gr_cases'] = True

if fAll:
    fTmp = fOptions['noshow']
    for k in fOptions.keys():
        fOptions[k] = True
    fOptions['noshow'] = fTmp



# %%
def dfLoadGeoNamesData (fname='./countryInfo.txt'):
    # https://download.geonames.org/export/dump/countryInfo.txt
    df = pd.read_csv(fname,
                     skiprows=51,
                     skip_blank_lines=True,
                     delimiter="\t",
                     header=None,
                     index_col='country',
                     names=['ISO', 'ISO3', 'ISOn', 'fips', 'country', 'capital', 'area', 'population', 'continent', 'tld', 'currencyCode', 'currencyName', 'phone', 'postalCodeFmt', 'postalCodeRegEx', 'languages', 'geonameId', 'neighbors', 'fips_equiv']
                    )
    # [FIXES] patching database glitches
    df.at['Eritrea', 'population'] = 5750433 # https://en.wikipedia.org/wiki/Eritrea
    df.loc['US'] = df.loc['United States']
    # [/FIXES]
    return df


# %%
def dfLoadCountriesDataStatJHUWDv2 (fname=pDataJHUWDBase+'cases_country.csv'):
    # https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv
    df = pd.read_csv(pDataJHUWDBase+'cases_country.csv',#fname,
                     header=0,
                     index_col='country',
                     names=['country', 'upd', 'lat', 'lon', 'confirmed', 'deaths', 'recovered', 'active']
                    )
    #Python 3.7+: tUpdate = df['upd'].apply(lambda x: pd.Timestamp.fromisoformat(x)).max()
    tUpdate = df['upd'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')).max()
    # tUpdate.tz_localize('UTC')
    return df, tUpdate.to_pydatetime()

def dfLoadCasesTLCovAPIv1 (fname=pDataCovidDataBase+'docs/v1/countries/cases.csv'):
    # https://raw.githubusercontent.com/coviddata/coviddata/master/docs/v1/countries/cases.csv
    return pd.read_csv(fname, index_col=0)


def dfLoadDataTLCovAPIv1 (fname=pDataCovidDataBase+'data/sources/jhu_csse/standardized/standardized.csv'):
    # https://raw.githubusercontent.com/coviddata/coviddata/master/data/sources/jhu_csse/standardized/standardized.csv
    return pd.read_csv(fname,
                       index_col=[0,1]
                      ) \
        .groupby(level=[0,1]).sum()


# %%
def axRotateLabels (ax):
    for label in ax.get_xticklabels():
        label.set_rotation(40)
        label.set_horizontalalignment('right')

# %%
# def autolabel(rects):
#     """Attach a text label above each bar in *rects*, displaying its height."""
#     for rect in rects:
#         width = rect.get_width()
#         ax.annotate('{}'.format(width),
#                     xy=(rect.get_y() + rect.get_height() / 2, width),
#                     xytext=(3, 0),  # 3 points horizontal offset
#                     textcoords="offset points",
#                     ha='left', va='center')


def filenamify (name):
    return name.replace(' ', '_').replace('/', '_').replace('\\', '_').replace('%', '_').replace(':', '_')


# %%
dfCountryData = dfLoadGeoNamesData()


# %%
dfCOVID, pydtUpdate = dfLoadCountriesDataStatJHUWDv2()
theDate = pydtUpdate.strftime('%Y-%m-%d')
dfData = dfCOVID.merge(dfCountryData, how='inner', left_index=True, right_index=True)

# %%
# [FIXES] patching database glitches
dfData.at['US', 'active'] = dfData.at['US', 'confirmed'] - dfData.at['US', 'recovered'] - dfData.at['US', 'deaths']
#dfData.at['United States', 'active'] = dfData.at['US', 'active']
#[/FIXES]

# %%
# Calculate additional columns
dfData['prevalence'] = dfData['active'] / dfData['population'] * 100000
dfData['prevalence_agg'] = dfData['confirmed'] / dfData['population'] * 100000
dfData['deathrate'] = dfData['deaths'] / dfData['population'] * 100000
dfData['recoveredrate'] = dfData['recovered'] / dfData['population'] * 100000
#


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
                                title='Case numbers ('+theDate+')',
                                figsize=(10,8))
    # %%
    ax.set_xlabel('capita')
    ax.set_ylabel('Country')

    if not fOptions['noshow']: plt.subplot(ax)
    plt.savefig(pImagesBase + 'cases.svg', format='svg')




# %%
# ########################################################################

if fOptions['prevalence']:

    dfB = dfData.sort_values(by='prevalence', ascending=False)
    ax = dfB.head(30).plot.barh(stacked=False, logx=False,
                                y='prevalence',
                                color='xkcd:bright blue',
                                title='Prevalence ('+theDate+')',
                                figsize=(10,8))
    # %%
    ax.set_xlabel('capita / 100000')
    ax.set_ylabel('Country')

    plt.subplot(ax)
    plt.savefig(pImagesBase + 'preval-r.svg', format='svg')


    # %%
    dfB = dfData.sort_values(by='prevalence_agg', ascending=False)
    ax = dfB.head(30).plot.barh(stacked=False, logx=False,
                                y='prevalence_agg',
                                color='xkcd:bright blue',
                                title='Prevalence::agregate ('+theDate+')',
                                figsize=(10,8))
    # %%
    ax.set_xlabel('capita / 100000')
    ax.set_ylabel('Country')

    if not fOptions['noshow']: plt.subplot(ax)
    plt.savefig(pImagesBase + 'preval-agg-r.svg', format='svg')


# %%
if fOptions['rates']:

    if False:
      # separate death & recovery rate
      dfC = dfData.sort_values(by='deathrate', ascending=False)
      # %%
      ax = dfC.head(30).plot.barh(stacked=False, logx=True,
                                  y='deathrate',
                                  color='xkcd:reddish gray',
                                  title='Fatalities rate ('+theDate+')',
                                  figsize=(10,8))
      ax.set_xlabel('capita / 100000')
      ax.set_ylabel('Country')

      if not fOptions['noshow']: plt.subplot(ax)
      plt.savefig(pImagesBase + 'deaths-rl.svg', format='svg')


      # %%
      dfC = dfData.sort_values(by='recoveredrate', ascending=False)
      # %%
      ax = dfC.head(30).plot.barh(stacked=False, logx=True,
                                  y='recoveredrate',
                                  color='xkcd:leaf green', #, 'xkcd:reddish gray'), #('xkcd:bright blue', 'xkcd:leaf green', 'xkcd:reddish gray'),
                                  title='Recovered rate ('+theDate+')',
                                  figsize=(10,12))
      ax.set_xlabel('capita / 100000')
      ax.set_ylabel('Country')

      if not fOptions['noshow']: plt.subplot(ax)
      plt.savefig(pImagesBase + 'recov-rl.svg', format='svg')

    else:
      # combined death & recovery rate

      dfC = dfData.sort_values(by='deathrate', ascending=False)
      # %%
      ax = dfC.head(30).plot.barh(stacked=False, logx=True,
                                  y=['deathrate', 'recoveredrate'],
                                  color=('xkcd:reddish gray', 'xkcd:leaf green'),
                                  title='Fatalities / Recovered rate ('+theDate+')',
                                  figsize=(10,10))
      ax.set_xlabel('capita / 100000')
      ax.set_ylabel('Country')

      if not fOptions['noshow']: plt.subplot(ax)
      plt.savefig(pImagesBase + 'deaths-recov-rl.svg', format='svg')



# %%
#dfC = dfData.sort_values(by='recoveredrate', ascending=False)
# %%


if not fOptions['noshow']: plt.show()


# ############################################################################

if fOptions['deathrate']:

    dfD = dfData[dfData.notna()['confirmed']]
    maxCases = dfD['population'].max()
    ax = dfD.plot.scatter(
                    x='confirmed',
                    y='deaths',
                    s=dfD['population'] / maxCases * 750,
                    logx=True, logy=True,
                    title='Confirmed cases versus fatalities ('+theDate+')',
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
        # NB: this is slow!
        cData = dfD.loc[c]
        x = cData['confirmed']
        y = cData['deaths']
        rnd = np.random.random() * 40 - 20
        ax.text(x, y, c, rotation=20+rnd, size=9)


    # %%
    if not fOptions['noshow']: plt.subplot(ax)
    plt.savefig(pImagesBase + 'cases-deaths-ll.svg', format='svg')




# ############################################################################

# locator = mdates.AutoDateLocator(minticks=7)
# formatter = mdates.ConciseDateFormatter(locator)

if fOptions['tl_cases']:
    dftlCases = dfLoadCasesTLCovAPIv1()
    strDate = dftlCases.iloc[:,-1].name

    dftlCasesPop = dftlCases.merge(dfCountryData['population'], how='inner', left_index=True, right_index=True)
    dftlCasesPop = dftlCasesPop.apply(lambda data: data / dftlCasesPop['population'][data.index] * 100000)
    dftlCasesPop = dftlCasesPop.iloc[:,0:-1]

    df = dftlCasesPop.loc[['Belgium','Germany','Switzerland','France','Italy','Spain','Japan','South Korea','China','United States']].T

    ax = df.plot.line(
                      logy=False,
                      marker='o',
                      title='Confirmed cases per 100.000 capita ('+strDate+')',
                      figsize=(13,8)
                     )

    # ax.xaxis.set_major_locator(locator)
    # ax.xaxis.set_major_formatter(formatter)
    axRotateLabels(ax)
    ax.minorticks_on()
    ax.grid(axis='x', which='both', linestyle=':', color='xkcd:light gray')
    ax.legend(title='Countries')
    ax.set_ylabel('cases · population${}^{-1}$ · 100000')

    if not fOptions['noshow']: plt.subplot(ax)
    plt.savefig(pImagesBase + 'tl-cases-r.svg', format='svg')

    ax = df.plot.line(
                      logy=True,
                      marker='o',
                      title='Confirmed cases per 100.000 capita (log-y) ('+strDate+')',
                      figsize=(13,8)
                     )

    X = df.index
    Y = np.linspace(0, df.index.size-1, num=df.index.size)
    # c = df.loc[df.index.min()].max()
    c = df.loc[df.index.min()]['South Korea']

    ax.plot(X, c * 2**(Y/10), linestyle=':', color='xkcd:sky blue')
    ax.plot(X, c * 2**(Y/4), linestyle=':', color='xkcd:light red')
    ax.plot(X, c * 2**(Y/2), linestyle=':', color='xkcd:reddish gray')

    # ax.xaxis.set_major_locator(locator)
    # ax.xaxis.set_major_formatter(formatter)
    axRotateLabels(ax)
    ax.minorticks_on()
    ax.grid(axis='x', which='both', linestyle=':', color='xkcd:light gray')
    ax.legend(title='Countries')
    ax.set_ylabel('cases · population${}^{-1}$ · 100000')

    # %%
    if not fOptions['noshow']: plt.subplot(ax)
    plt.savefig(pImagesBase + 'tl-cases-rl.svg', format='svg')



# ############################################################################

if fOptions['gr_cases']:
    dftlCases = dfLoadCasesTLCovAPIv1()
    strDateFirst = dftlCases.iloc[:,0].name
    strDateLast = dftlCases.iloc[:,-1].name
    dftlCases = dftlCases.loc[['Belgium','Germany','Switzerland','France','Italy','Spain','Japan','South Korea','China','United States']].T

    #plt.subplots(6, 1)
    countries = ('Germany','Belgium','Switzerland','Italy','Spain','China','United States')

    for country in countries:
        dfCountry = pd.DataFrame(dftlCases.loc[:,country])

        for d in (2, 4, 7, 14):
          dfCountry = dfCountry.join(
                    dftlCases.loc[:,country].rename("{:d} days".format(d)) \
                    .rolling(window=d+1, center=False) \
                    #.apply(lambda v: (v[d]/v[0])**(1./d), raw=True)
                    .apply(lambda v: ((v[d]/v[0])**(1./d)-1)*100, raw=True) # percent
                )

        ax = dfCountry.iloc[:,1:].plot.line(
                    logy=False,
                    marker='o',
                    title='Confirmed cases, daily growth rate in {:s} ({:s}..{:s})'.format(country, strDateFirst, strDateLast),
                    #title='Confirmed cases, growth rate in '+country+' ('+strDateFirst+'..'+strDateLast+')',
                    figsize=(13,8)
                )
        ax.minorticks_on()
        ax.grid(axis='both', which='both', linestyle=':', color='xkcd:light gray')
        fo.ax.set_ylabel('(backw avg) growth in percent per day')
        ax.legend(title='Avg over $n$ days')

        if not fOptions['noshow']: plt.subplot(ax)
        plt.savefig(pImagesBase + 'tl-rates-confirmed-{:s}.svg'.format(filenamify(country)), format='svg')


    # ##

    dftlCases = dfLoadCasesTLCovAPIv1(pDataCovidDataBase+'docs/v1/countries/deaths.csv')
    strDateFirst = dftlCases.iloc[:,0].name
    strDateLast = dftlCases.iloc[:,-1].name
    dftlCases = dftlCases.loc[['Belgium','Germany','Switzerland','France','Italy','Spain','Japan','South Korea','China','United States']].T

    #plt.subplots(6, 1)
    countries = ('Germany','Belgium','Switzerland','Italy','Spain','China','United States')

    for country in countries:
        dfCountry = pd.DataFrame(dftlCases.loc[:,country])

        for d in (2, 4, 7, 14):
          dfCountry = dfCountry.join(
                    dftlCases.loc[:,country].rename("{:d} days".format(d)) \
                    .rolling(window=d+1, center=False) \
                    #.apply(lambda v: (v[d]/v[0])**(1./d), raw=True)
                    .apply(lambda v: ((v[d]/v[0])**(1./d)-1)*100, raw=True) # percent
                )

        ax = dfCountry.iloc[:,1:].plot.line(
                    logy=False,
                    marker='o',
                    title='Fatalities, daily growth rate in {:s} ({:s}..{:s})'.format(country, strDateFirst, strDateLast),
                    #title='Confirmed cases, growth rate in '+country+' ('+strDateFirst+'..'+strDateLast+')',
                    figsize=(13,8)
                )
        ax.minorticks_on()
        ax.grid(axis='both', which='both', linestyle=':', color='xkcd:light gray')
        fo.ax.set_ylabel('(backw avg) growth in percent per day')
        ax.legend(title='Avg over $n$ days')

        if not fOptions['noshow']: plt.subplot(ax)
        plt.savefig(pImagesBase + 'tl-rates-deaths-{:s}.svg'.format(filenamify(country)), format='svg')



#plt.subplots()

if not fOptions['noshow']: plt.show()
