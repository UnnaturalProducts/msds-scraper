import pytest


@pytest.fixture(scope="module")
def vcr_config():
    # Store response bodies decompressed so replay works regardless of the
    # recorded Content-Encoding (vcrpy does not re-decompress gzip on replay).
    return {"decode_compressed_response": True}
