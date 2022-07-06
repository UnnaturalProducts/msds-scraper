from pathlib import Path
from typing import Optional

import typer
from joblib import Parallel, delayed

from msds_scraper import fischer, io

app = typer.Typer()


def get_cas(cas: str, ouput_dir: Path) -> Optional[str]:
    """Abstraction around get_cas from service.
    Extend here if we want to add extra queries.

    Returns CAS is retrieval failed
    """
    try:
        fischer.get_cas_pdf(cas, ouput_dir)
    except AssertionError:
        return cas


@app.command()
def main(
    input: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        resolve_path=True,
    ),
    msds_directory: Path = typer.Argument(
        ...,
        resolve_path=True,
    ),
    bad_cas_output: Path = typer.Option(
        Path("./bas-cas.csv"),
        resolve_path=True,
        help="File path output of text file containing cas numbers which failed to return a msds.",
    ),
    workers: int = typer.Option(
        -1, "--workers", "-w", help="Number of worker for multi-threading"
    ),
    verbose: bool = typer.Option(True, help="Toggle progress output"),
):
    """
    Tool for scraping material saftey datasheets (currently only from fishersci.com)

    This repository contains a script that inputs a .xlsx file which at a minimum has a named 'Substance CAS'.
    The script also takes the a path to a directory of already obtained material datasheets, `msds_directory`.
    For each substance CAS it checks for an already exisiting material datasheets in the msds directory.
    If it doesn't find an existing material datasheet it checks the fishsci website and attempts
    to download the .pdf to the given directory.

    Example:

    msds-scraper /path/to/your/UNP_Inventory.xlsx /path/to/your/MSDS_DIRCTORY
    """
    df = io.read_xlsx_sheet(input)
    assert (
        "substance cas" in df.columns
    ), "Input Excel file missing `Substance CAS` column"
    if not msds_directory.is_dir():
        typer.echo(f"Creating output directory - {msds_directory}")
        msds_directory.mkdir()

    casnos = set(df["substance cas"].values)
    known_casnos = set(io.get_current_msds_casnos(msds_directory))
    new_casnos = [cas for cas in (casnos - known_casnos) if cas is not None]  # set math
    typer.echo(
        f"Found {len(new_casnos)} new CAS to query - writing files to {msds_directory}"
    )

    results = Parallel(n_jobs=workers, verbose=10 if verbose else 0)(
        delayed(get_cas)(cas, msds_directory) for cas in new_casnos
    )
    bad_casnos = list(filter(lambda x: x is not None, results))

    typer.echo(f"Found {len(bad_casnos)} bad CAS - writing to {bad_cas_output}")
    io.write_bad_cas(bad_casnos, bad_cas_output)


if __name__ == "__main__":
    app()
