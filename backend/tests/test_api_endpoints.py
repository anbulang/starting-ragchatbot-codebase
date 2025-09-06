"""
API endpoint tests for the RAG system FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import json
import os
import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def mock_rag_system():
    """Mock RAG system for API tests."""
    mock_rag = Mock()
    mock_rag.query.return_value = (
        "Python is a high-level programming language.",
        ["Python documentation", "Python tutorial"]
    )
    mock_rag.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Python Fundamentals", "Web Development"]
    }
    mock_rag.add_course_folder.return_value = (2, 10)
    mock_rag.session_manager.create_session.return_value = "new_session_456"
    return mock_rag


@pytest.fixture
def test_app(mock_rag_system, mock_os_path_exists):
    """Create test FastAPI app with mocked dependencies."""
    with patch('app.RAGSystem', return_value=mock_rag_system), \
         patch('app.config') as mock_config:
        
        mock_config.anthropic_api_key = "test_key"
        
        # Import app after patching
        from app import app
        
        # Override the static files mount to avoid missing directory issues
        app.router.routes = [route for route in app.router.routes 
                           if not hasattr(route, 'path') or route.path != "/"]
        
        return app


@pytest.fixture 
def client(test_app):
    """Test client for API endpoints."""
    return TestClient(test_app)


class TestQueryEndpoint:
    """Tests for the /api/query endpoint."""
    
    @pytest.mark.api
    def test_query_with_session_id(self, client, mock_rag_system):
        """Test query endpoint with existing session ID."""
        request_data = {
            "query": "What is Python?",
            "session_id": "existing_session_123"
        }
        
        response = client.post("/api/query", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["session_id"] == "existing_session_123"
        assert data["answer"] == "Python is a high-level programming language."
        assert len(data["sources"]) == 2
        
        # Verify RAG system was called correctly
        mock_rag_system.query.assert_called_once_with("What is Python?", "existing_session_123")
    
    @pytest.mark.api
    def test_query_without_session_id(self, client, mock_rag_system):
        """Test query endpoint without session ID (should create new session)."""
        request_data = {
            "query": "Explain variables in Python"
        }
        
        response = client.post("/api/query", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["session_id"] == "new_session_456"
        
        # Verify new session was created
        mock_rag_system.session_manager.create_session.assert_called_once()
        mock_rag_system.query.assert_called_once_with("Explain variables in Python", "new_session_456")
    
    @pytest.mark.api
    def test_query_empty_string(self, client):
        """Test query endpoint with empty query string."""
        request_data = {"query": ""}
        
        response = client.post("/api/query", json=request_data)
        
        assert response.status_code == 200
        # Should still process empty query
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
    
    @pytest.mark.api
    def test_query_missing_required_field(self, client):
        """Test query endpoint with missing required query field."""
        request_data = {"session_id": "test_session"}
        
        response = client.post("/api/query", json=request_data)
        
        assert response.status_code == 422  # Unprocessable Entity
    
    @pytest.mark.api
    def test_query_invalid_json(self, client):
        """Test query endpoint with invalid JSON."""
        response = client.post("/api/query", data="invalid json")
        
        assert response.status_code == 422
    
    @pytest.mark.api
    def test_query_rag_system_error(self, client, mock_rag_system):
        """Test query endpoint when RAG system raises an exception."""
        mock_rag_system.query.side_effect = Exception("RAG system error")
        
        request_data = {"query": "What is Python?"}
        
        response = client.post("/api/query", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "RAG system error" in data["detail"]


class TestCoursesEndpoint:
    """Tests for the /api/courses endpoint."""
    
    @pytest.mark.api
    def test_get_course_stats_success(self, client, mock_rag_system):
        """Test successful course stats retrieval."""
        response = client.get("/api/courses")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_courses" in data
        assert "course_titles" in data
        assert data["total_courses"] == 2
        assert len(data["course_titles"]) == 2
        assert "Python Fundamentals" in data["course_titles"]
        assert "Web Development" in data["course_titles"]
        
        mock_rag_system.get_course_analytics.assert_called_once()
    
    @pytest.mark.api
    def test_get_course_stats_error(self, client, mock_rag_system):
        """Test course stats endpoint when analytics fails."""
        mock_rag_system.get_course_analytics.side_effect = Exception("Analytics error")
        
        response = client.get("/api/courses")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Analytics error" in data["detail"]


class TestNewSessionEndpoint:
    """Tests for the /api/new-session endpoint."""
    
    @pytest.mark.api
    def test_create_new_session_success(self, client, mock_rag_system):
        """Test successful new session creation."""
        response = client.post("/api/new-session")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert "message" in data
        assert data["session_id"] == "new_session_456"
        assert "New session created" in data["message"]
        
        mock_rag_system.session_manager.create_session.assert_called_once()
    
    @pytest.mark.api
    def test_create_new_session_error(self, client, mock_rag_system):
        """Test new session endpoint when creation fails."""
        mock_rag_system.session_manager.create_session.side_effect = Exception("Session creation failed")
        
        response = client.post("/api/new-session")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Session creation failed" in data["detail"]


class TestResponseModels:
    """Test response model validation."""
    
    @pytest.mark.api
    def test_query_response_model(self, client):
        """Test that query response matches expected model structure."""
        request_data = {"query": "Test query"}
        
        response = client.post("/api/query", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = ["answer", "sources", "session_id"]
        for field in required_fields:
            assert field in data
        
        # Verify data types
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["session_id"], str)
    
    @pytest.mark.api
    def test_course_stats_response_model(self, client):
        """Test that course stats response matches expected model structure."""
        response = client.get("/api/courses")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = ["total_courses", "course_titles"]
        for field in required_fields:
            assert field in data
        
        # Verify data types
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)
        
        # Verify course titles are strings
        for title in data["course_titles"]:
            assert isinstance(title, str)


class TestCORSAndMiddleware:
    """Test CORS and middleware functionality."""
    
    @pytest.mark.api
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.options("/api/query")
        
        # Check for key CORS headers (exact headers may vary by FastAPI version)
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods", 
            "access-control-allow-headers"
        ]
        
        response_headers_lower = {k.lower(): v for k, v in response.headers.items()}
        
        # At least one CORS header should be present
        cors_present = any(header in response_headers_lower for header in cors_headers)
        assert cors_present, f"No CORS headers found in: {list(response.headers.keys())}"
    
    @pytest.mark.api
    def test_trusted_host_middleware_allows_requests(self, client):
        """Test that trusted host middleware allows requests."""
        # This should not be blocked by trusted host middleware
        response = client.get("/api/courses")
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling across endpoints."""
    
    @pytest.mark.api
    def test_404_for_nonexistent_endpoint(self, client):
        """Test 404 response for non-existent endpoints."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_405_for_wrong_method(self, client):
        """Test 405 response for wrong HTTP method."""
        response = client.get("/api/query")  # Should be POST
        assert response.status_code == 405
        
        response = client.post("/api/courses")  # Should be GET
        assert response.status_code == 405


@pytest.mark.integration
class TestEndToEndAPIFlow:
    """Integration tests for complete API workflows."""
    
    def test_complete_chat_session_flow(self, client, mock_rag_system):
        """Test complete flow: create session, ask questions, get stats."""
        # Step 1: Create new session
        session_response = client.post("/api/new-session")
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        
        # Step 2: Ask first question
        query1 = {"query": "What is Python?", "session_id": session_id}
        response1 = client.post("/api/query", json=query1)
        assert response1.status_code == 200
        assert response1.json()["session_id"] == session_id
        
        # Step 3: Ask follow-up question
        query2 = {"query": "Tell me about variables", "session_id": session_id}
        response2 = client.post("/api/query", json=query2)
        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id
        
        # Step 4: Get course statistics
        stats_response = client.get("/api/courses")
        assert stats_response.status_code == 200
        assert "total_courses" in stats_response.json()
        
        # Verify all calls used the same session
        query_calls = mock_rag_system.query.call_args_list
        assert len(query_calls) == 2
        assert all(call[0][1] == session_id for call in query_calls)