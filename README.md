# msds-scraper
Python + Selenium for scraping material saftey datasheets from fishersci.com

## Install
Make and add to an anaconda environment: 
```
conda create --name msds_scraper python
conda activate msds_scraper

$CONDA_PREFIX/bin/pip install git+https://github.com/UnnaturalProducts/msds-scraper.git
```

Or make your own lil virtual env and carry forward from there:
```
git clone https://github.com/UnnaturalProducts/msds-scraper.git
cd msds-scraper
virtualenv -p python env
source env/bin/activate
pip install .
```

## CLI

Once you've followed the installation instructions the cli will be available in the environment.

Check out the documentation with
```
msds_scraper --help
```
Or use this template
```
msds_scraper /path/to/your/UNP_Inventory.xlsx /path/to/your/dirctory/with/msds.pdfs
```

There are example files in the `./msds_scraper/tests/data` directory.