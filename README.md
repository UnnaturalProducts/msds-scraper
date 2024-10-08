# msds-scraper

Tool for scraping material saftey datasheets from fishersci and combiblocks.

This repository contains a script that inputs a .xlsx file which at a minimum has a named 'Substance CAS'.
The script also takes the a path to a directory of already obtained material datasheets, `msds_directory`.
For each substance CAS it checks for an already exisiting material datasheets in the msds directory.
If it doesn't find an existing material datasheet it checks the fishsci website and attempts
to download the .pdf to the given directory.

It also creates a log file `./bad-cas.csv` which warns about any CAS number where it couldn't find a file in the same directory the
script is executed, or you can specify a path and filename for the log file.

## Usage

This tool works cross platform. Running the CLI has the advantage of using the Google Drive client to sync.
On macOS this is simplified by the fact that the Google Drive client is available and you can do the same
steps but skip all the rclone details. On Linux a couple extra steps can be taken to make usage easier (See Rclone section below).

The typical workflow currently is as follows:

```bash
poetry shell
cd PATH TO GOOGLE DRIVE/2023_Inventory/March_2023_Inventory
msds-scraper --verbose --worker  ./ChemInventoryMarch23.xlsx ./March_2023_MSDS
```

Check out the complete documentation with

```bash
msds-scraper --help
```

Once finished, monthly MSDS should also be copied to the `All_MSDS` folder. This is can be done using `rsync`. Ex.

```bash
# switch to data root
cd ..\..
# a specific month
rsync -avz --progress --ignore-existing ./2023_Inventory/March_2023_Inventory/March_2023_MSDS/*.pdf ./All_MSDS/
# all months
rsync -avz --progress --ignore-existing ./2024_Inventory/2024_*_Inventory/*_MSDS/*.pdf ./All_MSDS/
```

### Rclone

First, use rclone to mount the Google Drive. You will need to configure the clone following instruction [here](https://rclone.org/drive/). This requires read+write for the UNP Core Shared Drive. Client name is `gdrive` and the mount point is `data` here.

```bash
rclone -v --vfs-cache-mode writes mount "gdrive:Operations/Laboratory Operations/Inventory MSDS" "data"
```

Check and see if you are infact mounted in a second terminal

```bash
ls data/2023_Inventory
```

If there is no output, check to make sure that your root_folder_id matches UNP Core's root folder id. You can find it
in the url of the root folder: `0ALC9N0phLt1LUk9PVA`.

Then set this in your rclone config file by adding the line `root_folder_id = 0ALC9N0phLt1LUk9PVA`

Try again.

Once connected you can run the CLI as normal in a second terminal (as described above).

Wait for the rclone sync to finish and then you can cancel the rclone mount (`ctrl+c`).

## Installation

A windows executable of the `msds-scraper.exe` is available for distribution and does not require the
creation or activation of a virtual environment. Put this executable somewhere you remember because
you'll need the full path to run the program.

This does require you have [Python 3.8](https://www.python.org/downloads/)
installed on your machine and on your system Path. (_IMPORTANT_: Select the __Select the 'add to path' option.__ during installation).
_Note: initial testing suggests that a Python installation may not be needed._

After this, simply download the latest release executable for the [GitHub releases](https://github.com/UnnaturalProducts/msds-scraper/releases) 
and you should be good to go.

To run the program, open up a cmd or powershell window on your machine and run the following:

```cmd
.\path\to\msds-scraper.exe .\path\to\Inventory.xslx .\path\to\pdf\output\directory\
```

## Development

Using Python Poetry:

```bash
git clone git@github.com:UnnaturalProducts/msds-scraper.git
cd msds-scraper
poetry install
poetry shell
```

To run the tests ([see here for VCR options](https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes)):

You may need to install `libmagic` for the `python-magic` package to work. On Ubuntu this can be done with `sudo apt-get install libmagic1`.
On macOS this can be done with `brew install libmagic`.

__NOTE__ tests are currently failing if you use VCR for some reason? This is a known issue and will be fixed later. For
now just run the tests without VCR by including `--vcr-record=all` in the command to fetch new data.

```bash
pytest

# If you added new tests or changed a test which interacts with VCR add the `--record-mode` flag: eg.
pytest --record-mode=once
```

## Production Build

To build a windows executable for distribution you will also need a Windows machine with python3.8 installed.

Then in your dev environment setup with poetry:

```cmd
pyinstaller .\msds_scraper\cli.py -F -n msds-scraper
```

This will create the file `.\dist\msds-scraper.exe` which should be upload to the latest stable GitHub Release.
