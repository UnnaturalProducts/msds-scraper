from http import HTTPStatus
from pathlib import Path
from typing import Dict, Optional
import bs4
import requests

FISCHER_BASE = "https://www.fishersci.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
DEFAULT_HEADERS = {"User-Agent": USER_AGENT}


def is_pdf_content(r: requests.Response) -> bool:
    return r.headers["content-type"] == "application/pdf"


def _get_fischer(path: str, headers: Dict = DEFAULT_HEADERS) -> requests.Response:
    if path.startswith("/"):
        path = path.lstrip("/")
    return requests.get(f"{FISCHER_BASE}/{path}", headers=headers)


def get_fischer_msds_link(cas: str) -> Optional[str]:
    r = _get_fischer(f"/us/en/catalog/search/sds?selectLang=EN&msdsKeyword={cas}")
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    # get first catalog link - this appears to be unique to the msds results
    anchor = soup.find("a", {"class": "catalog_num_link"})
    if anchor is None:
        return None
    return anchor.attrs.get("href")


def get_cas_pdf(cas: str, output_dir: Path) -> Path:
    pdf_path = get_fischer_msds_link(cas)
    assert pdf_path is not None, f"CAS = {cas} not found on Fischer"
    r = _get_fischer(pdf_path)
    assert (
        r.status_code == HTTPStatus.OK
    ), f"Could not get PDF for CAS = {cas} from Fischer\nResponse:\t{r.content.decode()}"
    assert is_pdf_content(r), "Response from Fischer is not PDF content"
    output_path = output_dir.joinpath(f"{cas}.pdf")
    with output_path.open("wb") as f:
        f.write(r.content)
    return output_path
