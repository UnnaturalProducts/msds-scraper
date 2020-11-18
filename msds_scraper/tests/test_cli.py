from os import devnull
from msds_scraper.__main__ import main
import pathlib
from unittest.mock import patch
import os


@patch("msds_scraper.__main__.print")
def test_cli(printer):
    """Test the cli is working. In this cas there is a missing cas so the print function should be called once."""
    input_path = str(pathlib.Path(__file__).parent.absolute() / "data" / "InventoryExport.xlsx")
    output_path = str(pathlib.Path(__file__).parent.absolute() / "data" / "msds_output")
    main(args=[input_path, output_path, "-s", "--bad_cas_output", os.devnull])
    assert printer.called