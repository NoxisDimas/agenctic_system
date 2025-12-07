import pytest
from unittest.mock import MagicMock, patch
from app.vectorstore.controller import QdrantController, Domain
from langchain_core.documents import Document

@patch('app.vectorstore.controller.QdrantClient')
def test_add_documents(mock_qdrant_client):
    controller = QdrantController()
    
    # Mock the internal vectorstore getter to return a mock
    mock_vectorstore = MagicMock()
    controller._get_vectorstore = MagicMock(return_value=mock_vectorstore)
    
    docs = [Document(page_content="test")]
    controller.add_documents(Domain.FAQ, docs)
    
    controller._get_vectorstore.assert_called_with(Domain.FAQ)
    mock_vectorstore.add_documents.assert_called_with(docs)

@patch('app.vectorstore.controller.QdrantClient')
def test_search(mock_qdrant_client):
    controller = QdrantController()
    
    mock_vectorstore = MagicMock()
    mock_vectorstore.similarity_search.return_value = [Document(page_content="result")]
    controller._get_vectorstore = MagicMock(return_value=mock_vectorstore)
    
    results = controller.search(Domain.FAQ, "query")
    assert len(results) == 1
    assert results[0].page_content == "result"
