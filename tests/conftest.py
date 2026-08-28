from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def load():
    from receipts.adapters import load as _load

    return lambda name: _load(FIXTURES / name)
