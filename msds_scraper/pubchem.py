from pathlib import Path

import pubchempy as pcp
import typer
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from .utils import is_pdf_file

LCSS_URL = "https://pubchem.ncbi.nlm.nih.gov/compound/{cid}#datasheet=lcss"


def get_cid_from_cas(cas: str) -> int:
    """Resolve a CAS number to a PubChem CID via PubChem's name lookup.

    Raises AssertionError (the source-failure signal used across this package)
    when PubChem has no compound for the CAS.
    """
    cids = pcp.get_cids(cas, "name")
    assert cids, f"CAS = {cas} not found on PubChem"
    if len(cids) > 1:
        typer.echo(f"Multiple CIDs for CAS = {cas}: {cids} - using first ({cids[0]})")
    return cids[0]


def render_lcss_pdf(cid: int, output_path: Path) -> None:
    """Render a PubChem LCSS datasheet to PDF via headless Chromium.

    The compound page is a JS single-page app whose sections lazy-load on
    scroll, so we navigate, wait for network idle, scroll to the bottom in
    steps to trigger all sections, then print to PDF (PubChem's own
    recommended print -> save-as-PDF flow).
    """
    url = LCSS_URL.format(cid=cid)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            # Scroll to the bottom in steps to trigger lazy-loaded sections.
            prev_height = -1
            for _ in range(30):
                height = page.evaluate("document.body.scrollHeight")
                if height == prev_height:
                    break
                prev_height = height
                page.mouse.wheel(0, height)
                page.wait_for_timeout(500)
            page.wait_for_load_state("networkidle")
            page.pdf(path=str(output_path), format="A4", print_background=True)
        finally:
            browser.close()


def get_cas_pdf(cas: str, output_dir: Path) -> Path:
    """LCSS backup source: resolve CAS -> CID, render the LCSS page to {cas}.pdf.

    Assertion-based failures match the existing source pattern (caught by
    cli._try_get_cas).
    """
    cid = get_cid_from_cas(cas)
    output_path = output_dir.joinpath(f"{cas}.pdf")
    # Convert Playwright failures (nav timeout, render error) into the
    # assertion-based source-failure signal so a single bad render falls
    # through cleanly instead of crashing the whole run.
    try:
        render_lcss_pdf(cid, output_path)
    except PlaywrightError as e:
        raise AssertionError(
            f"Could not render PubChem LCSS for CAS = {cas} (CID {cid}): {e}"
        ) from e
    assert is_pdf_file(output_path), (
        f"PubChem LCSS render for CAS = {cas} did not produce a valid PDF"
    )
    return output_path
