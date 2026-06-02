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


def test_is_pdf_file_true(tmp_path):
    p = tmp_path / "doc.pdf"
    p.write_bytes(b"%PDF-1.7\n...content...")
    assert utils.is_pdf_file(p)


def test_is_pdf_file_not_pdf(tmp_path):
    p = tmp_path / "doc.pdf"
    p.write_bytes(b"<html></html>")
    assert not utils.is_pdf_file(p)


def test_is_pdf_file_empty(tmp_path):
    p = tmp_path / "empty.pdf"
    p.write_bytes(b"")
    assert not utils.is_pdf_file(p)


def test_is_pdf_file_missing(tmp_path):
    assert not utils.is_pdf_file(tmp_path / "nope.pdf")
