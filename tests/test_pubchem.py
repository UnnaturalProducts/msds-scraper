import pytest

from msds_scraper import pubchem

GOOD_CAS = "50-00-0"
GOOD_CID = 712
BAD_CAS = "OBVIOISLY-FAKE-CAS"


@pytest.mark.vcr
def test_get_cid_from_cas_good_cas():
    cid = pubchem.get_cid_from_cas(GOOD_CAS)
    assert cid == GOOD_CID


@pytest.mark.vcr
def test_get_cid_from_cas_bad_cas():
    with pytest.raises(AssertionError) as e:
        pubchem.get_cid_from_cas(BAD_CAS)
    assert str(e.value) == f"CAS = {BAD_CAS} not found on PubChem"
