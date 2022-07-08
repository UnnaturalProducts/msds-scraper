from http import HTTPStatus
from pathlib import Path
from typing import Dict, Optional
import bs4
import requests

from .utils import is_pdf_content

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
DEFAULT_HEADERS = {"User-Agent": USER_AGENT}


def combiblocks_search(
    query: str, headers: Dict = DEFAULT_HEADERS
) -> bs4.BeautifulSoup:
    """
    Method to send query through combiblocks search form
    Returns Soup HTML for querying
    """
    r = requests.post(
        "https://www.combi-blocks.com/cgi-bin/find.cgi",
        headers=headers,
        data={"Input": query, "Page_Num": 1},
    )
    assert r.status_code == HTTPStatus.OK
    return bs4.BeautifulSoup(r.content, "html.parser")


def get_catalog_number(soup: bs4.BeautifulSoup) -> Optional[str]:
    inputs = soup.find_all("input")
    for i in inputs:
        if i.attrs.get("name") == "MY_CATA_NUM":
            return i.attrs.get("value")
    return None


def get_cas_pdf(cas: str, output_dir: Path) -> Path:
    soup = combiblocks_search(cas)
    cat_id = get_catalog_number(soup)
    assert cat_id is not None, f"Could not find CAS = {cas} from Combi-Blocks"
    pdf_path = f"https://www.combi-blocks.com/msds/{cat_id}.pdf"
    r = requests.get(pdf_path, headers=DEFAULT_HEADERS)
    assert (
        r.status_code == HTTPStatus.OK
    ), f"Could not get PDF for CAS = {cas} from Combi-Blocks\nResponse:\t{r.content.decode()}"
    assert is_pdf_content(r), "Response from Combi-Blocks is not PDF content"
    output_path = output_dir.joinpath(f"{cas}.pdf")
    with output_path.open("wb") as f:
        f.write(r.content)
    return output_path
