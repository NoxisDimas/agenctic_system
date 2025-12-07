import sys
from unittest.mock import MagicMock

# Mock mem0 globally before any test collection imports the app modules
mock_mem0 = MagicMock()
sys.modules["mem0"] = mock_mem0
