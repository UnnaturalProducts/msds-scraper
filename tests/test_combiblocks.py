from http import HTTPStatus
from pathlib import Path
import bs4
import magic

import pytest
from msds_scraper import combiblocks

GOOD_CAS = "1758-46-9"
BAD_CAS = "0000X-00-00"


@pytest.mark.vcr
def test_combiblocks_search():
    soup = combiblocks.combiblocks_search("")
    assert isinstance(soup, bs4.BeautifulSoup)


@pytest.mark.vcr
def test_combiblocks_search_good_cas():
    soup = combiblocks.combiblocks_search(GOOD_CAS)
    assert isinstance(soup, bs4.BeautifulSoup)


@pytest.mark.vcr
def test_get_catalog_num_good_cas():
    soup = combiblocks.combiblocks_search(GOOD_CAS)
    cat_id = combiblocks.get_catalog_number(soup)
    assert cat_id == "ST-6703"


@pytest.mark.vcr
def test_get_catalog_num_bad_cas():
    soup = combiblocks.combiblocks_search(BAD_CAS)
    cat_id = combiblocks.get_catalog_number(soup)
    assert cat_id is None


@pytest.mark.vcr
def test_get_cas_pdf_good_cas(tmp_path: Path):
    output_path = combiblocks.get_cas_pdf(GOOD_CAS, tmp_path)
    assert output_path.exists()
    # check it's actually a pdf
    f = magic.from_file(output_path)
    assert "PDF document" in f


@pytest.mark.vcr
def test_get_cas_pdf_bad_cas(tmp_path: Path):
    with pytest.raises(AssertionError) as e:
        combiblocks.get_cas_pdf(BAD_CAS, tmp_path)
        assert str(e) == f"CAS = {BAD_CAS} not found on Combi-Blocks"
