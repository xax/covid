#!/usr/bin/env python3
cName = 'covid2xa'
cVersion = '4.6.2'
cCopyright = 'Copyright (C) by XA, III - X 2020. All rights reserved.'
#
# * Preparation to environment
#
#   #0 create virtual environment (optional)
#    $ python -m venv ./.venv
#    $ source ./.venv/bin/activate
#
#   #1 install dependencies
#    $ pip install numpy matplotlib pandas
#    $ pip install adjustText  # (optional)
#
#   #2 install Tk and Tk-python bindings to enable matplotlib
#      to display figures in GUI
#    $ sudo apt-get install python3-tk  # (Debian'ish)
#    $ sudo dnf install python3-tkinter # (Fedora-flavoured)
#    $ sudo pacman -S tk                # (Arch)
#
# * How to set it up:
#
#   #1 clone [JHUCSSE] repository
#    $ git clone --depth=1 -b web-data https://github.com/CSSEGISandData/COVID-19.git
#
#   #2 clone [CovidData] repository
#    $ git clone --depth=1 https://github.com/coviddata/coviddata.git
#
#   #3 retrieve GeoNmes [CountryDataGN] database
#    $ wget https://download.geonames.org/export/dump/countryInfo.txt
#
#   #*
#    $ python3 ./covidrates.py -h
#
# %%
import numpy as np
import pandas as pd

import sys
import getopt
import datetime



# %%
class rcConfig:
    """ Configuration data static. """

    def __init__ (self): raise Exception("This class is static only!")

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
    {cName} {{ -h | -[aXY] | -[cprCdgz] }}

    -a      -- show all graphics
    -X      -- create, but don't show
    -Y      -- don't spend time on trying to arrange labels

    -c      -- cases diagram
    -p      -- prevalence diagrams
    -r      -- rates diagrams
    -C      -- cases timeline
    -d      -- fatalities v cases

    -g      -- growth rates of confirmed cases
    -z      -- growth of confirmed cases on a relative timeline
