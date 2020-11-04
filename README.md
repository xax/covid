# covid

**→ Have a look at the compiled visuals [here](https://xax.github.io/covid/).**


# Data visualization


## Preparations and Dependencies

To run the visualization script you need *Python* (as of versions *3.6+*), of course, and probably want to prepare the environment as follows:

0. create virtual environment (*optional*)

    `$ python -m venv ./.venv`

    `$ source ./.venv/bin/activate`

1. install dependencies

    `$ pip install numpy matplotlib pandas`

    `$ sudo apt-get install python3-tk`  *#* (*perhaps; Debian'ish case*)

    `$ pip install Tkinter`  *#* (*possibly*)

    `$ pip install adjustText`  *#* (*optional*)


## Setup of data sources

1. clone [JHUCSSE] repository

    `$ git clone --depth=1 -b web-data https://github.com/CSSEGISandData/COVID-19.git`

2. clone [CovidData] repository

    `$ git clone --depth=1https://github.com/coviddata/coviddata.git`

3. retrieve GeoNames [CountryDataGN] database

    `$ wget https://download.geonames.org/export/dump/countryInfo.txt`

9. show command line options help

    `$ python3 ./covid2xa.py -h`


## Run the visualization script `covid2xa.py`

- show all plots and create SVG files

    `$ python ./covid2xa.py -a`

- create all plots as SVG files only

    `$ python ./covid2xa.py -aX`


[JHUCSSE]: https://github.com/CSSEGISandData/COVID-19 "2019 Novel Coronavirus COVID-19 (2019-nCoV) Data Repository by Johns Hopkins CSSE"
[CovidData]: https://github.com/coviddata/coviddata "CovidData, preprocessed JHU CSSE and New York Times data"
[NYTData]: https://github.com/nytimes/covid-19-data "New York Times Covid-19 US states data"

[GeoNames]: http://www.geonames.org/ "GeoNames"
[CountryDataGN]: https://download.geonames.org/export/dump/countryInfo.txt "GeoNames country data"

[CC-by-4.0]: https://creativecommons.org/licenses/by/4.0/ "Creative Commons Attribution 4.0 License"
[JHU-TOS]: https://github.com/CSSEGISandData/COVID-19/blob/master/README.md "Terms of use"
[NYT-TOS]: https://github.com/nytimes/covid-19-data#license-and-attribution "License and Attribution"
