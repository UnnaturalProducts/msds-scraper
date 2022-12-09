from os import PathLike
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd


def remove_old_msds(old_cas: List[str], output_path: Path):
    for cas in old_cas:
        fpath = output_path / f"{cas}.pdf"
        if fpath.exists():
            fpath.unlink()
        else:
            print(f"Error: {fpath} does not exist")


def get_current_msds_casnos(path: PathLike) -> List[str]:
    path = Path(path)
    return [sd.stem for sd in path.glob("*.pdf")]


def read_xlsx_sheet(
    path, *, lower_cols: bool = True, sheet_name="Sheet1"
) -> pd.DataFrame:
    return next(
        df for sn, df in read_xlsx(path, lower_cols=lower_cols) if sn == sheet_name
    )


def write_bad_cas(bad_cas_list: List[str], output_path: Path):
    with output_path.open("w") as f:
        for bad_cas in bad_cas_list:
            print(bad_cas, file=f)


# Taken from unpdash-django
def read_xlsx(path, header=0, lower_cols=True) -> List[Tuple[str, pd.DataFrame]]:
    """Read in xlsx and return list of tuple with all sheets -> dataframe"""
    sp = pd.read_excel(path, sheet_name=None, header=header)
    df_tuples = [(sheet_name, df) for sheet_name, df in sp.items()]
    df_tuples = [
        (sheet_name, sanitize_df(df, lower_cols)) for sheet_name, df in df_tuples
    ]
    df_tuples = [
        (sheet_name, df.apply(strip_df_strings)) for sheet_name, df in df_tuples
    ]
    return df_tuples


def strip_df_strings(contents):
    """Strip whitespace if item in content is a str"""
    for index, item in contents.items():
        if isinstance(item, str):
            contents[index] = item.strip()
    return contents


def sanitize_df(df: pd.DataFrame, lower_cols=True) -> pd.DataFrame:
    df.dropna(how="all", axis="index", inplace=True)
    df.replace({np.nan: None}, inplace=True)

    ghost_columns = [
        col_name
        for col_name in df.columns
        if isinstance(col_name, str) and "Unnamed:" in col_name
    ]

    df.drop(ghost_columns, axis=1, inplace=True)
    if lower_cols:
        df.columns = [col.lower() for col in df.columns]

    return df