""")
    pass


fTasks = {
        'cases': False,
        'prevalence': False,
        'rates': False,
        'tl_cases': False,
        'deathrate': False,
        'gr_cases': False,
        'gr_zeroday_cases': False,
        }
fOptions = {
        'all': False,
        'noshow': False,
        'hasAdjustText': True,
        }


def parseOptions (fOptions, fTasks):
    ''' Parse command line options into passed `fOptions` and `fTasks`. '''
    try:
        optlist, args = getopt.gnu_getopt(sys.argv[1:], 'haXYcprCdgz')
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    fAll = False
    for o, a in optlist:
        if o == '-h':
            usage()
            sys.exit(2)
        elif o == '-a':
            fAll = True
            fOptions['all'] = True
        elif o == '-X':
            fOptions['noshow'] = True
        elif o == '-Y':
            fTasks['hasAdjustText'] = False
        elif o == '-c':
            fTasks['cases'] = True
        elif o == '-p':
            fTasks['prevalence'] = True
        elif o == '-r':
            fTasks['rates'] = True
        elif o == '-C':
            fTasks['tl_cases'] = True
        elif o == '-d':
            fTasks['deathrate'] = True
        elif o == '-g':
            fTasks['gr_cases'] = True
        elif o == '-z':
            fTasks['gr_zeroday_cases'] = True

    if fAll:
        for k in fTasks.keys():
            fTasks[k] = True

    return fOptions, fTasks

parseOptions(fOptions, fTasks)


# %%
try:
    if fOptions['hasAdjustText']:
      import adjustText
except:
    fOptions['hasAdjustText'] = False

import matplotlib as mpl
import matplotlib.dates as mdates
# Use MPLBACKEND=TkAgg
if fOptions['noshow']:
      mpl.use('Agg')
      from matplotlib import pyplot as plt
else:
  try:
      from matplotlib import pyplot as plt
  except:
      mpl.use('Agg')
      from matplotlib import pyplot as plt


# %%
def dfLoadGeoNamesData (fname='./countryInfo.txt'):
    ''' Load country specific data from GeoNames database.
        # https://download.geonames.org/export/dump/countryInfo.txt
    '''
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
def dfLoadCountriesDataStatJHUWDv2 (fname=rcConfig.pDataJHUWDBase+'cases_country.csv'):
    ''' Load JHU `cases per country` snapshot data .
        # https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv
    '''
    df = pd.read_csv(rcConfig.pDataJHUWDBase+'cases_country.csv',#fname,
                     header=0,
                     index_col=1,
                     # v2: Country_Region,Last_Update,Lat,Long_,Confirmed,Deaths,Recovered,Active
                     names=['country', 'upd', 'lat', 'lon', 'confirmed', 'deaths', 'recovered', 'active']
                    )
    #Python 3.7+: tUpdate = df['upd'].apply(lambda x: pd.Timestamp.fromisoformat(x)).max()
    tUpdate = df['upd'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')).max()
    # tUpdate.tz_localize('UTC')
    return df, tUpdate.to_pydatetime()


def dfLoadCountriesDataStatJHUWDv3 (fname=rcConfig.pDataJHUWDBase+'cases_country.csv'):
    ''' Load JHU `cases per country` snapshot data .
        # https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv
    '''
    df = pd.read_csv(rcConfig.pDataJHUWDBase+'cases_country.csv',#fname,
                     header=0,
                     index_col=0, #'country',
                     # v3: Country_Region,Last_Update,Lat,Long_,Confirmed,Deaths,Recovered,Active,Incident_Rate,People_Tested,People_Hospitalized,Mortality_Rate,UID,ISO3
                     names=['country', 'upd', 'lat', 'lon', 'confirmed', 'deaths', 'recovered', 'active', 'incidencerate', 'tested', 'hospitalized', 'mortalityrate', 'uid', 'cocoISO3']
                    )
    #Python 3.7+: tUpdate = df['upd'].apply(lambda x: pd.Timestamp.fromisoformat(x)).max()
    tUpdate = df['upd'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')).max()
    # tUpdate.tz_localize('UTC')
    return df, tUpdate.to_pydatetime()


dfLoadCountriesDataStatJHUWD = dfLoadCountriesDataStatJHUWDv3


def dfLoadCasesTLCovAPIv1 (fname=rcConfig.pDataCovidDataBase+'docs/v1/countries/cases.csv'):
    ''' Load coviddata preprocessed JHU `cases` per country timeline data.
        # https://raw.githubusercontent.com/coviddata/coviddata/master/docs/v1/countries/cases.csv
    '''
    return pd.read_csv(fname, index_col=0)


# def dfLoadDataTLCovAPIv1 (fname=rcConfig.pDataCovidDataBase+'data/sources/jhu_csse/standardized/standardized.csv'):
#     # https://raw.githubusercontent.com/coviddata/coviddata/master/data/sources/jhu_csse/standardized/standardized.csv
#     return pd.read_csv(fname,
#                        index_col=[0,1]
#                       ) \
#         .groupby(level=[0,1]).sum()



# %%
def provideLocPerData (dfCOVID, dfCountryData):
    df = dfCOVID.merge(dfCountryData, how='inner', left_index=True, right_index=True)
    # [FIXES] patching database glitches
    df.at['US', 'active'] = df.at['US', 'confirmed'] - df.at['US', 'recovered'] - df.at['US', 'deaths']
    # df.at['United States', 'active'] = df.at['US', 'active']
    # [/FIXES]
    return df


def provideTLPerCountry (dftlCases, countries):
    df = dftlCases.loc[countries].T
    return df



class FigureObj(object):
    ''' Class representing MATPlotLib Figure with Axes.
        Construct and show dependend on `fOptions['noshow']`;
        manage lifetime.
    '''
    __slots__ = ['_fig', '_ax']

    def __init__ (self, nRows=1, nCols=1, **kwargs):
        if fOptions['noshow']:
            self._fig = mpl.figure.Figure()
            self._ax = self._fig.subplots(nRows, nCols, **kwargs)
        else:
            self._fig, self._ax = plt.subplots(nRows, nCols, **kwargs)

    def __del__ (self):
        # DBG: print('OBJ DEL', self)
        del self._ax
        del self._fig
        self._ax = None
        self._fig = None

    @property
    def fig(self):
        return self._fig

    @fig.setter
    def fig(self, val):
        self._fig = val

    @property
    def ax(self):
        return self._ax

    @ax.setter
    def ax(self, val):
        self._ax = val

    def axs(self, n):
        return self._ax[n]

    def _sanitizeFName (fName):
        # NB: Not secure™!
        return fName \
            .replace(' ', '_').replace("'", '_').replace('"', '_') \
            .replace(':', '_').replace('/', '_').replace('\\', '_') \
            .replace('%', '_').replace('$', '_').replace('`', '_') \
            .replace('>', '_').replace('<', '_').replace('|', '_')

    def clear(self):
        self._fig.clear()

    def show(self, fName=None, noshow=None, pause=True, pBase=None, format='svg'):
        if fName is not None:
            if pBase is None: pBase = rcConfig.pImagesBase
            # [QUIRK]
            for cntRetry in range(4):
                try:
                    self._fig.savefig(pBase + __class__._sanitizeFName(fName), format=format)
                except OSError as e:  # catch sporadic OSErrors - some race condition?
                    if e.errno != 22: # errno.???
                        raise  # re-raise if unrelated exception
                    #print("OSError {:n} on 'savefig' regarding '{:s}' ('{:s}')".format(e.errno, e.filename or '', e.filename2 or ''), file=sys.stderr, flush=True)
                    print("OSError {:n} on 'savefig': {}\nRetry #{:n}...".format(e.errno, e, cntRetry), file=sys.stderr, flush=True)
                else:  # break from re-try loop on success
                    break
            else:  # out of tries
                print("Multiple OSErrors on 'savefig' - even tried multiple times.", file=sys.stderr, flush=True)
                raise OSError()
            # [/QUIRK]
        if fOptions['noshow']:
            pass
        else:
            if noshow is not True:
                plt.subplot(self._fig.gca())

    def axRotateLabels(self):
        for label in self._ax.get_xticklabels():
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



# %%
dfCountryData = dfLoadGeoNamesData()

# %%
dfCOVID, pydtUpdate = dfLoadCountriesDataStatJHUWD()
theDate = pydtUpdate.strftime('%Y-%m-%d')
dfData = provideLocPerData(dfCOVID, dfCountryData)


# %%
# Calculate additional columns
dfData['prevalence'] = dfData['active'] / dfData['population'] * 100000
dfData['prevalence_agg'] = dfData['confirmed'] / dfData['population'] * 100000
dfData['deathrate'] = dfData['deaths'] / dfData['population'] * 100000
dfData['recoveredrate'] = dfData['recovered'] / dfData['population'] * 100000
#


# %%
# ########################################################################
if fTasks['cases']:

    if False:
        dfA = dfData.sort_values(by=['confirmed'], ascending=False)
    else:
        dfA = dfData.sort_values(by=['active'], ascending=False)
    dfA = dfA.head(20)
    # [FIXES] force appearance of China
    if not dfA.index.isin(['China']).any(): dfA = dfA.append(dfData.loc['China',:])
    # [/FIXES]

    fo = FigureObj()

    dfA.plot(ax=fo.ax, kind='barh', stacked=True, logx=False,
             y=['active', 'recovered', 'deaths'],
             color=('xkcd:bright blue', 'xkcd:leaf green', 'xkcd:reddish gray'),
             title='Case numbers ('+theDate+')',
             figsize=(10,8))

    # %%
    fo.ax.set_xlabel('capita')
    fo.ax.set_ylabel('Country')

    fo.show('cases.svg')




# %%
# ########################################################################

if fTasks['prevalence']:

    # fo = FigureObj(2, 1) # fo.ax[0]… fo.ax[1]…

    dfB = dfData.sort_values(by='prevalence', ascending=False)
    dfB = dfB.head(30)
    # [FIXES] force appearance of China
    # if not dfB.index.isin(['China']).any(): dfB = dfB.append(dfData.loc['China',:])
    # [/FIXES]

    fo = FigureObj()
    dfB.plot(ax=fo.ax, kind='barh', stacked=False, logx=False,
             y='prevalence',
             color='xkcd:bright blue',
             title='Prevalence ('+theDate+')',
             figsize=(10,8))
    # %%
    fo.ax.set_xlabel('capita / 100000')
    fo.ax.set_ylabel('Country')

    fo.show('preval-r.svg')


    # %%
    dfB = dfData.sort_values(by='prevalence_agg', ascending=False)
    dfB = dfB.head(30)
    # [FIXES] force appearance of China
    if not dfB.index.isin(['China']).any(): dfB = dfB.append(dfData.loc['China',:])
    # [/FIXES]

    fo = FigureObj()
    dfB.plot(ax=fo.ax, kind='barh', stacked=False, logx=False,
             y='prevalence_agg',
             color='xkcd:bright blue',
             title='Prevalence::agregate ('+theDate+')',
             figsize=(10,8))

    fo.ax.set_xlabel('capita / 100000')
    fo.ax.set_ylabel('Country')

    fo.show('preval-agg-r.svg')


# %%
if fTasks['rates']:

     # combined death & recovery rate

    dfC = dfData.sort_values(by='deathrate', ascending=False)
    dfC = dfC.head(30)
    # [FIXES] force appearance of China
    if not dfC.index.isin(['China']).any(): dfC = dfC.append(dfData.loc['China',:])
    # [/FIXES]

    # %%
    fo = FigureObj()
    dfC.plot(ax=fo.ax, kind='barh',
             stacked=False, logx=True,
             y=['deathrate', 'recoveredrate'],
             color=('xkcd:reddish gray', 'xkcd:leaf green'),
             title='Fatalities / Recovered rate ('+theDate+')',
             figsize=(10,10))

    fo.ax.set_xlabel('capita / 100000')
    fo.ax.set_ylabel('Country')

    fo.show('deaths-recov-rl.svg')



# %%
#dfC = dfData.sort_values(by='recoveredrate', ascending=False)
# %%




# ############################################################################

if fTasks['deathrate']:

    dfD = dfData[dfData.notna()['confirmed']]
    maxCases = dfD['population'].max()

    fo = FigureObj()
    dfD.plot(ax=fo.ax, kind='scatter',
             x='confirmed',
             y='deaths',
             s=dfD['population'] / maxCases * 750,
             logx=True, logy=True,
             title='Confirmed cases versus fatalities ('+theDate+')',
             figsize=(13,8)
    )

    fo.ax.set_xlabel('confirmed cases')
    fo.ax.set_ylabel('fatalities')
    fo.ax.grid(which='major', linestyle=':', color='xkcd:light gray')
    fo.ax.set_xlim(xmin=1)
    fo.ax.set_ylim(ymin=1)

    X = np.linspace(1,maxCases)
    fo.ax.plot(X, 0.001 * X, linestyle=':', color='xkcd:sky blue')
    fo.ax.plot(X, 0.004 * X, linestyle='-', color='xkcd:leaf green')
    fo.ax.plot(X, 0.01 * X, linestyle='-', color='#4040FF')
    fo.ax.plot(X, 0.025 * X, linestyle=':', color='xkcd:grey')
    fo.ax.plot(X, 0.04 * X, linestyle='-', color='#FF4040')
    fo.ax.plot(X, 0.11 * X, linestyle=':', color='xkcd:light purple')

    if fOptions['hasAdjustText']:
        df = dfD.sort_values(by='deaths',ascending=False)
        df = df[df.deaths > 1]
        df = df[df.confirmed > 10]
        texts = []
        for r in df.head(80).itertuples():
            text = fo.ax.text(r.confirmed, r.deaths, r.Index, size=9)
            texts.append(text)
        for r in df.tail(-80).itertuples():
            rnd = np.random.random() * 40 - 20
            fo.ax.text(r.confirmed, r.deaths, r.Index, rotation=20+rnd, size=9)
        if fOptions['noshow']:
            import matplotlib.backend_bases
            fo.fig.canvas.renderer = matplotlib.backend_bases.RendererBase()
        adjustText.adjust_text(texts, ax=fo.ax, lim=20, arrowprops=dict(arrowstyle='->', color='orange'))
    else:
        for r in dfD.itertuples():
            rnd = np.random.random() * 40 - 20
            texts.append(fo.ax.text(r.confirmed, r.deaths, r.Index, rotation=20+rnd, size=9))

    # %%
    fo.show('cases-deaths-ll.svg')


# ############################################################################

# locator = mdates.AutoDateLocator(minticks=7)
# formatter = mdates.ConciseDateFormatter(locator)

if fTasks['tl_cases']:
    dftlCases = dfLoadCasesTLCovAPIv1()
    strDate = dftlCases.iloc[:,-1].name

    dftlCasesPop = dftlCases.merge(dfCountryData['population'], how='inner', left_index=True, right_index=True)
    dftlCasesPop = dftlCasesPop.apply(lambda data: data / dftlCasesPop['population'][data.index] * 100000)
    dftlCasesPop = dftlCasesPop.iloc[:,0:-1]

    df = dftlCasesPop.loc[['Germany','Belgium','Netherlands','Switzerland','France','Italy','Spain','United Kingdom','United States','Japan','South Korea','China']].T

    fo = FigureObj()
    df.plot(ax=fo.ax,kind='line',
            logy=False,
            marker='|',
            title='Confirmed cases per 100.000 capita ('+strDate+')',
            figsize=(13,8)
           )

    X = df.index
    Y = np.linspace(0, df.index.size-1, num=df.index.size)
    # c = df.loc[df.index.min()].max()
    c = df.loc[df.index.min()]['South Korea']

    fo.ax.set_ylim(ymax=(df.max().max() // 50 + 1) * 50)
    fo.ax.plot(X, c * 2**(Y/10), linestyle=':', color='xkcd:sky blue')
    fo.ax.plot(X, c * 2**(Y/4), linestyle=':', color='xkcd:light red')
    fo.ax.plot(X, c * 2**(Y/2), linestyle=':', color='xkcd:reddish gray')

    # fo.ax.xaxis.set_major_locator(locator)
    # fo.ax.xaxis.set_major_formatter(formatter)
    fo.axRotateLabels()
    fo.ax.minorticks_on()
    fo.ax.grid(axis='both', which='both', linestyle=':', color='xkcd:light gray')
    fo.ax.grid(axis='y', which='minor', linestyle=(3, (1,6)), color='xkcd:light gray')
    fo.ax.legend(title='Countries')
    fo.ax.set_ylabel('cases · population${}^{-1}$ · 100000')

    fo.show('tl-cases-r.svg')

    fo = FigureObj()
    df.plot(ax=fo.ax, kind='line',
            logy=True,
            marker='|',
            title='Confirmed cases per 100.000 capita (log-y) ('+strDate+')',
            figsize=(13,8)
           )

    X = df.index
    Y = np.linspace(0, df.index.size-1, num=df.index.size)
    # c = df.loc[df.index.min()].max()
    c = df.loc[df.index.min()]['South Korea']

    fo.ax.plot(X, c * 2**(Y/10), linestyle=':', color='xkcd:sky blue')
    fo.ax.plot(X, c * 2**(Y/4), linestyle=':', color='xkcd:light red')
    fo.ax.plot(X, c * 2**(Y/2), linestyle=':', color='xkcd:reddish gray')

    # fo.ax.xaxis.set_major_locator(locator)
    # fo.ax.xaxis.set_major_formatter(formatter)
    fo.axRotateLabels()
    fo.ax.minorticks_on()
    fo.ax.set_ylim(ymin=1e-3, ymax=1e3)
    fo.ax.grid(axis='x', which='both', linestyle=':', color='xkcd:light gray')
    fo.ax.grid(axis='y', which='major', linestyle=':', color='xkcd:light gray')
    fo.ax.legend(title='Countries')
    fo.ax.set_ylabel('cases · population${}^{-1}$ · 100000')

    # %%
    fo.show('tl-cases-rl.svg')



# ############################################################################

if fTasks['gr_cases']:
    dftlCases = dfLoadCasesTLCovAPIv1()
    strDateFirst = dftlCases.iloc[:,0].name
    strDateLast = dftlCases.iloc[:,-1].name
    countriesPreselect = ['Germany','Belgium','Netherlands','Switzerland','France','Italy','Spain','Sweden','United Kingdom','United States','Japan','South Korea','China']


    dftlCases = provideTLPerCountry(dftlCases, countriesPreselect)

    #plt.subplots(6, 1)
    countries = ('Germany','Belgium','Netherlands','Switzerland','Italy','Spain','Sweden','United Kingdom','United States','Japan','South Korea','China')

    for country in countries:
        dfCountry = pd.DataFrame(dftlCases.loc[:,country])

        for d in (2, 4, 7, 14):
          dfCountry = dfCountry.join(
                    dftlCases.loc[:,country].rename("{:d} days".format(d)) \
                    .rolling(window=d+1, center=False) \
                    #.apply(lambda v: (v[d]/v[0])**(1./d), raw=True)
                    .apply(lambda v: ((v[d]/v[0])**(1./d)-1)*100, raw=True) # percent
                )

        fo = FigureObj()
        dfCountry.iloc[:,1:].plot(ax=fo.ax, kind='line',
                    logy=False,
                    marker='o',
                    title='Confirmed cases, daily growth rate in {:s} ({:s}..{:s})'.format(country, strDateFirst, strDateLast),
                    #title='Confirmed cases, growth rate in '+country+' ('+strDateFirst+'..'+strDateLast+')',
                    figsize=(13,8)
                )
        fo.ax.set_ylim(ymin=0, ymax=60)
        fo.ax.minorticks_on()
        fo.axRotateLabels()
        fo.ax.grid(axis='both', which='both', linestyle=':', color='xkcd:light gray')
        fo.ax.set_ylabel('(backw avg) growth in percent per day')
        fo.ax.legend(title='Avg over $n$ days')

        fo.show('tl-rates-confirmed-{:s}.svg'.format(country))

    # ##

    for country in countries:
        dfCountry = pd.DataFrame(dftlCases.loc[:,country])

        d = 4
        dfCountry = dfCountry.join(
                      dftlCases.loc[:,country].rename("{:d} days".format(d)) \
                      .rolling(window=d+1, center=False) \
                      .apply(lambda v: np.log(2)/np.log((v[d]/v[0])**(1./d)), raw=True)
                      #.apply(lambda v: np.log(2)/np.log((v[d]/v[0])**(1./d)) if v[0] != 0 else np.inf, raw=True)
                    )

        fo = FigureObj()
        dfCountry.iloc[:,1:].plot(ax=fo.ax, kind='line',
                    logy=False,
                    marker='o',
                    title='Confirmed cases in {:s} double every $n$ days ({:s}..{:s})'.format(country, strDateFirst, strDateLast),
                    figsize=(13,8)
                )
        fo.ax.set_ylim(ymin=0, ymax=25)
        fo.ax.minorticks_on()
        fo.axRotateLabels()
        fo.ax.grid(axis='both', which='both', linestyle=':', color='xkcd:light gray')
        fo.ax.set_ylabel('cases double every $n$ days (backw avg over {:n} days)'.format(d))
        #fo.ax.legend(title='Avg over $n$ days')

        fo.show('tl-doubles-confirmed-{:s}.svg'.format(country))

    # ## ## ## ## ## ##

    dftlCases = dfLoadCasesTLCovAPIv1(rcConfig.pDataCovidDataBase+'docs/v1/countries/deaths.csv')
    strDateFirst = dftlCases.iloc[:,0].name
    strDateLast = dftlCases.iloc[:,-1].name
    dftlCases = provideTLPerCountry(dftlCases, countriesPreselect)

    #plt.subplots(6, 1)
    countries = ('Germany','Belgium','Netherlands','Switzerland','Italy','Spain','Sweden','United Kingdom','United States','Japan','South Korea','China')

    for country in countries:
        dfCountry = pd.DataFrame(dftlCases.loc[:,country])

        for d in (2, 4, 7, 14):
          dfCountry = dfCountry.join(
                    dftlCases.loc[:,country].rename("{:d} days".format(d)) \
                    .rolling(window=d+1, center=False) \
                    #.apply(lambda v: (v[d]/v[0])**(1./d), raw=True)
                    .apply(lambda v: ((v[d]/v[0])**(1./d)-1)*100, raw=True) # percent
                )

        fo = FigureObj()
        dfCountry.iloc[:,1:].plot(ax=fo.ax, kind='line',
                    logy=False,
                    marker='+',
                    title='Fatalities, daily growth rate in {:s} ({:s}..{:s})'.format(country, strDateFirst, strDateLast),
                    #title='Confirmed cases, growth rate in '+country+' ('+strDateFirst+'..'+strDateLast+')',
                    figsize=(13,8)
                )
        fo.ax.set_ylim(ymin=0, ymax=60)
        fo.ax.minorticks_on()
        fo.axRotateLabels()
        fo.ax.grid(axis='both', which='both', linestyle=':', color='xkcd:light gray')
        fo.ax.set_ylabel('(backw avg) growth in percent per day')
        fo.ax.legend(title='Avg over $n$ days')

        fo.show('tl-rates-deaths-{:s}.svg'.format(country))



# ############################################################################

if fTasks['gr_zeroday_cases']:
    dftlCases = dfLoadCasesTLCovAPIv1()
    countriesPreselect = ['Germany','Belgium','Netherlands','Switzerland','Italy','Spain','Sweden','United Kingdom','United States','Japan','South Korea','China']
    dftlCases = provideTLPerCountry(dftlCases, countriesPreselect)

    countries = ['Germany','Belgium','Netherlands','Switzerland','Italy','Spain','Sweden','United Kingdom','United States','Japan','South Korea','China']
    nBase = 100

    nRowsMax = dftlCases.shape[0]
    dfD = pd.DataFrame(index=range(0, nRowsMax))
    for c in countries:
        dstl = dftlCases[c]
        for i in range(0, dstl.size):
            if dstl.iloc[i] >= nBase:
                break
        dstl = dstl.shift(-i)
        dfD = dfD.merge(pd.Series(data=dstl.values, index=range(0, nRowsMax), name=c), how='left', left_index=True, right_index=True)

    fo = FigureObj()
    dfD.plot(ax=fo.ax, kind='line',
                logy=True,
                marker='|',
                title='Confirmed cases relative to the day at least {:n} cases were on the record'.format(nBase),
                figsize=(13,8)
            )
    fo.ax.minorticks_on()
    fo.ax.grid(axis='both', which='both', linestyle=':', color='xkcd:light gray')
    fo.ax.set_xlim(xmin=0)
    fo.ax.set_ylim(ymin=nBase)
    fo.ax.set_xlabel('days since the day when ${{}}>{:n}$ cases where on the record'.format(nBase))
    fo.ax.set_ylabel('confirmed cases')
    fo.ax.legend(title='Country')

    fo.show('tl-rates-0d-confirmed.svg')

    # ## ## ## ## ## ##

    dftlCases = dfLoadCasesTLCovAPIv1(rcConfig.pDataCovidDataBase+'docs/v1/countries/deaths.csv')
    dftlCases = provideTLPerCountry(dftlCases, countriesPreselect)

    countries = ['Germany','Belgium','Netherlands','Switzerland','Italy','Spain','Sweden','United Kingdom','United States','Japan','South Korea','China']
    nBase = 10

    nRowsMax = dftlCases.shape[0]
    dfD = pd.DataFrame(index=range(0, nRowsMax))
    for c in countries:
        dstl = dftlCases[c]
        for i in range(0, dstl.size):
            if dstl.iloc[i] >= nBase:
                break
        dstl = dstl.shift(-i)
        dfD = dfD.merge(pd.Series(data=dstl.values, index=range(0, nRowsMax), name=c), how='left', left_index=True, right_index=True)

    fo = FigureObj()
    dfD.plot(ax=fo.ax, kind='line',
                logy=True,
                marker='+',
                title='Fatalities relative to the day at least {:n} fatalities were on the record'.format(nBase),
                figsize=(13,8)
            )
    fo.ax.minorticks_on()
    fo.ax.grid(axis='both', which='both', linestyle=':', color='xkcd:light gray')
    fo.ax.set_xlim(xmin=0)
    fo.ax.set_ylim(ymin=nBase)
    fo.ax.set_xlabel('days since the day when ${{}}>{:n}$ fatalities where on the record'.format(nBase))
    fo.ax.set_ylabel('fatalities')
    fo.ax.legend(title='Country')

    fo.show('tl-rates-0d-deaths.svg')

#plt.subplots()

if not fOptions['noshow']: plt.show()
