import requests


def is_pdf_content(r: requests.Response) -> bool:
    return r.headers["content-type"] == "application/pdf"
