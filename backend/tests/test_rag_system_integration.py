import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rag_system import RAGSystem
from vector_store import SearchResults
from models import Course, Lesson, CourseChunk

class MockConfig:
    """Mock configuration for testing."""
    def __init__(self):
        self.CHUNK_SIZE = 1000
        self.CHUNK_OVERLAP = 200
        self.CHROMA_PATH = "test_chroma"
        self.EMBEDDING_MODEL = "test_model"
        self.MAX_RESULTS = 5
        self.ANTHROPIC_API_KEY = "test_key"
        self.ANTHROPIC_MODEL = "claude-3-sonnet"
        self.MAX_HISTORY = 10

class TestRAGSystemIntegration:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.config = MockConfig()
        
        # Mock all the dependencies
        with patch('rag_system.DocumentProcessor'), \
             patch('rag_system.VectorStore') as mock_vector_store, \
             patch('rag_system.AIGenerator') as mock_ai_generator, \
             patch('rag_system.SessionManager') as mock_session_manager:
            
            self.rag_system = RAGSystem(self.config)
            self.mock_vector_store = self.rag_system.vector_store
            self.mock_ai_generator = self.rag_system.ai_generator
            self.mock_session_manager = self.rag_system.session_manager
    
    def test_query_successful_content_search(self):
        """Test successful content query with tool-based search."""
        # Mock vector store search returning results
        mock_search_results = SearchResults(
            documents=["Python is a programming language that emphasizes readability"],
            metadata=[{
                "course_title": "Python Fundamentals",
                "lesson_number": 1
            }],
            distances=[0.1],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_search_results
        self.mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson1"
        
        # Mock AI generator returning a proper response after tool use
        self.mock_ai_generator.generate_response.return_value = "Python is a high-level programming language known for its readability and simplicity."
        
        # Mock session manager
        self.mock_session_manager.get_conversation_history.return_value = None
        
        # Execute query
        response, sources = self.rag_system.query("What is Python?")
        
        # Verify AI generator was called with correct parameters
        self.mock_ai_generator.generate_response.assert_called_once()
        call_args = self.mock_ai_generator.generate_response.call_args
        
        # Check the query parameter
        assert "Answer this question about course materials: What is Python?" in call_args[1]["query"]
        
        # Check that tools were provided
        assert call_args[1]["tools"] is not None
        assert call_args[1]["tool_manager"] is not None
        
        # Verify response
        assert response == "Python is a high-level programming language known for its readability and simplicity."
    
    def test_query_with_session_history(self):
        """Test query with conversation history."""
        # Mock session history
        mock_history = "Previous: User asked about variables. Assistant explained Python variables."
        self.mock_session_manager.get_conversation_history.return_value = mock_history
        
        # Mock AI response
        self.mock_ai_generator.generate_response.return_value = "Building on variables, functions are..."
        
        response, sources = self.rag_system.query("What about functions?", session_id="test_session")
        
        # Verify history was passed to AI generator
        call_args = self.mock_ai_generator.generate_response.call_args[1]
        assert call_args["conversation_history"] == mock_history
        
        # Verify session was updated
        self.mock_session_manager.add_exchange.assert_called_once_with(
            "test_session", 
            "What about functions?", 
            "Building on variables, functions are..."
        )
    
    def test_query_with_tool_sources(self):
        """Test that sources from tool searches are properly retrieved."""
        # Mock tool manager returning sources
        mock_sources = [
            {"text": "Python Fundamentals - Lesson 1", "link": "https://example.com/lesson1"},
            "JavaScript Basics - Lesson 2"
        ]
        
        # Mock the get_last_sources method
        self.rag_system.tool_manager.get_last_sources = Mock(return_value=mock_sources)
        self.rag_system.tool_manager.reset_sources = Mock()
        
        self.mock_ai_generator.generate_response.return_value = "Here's information about programming languages."
        
        response, sources = self.rag_system.query("Tell me about programming languages")
        
        # Verify sources were retrieved and reset
        self.rag_system.tool_manager.get_last_sources.assert_called_once()
        self.rag_system.tool_manager.reset_sources.assert_called_once()
        
        # Check sources are returned
        assert sources == mock_sources
    
    def test_query_handles_search_errors(self):
        """Test how the system handles search errors."""
        # The error handling should happen in the tool, but let's test end-to-end
        
        # Mock AI generator to simulate what would happen if search tool returns error
        self.mock_ai_generator.generate_response.return_value = "I apologize, but I encountered an error searching the course materials."
        
        response, sources = self.rag_system.query("What is machine learning?")
        
        # Even with errors, we should get a response
        assert "error" in response.lower() or "apologize" in response.lower()
        
        # Verify AI generator was still called
        self.mock_ai_generator.generate_response.assert_called_once()
    
    def test_query_prompt_format(self):
        """Test that the query is formatted correctly for the AI."""
        self.mock_ai_generator.generate_response.return_value = "Test response"
        
        self.rag_system.query("How do I install Python?")
        
        # Check the prompt format
        call_args = self.mock_ai_generator.generate_response.call_args[1]
        expected_prompt = "Answer this question about course materials: How do I install Python?"
        assert call_args["query"] == expected_prompt
    
    def test_tool_definitions_provided(self):
        """Test that tool definitions are properly provided to the AI."""
        # Mock tool definitions
        expected_tools = [
            {"name": "search_course_content", "description": "Search tool"},
            {"name": "get_course_outline", "description": "Outline tool"}
        ]
        self.rag_system.tool_manager.get_tool_definitions = Mock(return_value=expected_tools)
        
        self.mock_ai_generator.generate_response.return_value = "Test response"
        
        self.rag_system.query("Test question")
        
        # Verify tools were provided
        call_args = self.mock_ai_generator.generate_response.call_args[1]
        assert call_args["tools"] == expected_tools
        assert call_args["tool_manager"] == self.rag_system.tool_manager
    
    def test_empty_query_handling(self):
        """Test handling of empty or whitespace-only queries."""
        self.mock_ai_generator.generate_response.return_value = "I need more information to help you."
        
        response, sources = self.rag_system.query("")
        
        # Should still process the query
        assert response == "I need more information to help you."
        self.mock_ai_generator.generate_response.assert_called_once()
    
    def test_system_configuration(self):
        """Test that the RAG system is properly configured."""
        # Verify all components are initialized
        assert self.rag_system.document_processor is not None
        assert self.rag_system.vector_store is not None
        assert self.rag_system.ai_generator is not None
        assert self.rag_system.session_manager is not None
        assert self.rag_system.tool_manager is not None
        
        # Verify tools are registered
        tools = self.rag_system.tool_manager.tools
        assert "search_course_content" in tools
        assert "get_course_outline" in tools
    
    def test_course_analytics(self):
        """Test the course analytics functionality."""
        # Mock vector store methods
        self.mock_vector_store.get_course_count.return_value = 3
        self.mock_vector_store.get_existing_course_titles.return_value = ["Course A", "Course B", "Course C"]
        
        analytics = self.rag_system.get_course_analytics()
        
        assert analytics["total_courses"] == 3
        assert analytics["course_titles"] == ["Course A", "Course B", "Course C"]

class TestRAGSystemRealScenarios:
    """Test realistic scenarios that might cause 'query failed' responses."""
    
    def setup_method(self):
        self.config = MockConfig()
        
        with patch('rag_system.DocumentProcessor'), \
             patch('rag_system.VectorStore') as mock_vector_store, \
             patch('rag_system.AIGenerator') as mock_ai_generator, \
             patch('rag_system.SessionManager') as mock_session_manager:
            
            self.rag_system = RAGSystem(self.config)
            self.mock_vector_store = self.rag_system.vector_store
            self.mock_ai_generator = self.rag_system.ai_generator
            self.mock_session_manager = self.rag_system.session_manager
    
    def test_scenario_empty_vector_store(self):
        """Test scenario where vector store has no data."""
        # Simulate empty vector store - search returns no results
        empty_results = SearchResults(
            documents=[],
            metadata=[],
            distances=[],
            error=None
        )
        self.mock_vector_store.search.return_value = empty_results
        
        # AI should still respond even with no search results
        self.mock_ai_generator.generate_response.return_value = "I don't have information about that topic in the course materials."
        
        response, sources = self.rag_system.query("What is Python?")
        
        # Should not return "query failed"
        assert "query failed" not in response.lower()
        assert response == "I don't have information about that topic in the course materials."
    
    def test_scenario_vector_store_error(self):
        """Test scenario where vector store returns an error."""
        # Simulate database error
        error_results = SearchResults(
            documents=[],
            metadata=[],
            distances=[],
            error="ChromaDB connection failed"
        )
        self.mock_vector_store.search.return_value = error_results
        
        # The tool should handle the error and return it
        # AI might respond with this error information
        self.mock_ai_generator.generate_response.return_value = "I encountered a database error while searching for information."
        
        response, sources = self.rag_system.query("What is Python?")
        
        # Check that we get a meaningful error message, not just "query failed"
        assert "database error" in response.lower()
    
    def test_scenario_anthropic_api_error(self):
        """Test scenario where Anthropic API fails."""
        # Mock Anthropic API failure
        self.mock_ai_generator.generate_response.side_effect = Exception("API rate limit exceeded")
        
        # This should raise an exception that needs to be handled at a higher level
        with pytest.raises(Exception, match="API rate limit exceeded"):
            self.rag_system.query("What is Python?")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])