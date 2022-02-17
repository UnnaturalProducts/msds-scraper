"""
This script scrapes the fishersci website for material saftey datasheets (msds).

It inputs a .xlsx file with a 'Substance CAS' column and checks an already exisiting 
msds directory for missing material datasheets. If any missing msds's are found, it writes
the .pdfs to the specified msds directory.

It also creates a log file 'bad-cas.csv' in the same directory the script is executed, or you
can specify a path and filename for the log file.
"""
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import requests
import os
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import sys

def get_msds(cas, msds_directory):
        user_agent = {'User-agent': 'Mozilla/5.0'}
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_experimental_option("prefs", {
        #"download.default_directory": "/home/cpye/Desktop/msds/",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
        })
        browser = webdriver.Chrome(ChromeDriverManager(log_level=0).install(), options=options)
        browser.get(f"https://www.fishersci.com/us/en/catalog/search/sds?selectLang=EN&msdsKeyword={cas}")
        """
        # Old method uses UI to search, new method directly uses url to jump to the page.
        browser.get('https://www.fishersci.com/us/en/catalog/search/sdshome.html')
        sleep(0.5)
        search_form = browser.find_element_by_css_selector("#qa_msdsKeyword")
        sleep(0.5)
        search_form.send_keys(f"{cas}")
        sleep(0.5)
        search_button = browser.find_element_by_css_selector("#msdsSearch")
        search_button.submit()
        sleep(2.5)
        """
        try:
            selector = "#main > div.search_results.row > div > table > tbody > tr > td.catalog_data > div > div > div.catalog_num > div > div > div:nth-child(1) > a"
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            first_result = browser.find_element_by_css_selector(selector)
            url = first_result.get_attribute("href")
            r = requests.get(url, allow_redirects=True, headers=user_agent)
            pdf = r.content
            with open(os.path.join(msds_directory,f"{cas}.pdf"),'wb') as fout:
                fout.write(pdf)
        except:
            # raise
            return cas
        finally:
            browser.quit()


def get_current_msds_casnos(path):
    pdfs = [sd.name for sd in os.scandir(path) if sd.name.lower().endswith('.pdf')]
    casnos = [
        fn.split('.')[0].lstrip().rstrip() 
        for fn in pdfs
        ]
    return casnos


def parse_args(args):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("input", help="File path to Inventory excel file")
    parser.add_argument("msds_directory", help="File path to directory of stored material saftey data sheets 'cas#'.pdf")
    parser.add_argument("--bad_cas_output", default="./bad-cas.csv", help="File path output of text file containing cas numbers which failed to return a msds.")

    parser.add_argument("-m","--multi_thread",help='Multithread (may not work on windows)', action='store_true')
    return parser.parse_args(args)
    

def main(args=None):    
    
    args = parse_args(args)
    df = pd.read_excel(
        args.input
    )
    
    casnos = set(df['Substance CAS'].values)
    known_casnos = set(
        get_current_msds_casnos(args.msds_directory)
    )
    new_casnos = list((casnos-known_casnos)) #set math
    new_casnos = [cas for cas in new_casnos if pd.notna(cas)]
    bad_casses = []
    
    if not args.multi_thread:
        for cas in tqdm(new_casnos):
            cas = get_msds(cas, args.msds_directory)
            if cas is not None:
                bad_casses.append(cas)
                
    else:
        with ThreadPoolExecutor(max_workers=20) as ex:
            futs = {}
            for cas in new_casnos:
                fut = ex.submit(get_msds, cas, args.msds_directory)
                futs[fut] = cas

            pbar = tqdm(total=len(futs))
            for fut in as_completed(futs):
                cas = fut.result()
                if cas is not None:
                    bad_casses.append(cas)
                pbar.update()

    with open(args.bad_cas_output, "w") as bad_cas_out:
        for bad_cas in bad_casses:
            print(bad_cas, file=bad_cas_out)
        
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))