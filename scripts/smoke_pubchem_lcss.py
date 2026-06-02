"""Manual smoke test for the PubChem LCSS -> PDF render.

Playwright browser traffic is not VCR-able, so the LCSS render is not unit
tested. Run this against a real CAS (or CID) to eyeball the generated PDF.

Usage:
    poetry run python scripts/smoke_pubchem_lcss.py 50-00-0
    poetry run python scripts/smoke_pubchem_lcss.py --cid 712 --out ./run
"""

import argparse
from pathlib import Path

from msds_scraper import pubchem
from msds_scraper.utils import is_pdf_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cas", nargs="?", help="CAS number to resolve and render")
    parser.add_argument(
        "--cid", type=int, help="Render this PubChem CID directly (skips CAS lookup)"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("./run"),
        help="Output directory for the rendered PDF (default: ./run)",
    )
    args = parser.parse_args()

    if not args.cas and args.cid is None:
        parser.error("provide a CAS argument or --cid")

    args.out.mkdir(parents=True, exist_ok=True)

    if args.cid is not None:
        cid = args.cid
        stem = args.cas or str(cid)
    else:
        print(f"Resolving CAS {args.cas} -> CID ...")
        cid = pubchem.get_cid_from_cas(args.cas)
        stem = args.cas
        print(f"  CID = {cid}")

    output_path = args.out / f"{stem}.pdf"
    print(f"Rendering LCSS for CID {cid} -> {output_path} ...")
    pubchem.render_lcss_pdf(cid, output_path)

    ok = is_pdf_file(output_path)
    size = output_path.stat().st_size if output_path.exists() else 0
    print(f"Done: {output_path} ({size} bytes), valid PDF: {ok}")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
