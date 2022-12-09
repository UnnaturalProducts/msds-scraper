from pathlib import Path

from msds_scraper import io

HERE = Path(__file__).parent


def mock_unlink(*args):
    return


def test_remove_old_msds(capsys, monkeypatch):
    monkeypatch.setattr(Path, "unlink", mock_unlink)
    output_dir = HERE / "data" / "msds_output"
    to_delete = ["109-99-9"]
    io.remove_old_msds(to_delete, output_dir)
    captured = capsys.readouterr()
    expected = "Removing /home/jvansan/projects/unp/msds-scraper/tests/data/msds_output/109-99-9.pdf"
    assert captured.out.strip() == expected


def test_remove_old_msds_missing_error(capsys, monkeypatch):
    monkeypatch.setattr(Path, "unlink", mock_unlink)
    output_dir = HERE / "data" / "msds_output"
    to_delete = ["109-99-X"]
    io.remove_old_msds(to_delete, output_dir)
    captured = capsys.readouterr()
    expected = "Error: /home/jvansan/projects/unp/msds-scraper/tests/data/msds_output/109-99-X.pdf does not exist"
    assert captured.out.strip() == expected


def test_get_current_msds_casnos():
    output_dir = HERE / "data" / "msds_output"
    expected = ["109-99-9", "88050-17-3"]
    assert io.get_current_msds_casnos(output_dir) == expected


def test_read_xlsx():
    input_path = HERE / "data" / "InventoryExport.xlsx"
    sname, df = io.read_xlsx(input_path)[0]
    assert sname == "Sheet1"
    print(df.columns)
    assert list(df.columns) == [
        "container name",
        "substance cas",
        "container size",
        "unit",
        "barcode",
        "supplier",
        "comments",
        "location",
        "date acquired",
        "smiles",
        "molecular weight",
        "molecular formula",
        "uniqueid_test",
    ]


def test_read_xlsx_no_lower():
    input_path = HERE / "data" / "InventoryExport.xlsx"
    sname, df = io.read_xlsx(input_path, lower_cols=False)[0]
    assert sname == "Sheet1"
    print(df.columns)
    assert list(df.columns) == [
        "Container Name",
        "Substance CAS",
        "Container Size",
        "Unit",
        "Barcode",
        "Supplier",
        "Comments",
        "Location",
        "Date Acquired",
        "SMILES",
        "Molecular Weight",
        "Molecular Formula",
        "UniqueID_TEST",
    ]


def test_read_xlsx_sheet():
    input_path = HERE / "data" / "InventoryExport.xlsx"
    df = io.read_xlsx_sheet(input_path)
    assert list(df.columns) == [
        "container name",
        "substance cas",
        "container size",
        "unit",
        "barcode",
        "supplier",
        "comments",
        "location",
        "date acquired",
        "smiles",
        "molecular weight",
        "molecular formula",
        "uniqueid_test",
    ]
    # check N/A -> None
    assert len(df["substance cas"]) == 4
    assert len([x for x in df["substance cas"] if x is not None]) == 3


def test_write_bad_cas(tmp_path: Path):
    bad_casses = ["list", "of", "casses"]
    output_path = tmp_path / "bad-cas-test.csv"
    io.write_bad_cas(bad_casses, output_path)
    assert output_path.exists()
    with output_path.open() as f:
        for idx, l in enumerate(f):
            assert bad_casses[idx] == l.strip()
