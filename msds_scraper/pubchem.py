import pubchempy as pcp
import typer


def get_cid_from_cas(cas: str) -> int:
    """Resolve a CAS number to a PubChem CID via PubChem's name lookup.

    Raises AssertionError (the source-failure signal used across this package)
    when PubChem has no compound for the CAS.
    """
    cids = pcp.get_cids(cas, "name")
    assert cids, f"CAS = {cas} not found on PubChem"
    if len(cids) > 1:
        typer.echo(f"Multiple CIDs for CAS = {cas}: {cids} - using first ({cids[0]})")
    return cids[0]
