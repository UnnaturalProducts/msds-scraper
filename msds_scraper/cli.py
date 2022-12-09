from pathlib import Path
from typing import Callable, Optional

import typer
from joblib import Parallel, delayed
from rich.progress import track

from msds_scraper import combiblocks, fischer, io

app = typer.Typer()


def _try_get_cas(method: Callable, cas: str, output_dir: Path) -> bool:
    try:
        method(cas, output_dir)
        return True
    except AssertionError:
        return False


def get_cas(cas: str, ouput_dir: Path) -> Optional[str]:
    """Abstraction around get_cas from service.
    Extend here if we want to add extra queries.

    Returns CAS is retrieval failed
    """
    result = False
    # if result is True, retrieval succeeded
    methods = (fischer.get_cas_pdf, combiblocks.get_cas_pdf)
    for get_method in methods:
        result = _try_get_cas(get_method, cas, ouput_dir)
        if result is True:
            return
    # return cas if none of the above succeeded
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
        Path("./bad-cas.csv"),
        resolve_path=True,
        help="File path output of text file containing cas numbers which failed to return a msds.",
    ),
    workers: int = typer.Option(
        1,
        "--workers",
        "-w",
        help="Number of worker for multi-threading (Not supported on Windows)",
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
    old_casnos = [cas for cas in (known_casnos - casnos) if cas is not None]

    typer.echo(
        f"Found {len(old_casnos)} old CAS to query - removing files from {msds_directory}"
    )
    io.remove_old_msds(old_casnos, msds_directory)

    typer.echo(
        f"Found {len(new_casnos)} new CAS to query - writing files to {msds_directory}"
    )
    cas_iter = new_casnos
    if verbose:
        cas_iter = track(new_casnos, description="Getting MSDS for CAS...")
    if workers == 1:
        results = [get_cas(cas, msds_directory) for cas in cas_iter]
    else:
        results = Parallel(n_jobs=workers, verbose=0)(
            delayed(get_cas)(cas, msds_directory) for cas in cas_iter
        )
    bad_casnos = list(filter(lambda x: x is not None, results))

    typer.echo(f"Found {len(bad_casnos)} bad CAS - writing to {bad_cas_output}")
    io.write_bad_cas(bad_casnos, bad_cas_output)


if __name__ == "__main__":
    app()
