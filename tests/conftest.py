import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.database import init_db, drop_db
from app.ratelimit import rate_limiter


@pytest.fixture(autouse=True)
def reset_state():
    drop_db()
    init_db()
    rate_limiter._buckets.clear()
    yield
    drop_db()