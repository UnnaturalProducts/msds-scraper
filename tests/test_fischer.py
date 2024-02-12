from http import HTTPStatus
from pathlib import Path

import magic
import pytest

from msds_scraper import fischer

GOOD_CAS = "50-00-0"
BAD_CAS = "OBVIOISLY-FAKE-CAS"


@pytest.mark.vcr
def test__get_fischer():
    home = "us/en/home.html"
    r = fischer._get_fischer(home)
    assert r.status_code == HTTPStatus.OK
    assert r.headers["content-type"] == "text/html; charset=UTF-8"


@pytest.mark.vcr
def test__get_fischer_strips():
    home = "/us/en/home.html"
    r = fischer._get_fischer(home)
    assert r.status_code == HTTPStatus.OK
    assert r.headers["content-type"] == "text/html; charset=UTF-8"


@pytest.mark.vcr
def test__get_fischer_strips_no_headers():
    home = "/us/en/home.html"
    r = fischer._get_fischer(home, headers={})
    assert r.status_code == HTTPStatus.OK
    assert r.headers["content-type"] == "text/html; charset=UTF-8"


@pytest.mark.vcr
def test_get_fischer_msds_link_good_cas():
    path = fischer.get_fischer_msds_link(GOOD_CAS)
    assert path is not None
    # This changes all the time
    assert isinstance(path, str)
    assert path.startswith("/store/msds?")


@pytest.mark.vcr
def test_get_fischer_msds_link_bad_cas():
    path = fischer.get_fischer_msds_link(BAD_CAS)
    assert path is None


@pytest.mark.vcr
def test_get_cas_pdf_good_cas(tmp_path: Path):
    output_path = fischer.get_cas_pdf(GOOD_CAS, tmp_path)
    assert output_path.exists()
    # check it's actually a pdf
    f = magic.from_file(output_path)
    assert "PDF document" in f


@pytest.mark.vcr
def test_get_cas_pdf_bad_cas(tmp_path: Path):
    with pytest.raises(AssertionError) as e:
        fischer.get_cas_pdf(BAD_CAS, tmp_path)
        assert str(e) == f"CAS = {BAD_CAS} not found on Fischer"
