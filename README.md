# msds-scraper
Python + Selenium for scraping material saftey datasheets from fishersci.com

### Install on windows:

Open up the command prompt and check to see if you have python installed:

```
py --version
```
If you don't have python installed, install python 3.8.0 onto your machine. Select the 

Next, check to see if you've got pip installed
```
py -m ensurepip --default-pip
```
If the above doesn't work [download this.](https://bootstrap.pypa.io/get-pip.py) And run that file
with 
```
py ./get-pip.py
```
Once you've got pip make sure things are up to date with
```
py -m pip install --upgrade pip setuptools wheel
```
Now you're ready to install the msds scraper on your machine.
```
py -m pip install msds_scraper@git+https://github.com/UnnaturalProducts/msds-scraper.git
```

### Install on Ubuntu or mac:  
You'l need git and optoinally virtualenv or the like.
make your own lil virtual env and carry forward from there:

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
