import pytest
import os



integration = pytest.mark.skipif(
    "CI" not in os.environ and "TEST_INTEGRATION" not in os.environ,
    reason="Integration tests autoskipped",
)
