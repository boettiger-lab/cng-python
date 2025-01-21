# Confirm environment is correctly defined:
from cng.utils import set_secrets
import ibis

def test_set_secrets():
    con = ibis.duckdb.connect()
    set_secrets(con)

