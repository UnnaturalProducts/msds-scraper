import requests

from msds_scraper import utils


def test_is_pdf_content():
    r = requests.Response()
    r.headers["content-type"] = "application/pdf"
    assert utils.is_pdf_content(r)


def test_not_is_pdf_content():
    r = requests.Response()
    r.headers["content-type"] = "text/html"
    assert not utils.is_pdf_content(r)
