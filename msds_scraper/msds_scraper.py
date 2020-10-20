from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from time import sleep
from IPython import embed
import requests
import sys
import os

import pandas as pd

#BASEPATH = "/mnt/storage/InSync/TeamDrives/Team Drive/Operational/Lab Safety"
BASEPATH = "/Volumes/GoogleDrive/Shared drives/UNP Core/Operational/Lab Safety/"
BASEPATH = "./"

def get_msds(cas):
        user_agent = {'User-agent': 'Mozilla/5.0'}
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_experimental_option("prefs", {
        "download.default_directory": "/home/cpye/Desktop/msds/",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
        })
        browser = Chrome(options=options)

        browser.get('https://www.fishersci.com/us/en/catalog/search/sdshome.html')
        sleep(0.5)
        search_form = browser.find_element_by_css_selector("#qa_msdsKeyword")
        sleep(0.5)
        search_form.send_keys(f"{cas}")
        sleep(0.5)
        search_button = browser.find_element_by_css_selector("#msdsSearch")
        search_button.submit()
        sleep(2.5)
        try:
            selector = "#main > div.search_results.row > div > table > tbody > tr > td.catalog_data > div > div > div.catalog_num > div > div > div:nth-child(1) > a"
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            first_result = browser.find_element_by_css_selector(selector)
            url = first_result.get_attribute("href")
            r = requests.get(url,allow_redirects=True,headers=user_agent)
            pdf = r.content
            with open(os.path.join(BASEPATH,f"msds/{cas}.pdf"),'wb') as fout:
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

if __name__ == "__main__":
    from tqdm import tqdm
    from concurrent.futures import ThreadPoolExecutor,as_completed
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input",help="Inventory excel file")
    parser.add_argument("-s","--single_thread",help='single threaded mode (for debugging)',action='store_true')
    args = parser.parse_args()

    df = pd.read_excel(os.path.join(BASEPATH,args.input))
    
    casnos = set(df['Substance CAS'].values)
    known_casnos = set(get_current_msds_casnos(os.path.join(BASEPATH,"msds")))

    new_casnos = list((casnos-known_casnos)) #set math
    new_casnos = [cas for cas in new_casnos if pd.notna(cas)]
    with open("SCRAPE_ERRORS.txt",'w') as log:

        if args.single_thread:
            for cas in tqdm(new_casnos):
                res = get_msds(cas)
                if res is not None:
                    print(res,file=log)
                    tqdm.write(f"bad cas: {res}")
        else:
            with ThreadPoolExecutor(max_workers=20) as ex:
                futs = {}
                for cas in new_casnos:
                    fut = ex.submit(get_msds,cas)
                    futs[fut] = cas
                pbar = tqdm(total=len(futs))
                for fut in as_completed(futs):
                    res = fut.result()
                    if res is not None:
                        print(res,file=log)
                        pbar.write(f"bad cas: {res}")   
                    pbar.update()
        


