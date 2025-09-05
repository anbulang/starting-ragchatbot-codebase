import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from search_tools import CourseSearchTool
from vector_store import SearchResults

class TestCourseSearchTool:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_vector_store = Mock()
        self.search_tool = CourseSearchTool(self.mock_vector_store)
    
    def test_execute_successful_search(self):
        """Test successful search returns formatted results."""
        # Mock successful search results
        mock_results = SearchResults(
            documents=["This is lesson content about Python basics"],
            metadata=[{
                "course_title": "Python Fundamentals",
                "lesson_number": 1
            }],
            distances=[0.1],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results
        self.mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson1"
        
        # Execute search
        result = self.search_tool.execute("Python basics")
        
        # Verify the search was called correctly
        self.mock_vector_store.search.assert_called_once_with(
            query="Python basics",
            course_name=None,
            lesson_number=None
        )
        
        # Verify result formatting
        assert "[Python Fundamentals - Lesson 1]" in result
        assert "This is lesson content about Python basics" in result
        assert len(self.search_tool.last_sources) == 1
        
        # Check that source includes lesson link
        source = self.search_tool.last_sources[0]
        assert isinstance(source, dict)
        assert source["text"] == "Python Fundamentals - Lesson 1"
        assert source["link"] == "https://example.com/lesson1"
    
    def test_execute_with_course_filter(self):
        """Test search with course name filter."""
        mock_results = SearchResults(
            documents=["Advanced Python concepts"],
            metadata=[{
                "course_title": "Advanced Python",
                "lesson_number": 3
            }],
            distances=[0.2],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results
        self.mock_vector_store.get_lesson_link.return_value = None
        
        result = self.search_tool.execute("concepts", course_name="Advanced Python")
        
        self.mock_vector_store.search.assert_called_once_with(
            query="concepts",
            course_name="Advanced Python",
            lesson_number=None
        )
        
        assert "[Advanced Python - Lesson 3]" in result
        assert "Advanced Python concepts" in result
    
    def test_execute_with_lesson_filter(self):
        """Test search with lesson number filter."""
        mock_results = SearchResults(
            documents=["Lesson 2 content"],
            metadata=[{
                "course_title": "JavaScript Basics",
                "lesson_number": 2
            }],
            distances=[0.15],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results
        self.mock_vector_store.get_lesson_link.return_value = "https://example.com/js-lesson2"
        
        result = self.search_tool.execute("variables", lesson_number=2)
        
        self.mock_vector_store.search.assert_called_once_with(
            query="variables",
            course_name=None,
            lesson_number=2
        )
        
        assert "[JavaScript Basics - Lesson 2]" in result
        assert "Lesson 2 content" in result
    
    def test_execute_search_error(self):
        """Test handling of search errors."""
        mock_results = SearchResults(
            documents=[],
            metadata=[],
            distances=[],
            error="Database connection failed"
        )
        self.mock_vector_store.search.return_value = mock_results
        
        result = self.search_tool.execute("test query")
        
        assert result == "Database connection failed"
        assert len(self.search_tool.last_sources) == 0
    
    def test_execute_empty_results(self):
        """Test handling of empty search results."""
        mock_results = SearchResults(
            documents=[],
            metadata=[],
            distances=[],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results
        
        result = self.search_tool.execute("nonexistent topic")
        
        assert result == "No relevant content found."
        assert len(self.search_tool.last_sources) == 0
    
    def test_execute_empty_results_with_filters(self):
        """Test empty results with filter information."""
        mock_results = SearchResults(
            documents=[],
            metadata=[],
            distances=[],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results
        
        result = self.search_tool.execute("topic", course_name="Python", lesson_number=5)
        
        expected_msg = "No relevant content found in course 'Python' in lesson 5."
        assert result == expected_msg
    
    def test_execute_multiple_results(self):
        """Test handling of multiple search results."""
        mock_results = SearchResults(
            documents=[
                "First result about functions",
                "Second result about functions"
            ],
            metadata=[
                {"course_title": "Python Basics", "lesson_number": 3},
                {"course_title": "Python Advanced", "lesson_number": 1}
            ],
            distances=[0.1, 0.2],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results
        self.mock_vector_store.get_lesson_link.side_effect = [
            "https://example.com/basic-lesson3",
            "https://example.com/advanced-lesson1"
        ]
        
        result = self.search_tool.execute("functions")
        
        assert "[Python Basics - Lesson 3]" in result
        assert "[Python Advanced - Lesson 1]" in result
        assert "First result about functions" in result
        assert "Second result about functions" in result
        assert len(self.search_tool.last_sources) == 2
    
    def test_execute_no_lesson_number(self):
        """Test handling when lesson_number is None in metadata."""
        mock_results = SearchResults(
            documents=["General course content"],
            metadata=[{
                "course_title": "Introduction to Programming",
                "lesson_number": None
            }],
            distances=[0.3],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results
        
        result = self.search_tool.execute("programming")
        
        assert "[Introduction to Programming]" in result  # No lesson number
        assert "General course content" in result
        
        # Check source format without lesson
        source = self.search_tool.last_sources[0]
        assert source == "Introduction to Programming"  # String, not dict
    
    def test_execute_missing_metadata(self):
        """Test handling when metadata is missing required fields."""
        mock_results = SearchResults(
            documents=["Content with incomplete metadata"],
            metadata=[{}],  # Empty metadata
            distances=[0.4],
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results
        
        result = self.search_tool.execute("test")
        
        assert "[unknown]" in result  # Default course title
        assert "Content with incomplete metadata" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])