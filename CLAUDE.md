# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
poetry install                                   # set up dev environment
make test                                        # run the suite in parallel (pytest -n auto)
make format                                      # ruff import-sort + ruff format
make lint                                         # ruff check + ruff format --check
poetry run pytest tests/test_cli.py::test_cli    # run a single test
poetry run msds-scraper --help                   # CLI usage
```

Success criterion: `make test` exits 0. There is no typecheck step; ruff (`make lint` / `make format`) is the only style gate.

## What this is

A small Typer CLI (`msds-scraper`) that reconciles an inventory `.xlsx` against a directory of downloaded MSDS PDFs, then scrapes vendor sites (Fischer, then Combi-Blocks) to fetch any missing ones. Saves each as `{cas}.pdf`; writes un-findable CAS numbers to a bad-CAS CSV (default `./bad-cas.csv`).

## Key concepts

- **Adding a vendor** = new module exposing `get_cas_pdf(cas, output_dir) -> Path`, then add it to the `methods` tuple in `cli.get_cas`. Vendors are tried in tuple order until one succeeds.
- **Existing-PDF detection keys purely off the filename stem** (`{cas}.pdf`) in the MSDS directory — there is no metadata or index.
- `io.read_xlsx` / `sanitize_df` are copied verbatim from `unpdash-django`; they lowercase column names (so the required column is matched as `substance cas`), strip strings, and drop `Unnamed:`/all-NaN rows.

## Things that will bite you

- **Scraper failure is signalled by `AssertionError`, not a return value or custom exception.** `cli._try_get_cas` catches `AssertionError` to mean "this vendor didn't have it." A scraper that raises anything else will crash the run.
- **`cli.get_cas` has inverted return semantics**: returns `None` on success, returns the CAS string on total failure. The CLI collects the non-`None` results as the bad-CAS list.
- **`--workers` > 1 is not supported on Windows** (joblib). The shipped `.exe` must run single-threaded.
- **VCR replay is currently flaky** (known issue): if a network test fails on replay, re-run with `--vcr-record=all` to hit live sites, or `--record-mode=once` to record only missing cassettes. Cassettes live in `tests/cassettes/<test_module>/`, fixtures in `tests/data/`.
- **`python-magic` (dev dep) needs system `libmagic`**: `brew install libmagic` (macOS) / `sudo apt-get install libmagic1` (Ubuntu).
