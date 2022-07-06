import shlex
from pathlib import Path
from black import out

import pytest
from msds_scraper import cli
from typer.testing import CliRunner

runner = CliRunner()

HERE = Path(__file__).parent


@pytest.mark.vcr
def test_cli(tmp_path):
    input_xlsx = HERE / "data" / "InventoryExport.xlsx"
    bad_cas_output = tmp_path / "bad-cas.csv"
    expected_bad_cas = HERE / "data" / "bad-cas.csv"
    pdf_output = tmp_path / "msds_outout"
    cmd = f"{input_xlsx} {pdf_output} --bad-cas-output {bad_cas_output} -w 1"
    output = runner.invoke(cli.app, shlex.split(cmd))
    assert output.exit_code == 0
    assert "Found 3 new CAS to query" in output.stdout
    assert "Found 1 bad CAS" in output.stdout
    assert bad_cas_output.exists()
    assert pdf_output.exists()
    assert sorted(list(map(lambda x: x.name, pdf_output.glob("*.pdf")))) == [
        "109-99-9.pdf",
        "88050-17-3.pdf",
    ]
    # compare to expected
    with bad_cas_output.open() as out_f:
        with expected_bad_cas.open() as e_f:
            for l in out_f:
                assert e_f.readline() == l


def mock_get_cas(cas, *args, **kwargs):
    """Only return cas for bad cas"""
    if cas == "885272-87-7XXXy":
        return cas
    return None


def test_cli_workers(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "get_cas", mock_get_cas)
    input_xlsx = HERE / "data" / "InventoryExport.xlsx"
    bad_cas_output = tmp_path / "bad-cas.csv"
    pdf_output = tmp_path / "msds_outout"
    cmd = f"{input_xlsx} {pdf_output} --bad-cas-output {bad_cas_output} -w 2"
    output = runner.invoke(cli.app, shlex.split(cmd))
    assert output.exit_code == 0
    assert "Found 3 new CAS to query" in output.stdout
    assert "Found 1 bad CAS" in output.stdout
    assert "n_jobs=2" in output.stdout
    assert bad_cas_output.exists()
    assert pdf_output.exists()
    # make sure monkeypatching worked
    assert len(list(pdf_output.glob("*.pdf"))) == 0


def test_cli_no_verbose(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "get_cas", mock_get_cas)
    input_xlsx = HERE / "data" / "InventoryExport.xlsx"
    bad_cas_output = tmp_path / "bad-cas.csv"
    pdf_output = tmp_path / "msds_outout"
    cmd = (
        f"{input_xlsx} {pdf_output} --bad-cas-output {bad_cas_output} -w 1 --no-verbose"
    )
    output = runner.invoke(cli.app, shlex.split(cmd))
    assert output.exit_code == 0
    assert "Found 3 new CAS to query" in output.stdout
    assert "Found 1 bad CAS" in output.stdout
    assert "n_jobs" not in output.stdout
    assert bad_cas_output.exists()
    assert pdf_output.exists()
    # make sure monkeypatching worked
    assert len(list(pdf_output.glob("*.pdf"))) == 0
