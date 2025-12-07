import pytest
import sys
from unittest.mock import MagicMock

from app.memory.controller import MemoryController
from app.memory.models import MemoryItem

@pytest.fixture
def mock_mem0_instance():
    # Retrieve the mock object from sys.modules
    mock_mem0 = sys.modules["mem0"]
    
    # Setup the mock class behavior
    mock_instance = MagicMock()
    mock_mem0.Memory.return_value = mock_instance
    
    # Setup default return values
    mock_instance.add.return_value = {"id": "123", "memory": "test", "user_id": "u1", "metadata": {"type": "test"}}
    mock_instance.get_all.return_value = []
    return mock_instance

def test_memory_crud(mock_mem0_instance):
    # Re-instantiate to use the mock
    controller = MemoryController()
    
    user_id = "user1"
    
    # Test Add
    mock_mem0_instance.add.return_value = {
        "id": "mem_1",
        "user_id": user_id,
        "memory": "likes pizza",
        "metadata": {"type": "preference", "tags": []}
    }
    
    item = controller.add_memory(user_id, "likes pizza", type="preference")
    assert item.content == "likes pizza"
    assert item.user_id == user_id
    assert item.metadata["type"] == "preference"
    
    mock_mem0_instance.add.assert_called_with("likes pizza", user_id=user_id, metadata={"type": "preference"})
    
    # Test Get
    mock_mem0_instance.get_all.return_value = [
        {
            "id": "mem_1",
            "user_id": user_id,
            "memory": "likes pizza",
            "metadata": {"type": "preference"}
        }
    ]
    
    items = controller.get_memory(user_id)
    assert len(items) == 1
    assert items[0].id == "mem_1"
    
    # Test Clear
    controller.clear_memory(user_id)
    mock_mem0_instance.delete_all.assert_called_with(user_id=user_id)

def test_memory_type_filtering(mock_mem0_instance):
    controller = MemoryController()
    user_id = "user1"
    
    mock_mem0_instance.get_all.return_value = [
        {"id": "1", "user_id": user_id, "memory": "A", "metadata": {"type": "preference"}},
        {"id": "2", "user_id": user_id, "memory": "B", "metadata": {"type": "issue"}}
    ]
    
    prefs = controller.get_memory(user_id, types=["preference"])
    assert len(prefs) == 1
    assert prefs[0].content == "A"
