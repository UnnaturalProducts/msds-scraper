from pathlib import Path

import requests


def is_pdf_content(r: requests.Response) -> bool:
    return r.headers["content-type"] == "application/pdf"


def is_pdf_file(path: Path) -> bool:
    """True if path is a non-empty file beginning with the %PDF magic bytes.

    Used for locally generated PDFs (e.g. the PubChem LCSS print), where there
    is no HTTP content-type header to check.
    """
    if not path.is_file() or path.stat().st_size == 0:
        return False
    with path.open("rb") as f:
        return f.read(5) == b"%PDF-"
