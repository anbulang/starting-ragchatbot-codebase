"""
Pytest configuration and fixtures for the RAG system tests.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import tempfile
import os
import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def mock_config():
    """Mock configuration object for testing."""
    config = Mock()
    config.anthropic_api_key = "test_key"
    config.anthropic_model = "claude-3-haiku-20240307"
    config.chroma_persist_directory = ":memory:"
    config.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    config.max_search_results = 5
    config.max_tokens = 4096
    return config

@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    from vector_store import SearchResults
    
    mock_store = Mock()
    mock_store.search.return_value = SearchResults(
        documents=["Mock document content"],
        metadata=[{"course_title": "Test Course", "lesson_number": 1}],
        distances=[0.1],
        error=None
    )
    mock_store.get_lesson_link.return_value = "https://example.com/lesson1"
    mock_store.add_documents.return_value = None
    mock_store.get_total_document_count.return_value = 1
    return mock_store

@pytest.fixture
def mock_ai_generator():
    """Mock AI generator for testing."""
    mock_ai = Mock()
    mock_ai.generate_response.return_value = "Mock AI response"
    mock_ai.generate_with_tools.return_value = ("Mock AI response", [])
    return mock_ai

@pytest.fixture
def mock_session_manager():
    """Mock session manager for testing."""
    mock_session = Mock()
    mock_session.create_session.return_value = "test_session_123"
    mock_session.add_message.return_value = None
    mock_session.get_history.return_value = []
    return mock_session

@pytest.fixture
def mock_document_processor():
    """Mock document processor for testing."""
    from models import Course, Lesson, CourseChunk
    
    mock_processor = Mock()
    
    # Mock course data
    lesson = Lesson(number=1, title="Test Lesson", content="Test lesson content")
    course = Course(title="Test Course", lessons=[lesson], source_path="/test/path")
    chunk = CourseChunk(
        course_title="Test Course",
        lesson_number=1,
        content="Test chunk content",
        metadata={"course_title": "Test Course", "lesson_number": 1}
    )
    
    mock_processor.process_course_folder.return_value = ([course], [chunk])
    return mock_processor

@pytest.fixture
def mock_rag_system(mock_config, mock_vector_store, mock_ai_generator, 
                   mock_session_manager, mock_document_processor):
    """Mock RAG system with all dependencies."""
    with patch('rag_system.VectorStore', return_value=mock_vector_store), \
         patch('rag_system.AIGenerator', return_value=mock_ai_generator), \
         patch('rag_system.SessionManager', return_value=mock_session_manager), \
         patch('rag_system.DocumentProcessor', return_value=mock_document_processor):
        
        from rag_system import RAGSystem
        return RAGSystem(mock_config)

@pytest.fixture
def sample_course_data():
    """Sample course data for testing."""
    from models import Course, Lesson, CourseChunk
    
    lessons = [
        Lesson(number=1, title="Introduction", content="Welcome to the course"),
        Lesson(number=2, title="Basics", content="Let's learn the basics")
    ]
    
    course = Course(
        title="Python Fundamentals",
        lessons=lessons,
        source_path="/test/python-fundamentals"
    )
    
    chunks = [
        CourseChunk(
            course_title="Python Fundamentals",
            lesson_number=1,
            content="Welcome to the course",
            metadata={"course_title": "Python Fundamentals", "lesson_number": 1}
        ),
        CourseChunk(
            course_title="Python Fundamentals", 
            lesson_number=2,
            content="Let's learn the basics",
            metadata={"course_title": "Python Fundamentals", "lesson_number": 2}
        )
    ]
    
    return course, chunks

@pytest.fixture
def temp_docs_directory():
    """Create a temporary directory with sample documents for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample course structure
        course_dir = Path(temp_dir) / "python-fundamentals"
        course_dir.mkdir()
        
        # Create lesson files
        (course_dir / "1-introduction.md").write_text("# Introduction\nWelcome to Python!")
        (course_dir / "2-variables.md").write_text("# Variables\nLet's learn about variables.")
        
        yield temp_dir

@pytest.fixture(autouse=True)
def suppress_warnings():
    """Suppress common warnings during testing."""
    import warnings
    warnings.filterwarnings("ignore", message="resource_tracker: There appear to be.*")
    warnings.filterwarnings("ignore", category=DeprecationWarning)

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for AI generator tests."""
    with patch('anthropic.Anthropic') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock response structure
        mock_response = Mock()
        mock_response.content = [Mock(text="Mock response")]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response
        
        yield mock_client

@pytest.fixture
def api_test_data():
    """Common test data for API endpoint tests."""
    return {
        "query_request": {
            "query": "What is Python?",
            "session_id": "test_session_123"
        },
        "expected_response": {
            "answer": "Python is a programming language",
            "sources": ["Test source"],
            "session_id": "test_session_123"
        },
        "course_stats": {
            "total_courses": 2,
            "course_titles": ["Python Fundamentals", "Web Development"]
        }
    }

@pytest.fixture
def mock_os_path_exists():
    """Mock os.path.exists to control file existence checks."""
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        yield mock_exists