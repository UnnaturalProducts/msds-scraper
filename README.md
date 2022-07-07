# msds-scraper

Tool for scraping material saftey datasheets (currently only from fishersci.com)

This repository contains a script that inputs a .xlsx file which at a minimum has a named 'Substance CAS'. 
The script also takes the a path to a directory of already obtained material datasheets, `msds_directory`. 
For each substance CAS it checks for an already exisiting material datasheets in the msds directory. 
If it doesn't find an existing material datasheet it checks the fishsci website and attempts
to download the .pdf to the given directory.

It also creates a log file `./bad-cas.csv` which warns about any CAS number where it couldn't find a file in the same directory the 
script is executed, or you can specify a path and filename for the log file.

Example:

```bash
msds-scraper /path/to/UNP_Inventory.xlsx /path/to/msds_directory/msds.pdfs
```

### Install (developers):

We no longer have "user" instructions as this tool has been redesigned to fit into an automated task on AWS.

Using Python Poetry:

```bash
git clone https://github.com/UnnaturalProducts/msds-scraper.git
cd msds-scraper
poetry install
poetry shell
```

### CLI

Check out the complete documentation with

```bash
msds-scraper --help
```

Or use this template

```bash
msds-scraper /path/to/your/UNP_Inventory.xlsx /path/to/your/dirctory/with/msds.pdfs
```

There are example files in the `./tests/data` directory.
