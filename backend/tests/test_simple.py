#!/usr/bin/env python3
"""
Simple tests that can run without pytest to diagnose the RAG system issues.
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import Mock, MagicMock

def test_course_search_tool_import():
    """Test if we can import CourseSearchTool"""
    try:
        from search_tools import CourseSearchTool
        print("✅ CourseSearchTool import successful")
        return True
    except Exception as e:
        print(f"❌ CourseSearchTool import failed: {e}")
        return False

def test_vector_store_import():
    """Test if we can import VectorStore and SearchResults"""
    try:
        from vector_store import VectorStore, SearchResults
        print("✅ VectorStore and SearchResults import successful")
        return True
    except Exception as e:
        print(f"❌ VectorStore import failed: {e}")
        return False

def test_ai_generator_import():
    """Test if we can import AIGenerator"""
    try:
        from ai_generator import AIGenerator
        print("✅ AIGenerator import successful")
        return True
    except Exception as e:
        print(f"❌ AIGenerator import failed: {e}")
        return False

def test_rag_system_import():
    """Test if we can import RAGSystem"""
    try:
        from rag_system import RAGSystem
        print("✅ RAGSystem import successful")
        return True
    except Exception as e:
        print(f"❌ RAGSystem import failed: {e}")
        return False

def test_course_search_tool_execute():
    """Test CourseSearchTool execute method with mock data"""
    try:
        from search_tools import CourseSearchTool
        from vector_store import SearchResults
        
        # Mock vector store
        mock_vector_store = Mock()
        
        # Test 1: Empty results
        empty_results = SearchResults(
            documents=[],
            metadata=[],
            distances=[],
            error=None
        )
        mock_vector_store.search.return_value = empty_results
        
        tool = CourseSearchTool(mock_vector_store)
        result = tool.execute("test query")
        
        if "No relevant content found" in result:
            print("✅ CourseSearchTool handles empty results correctly")
        else:
            print(f"❌ CourseSearchTool empty results: {result}")
            return False
        
        # Test 2: Error handling  
        error_results = SearchResults(
            documents=[],
            metadata=[],
            distances=[],
            error="Test error message"
        )
        mock_vector_store.search.return_value = error_results
        
        result = tool.execute("test query")
        if result == "Test error message":
            print("✅ CourseSearchTool handles errors correctly")
        else:
            print(f"❌ CourseSearchTool error handling: {result}")
            return False
        
        # Test 3: Successful search
        success_results = SearchResults(
            documents=["This is test content about Python"],
            metadata=[{
                "course_title": "Python Fundamentals", 
                "lesson_number": 1
            }],
            distances=[0.1],
            error=None
        )
        mock_vector_store.search.return_value = success_results
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson1"
        
        result = tool.execute("Python basics")
        
        if "[Python Fundamentals - Lesson 1]" in result and "This is test content about Python" in result:
            print("✅ CourseSearchTool handles successful search correctly")
        else:
            print(f"❌ CourseSearchTool successful search: {result}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ CourseSearchTool execute test failed: {e}")
        return False

def test_tool_manager():
    """Test ToolManager functionality"""
    try:
        from search_tools import ToolManager, CourseSearchTool
        from vector_store import VectorStore
        
        # Create mock vector store
        mock_vector_store = Mock()
        
        # Create tool manager and register tool
        tool_manager = ToolManager()
        search_tool = CourseSearchTool(mock_vector_store)
        tool_manager.register_tool(search_tool)
        
        # Test tool definitions
        definitions = tool_manager.get_tool_definitions()
        if len(definitions) == 1 and definitions[0]['name'] == 'search_course_content':
            print("✅ ToolManager registers tools correctly")
        else:
            print(f"❌ ToolManager tool definitions: {definitions}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ToolManager test failed: {e}")
        return False

def test_ai_generator_basic():
    """Test AIGenerator basic functionality with mocks"""
    try:
        from ai_generator import AIGenerator
        
        # Mock the Anthropic client import
        import unittest.mock
        with unittest.mock.patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            # Create AIGenerator
            ai_gen = AIGenerator("test_key", "test_model")
            
            # Mock response
            mock_response = Mock()
            mock_response.content = [Mock(text="Test response")]
            mock_response.stop_reason = "end_turn"
            mock_client.messages.create.return_value = mock_response
            
            # Test basic response
            result = ai_gen.generate_response("Test query")
            
            if result == "Test response":
                print("✅ AIGenerator basic functionality works")
                return True
            else:
                print(f"❌ AIGenerator basic response: {result}")
                return False
                
    except Exception as e:
        print(f"❌ AIGenerator test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and return success count"""
    tests = [
        test_course_search_tool_import,
        test_vector_store_import, 
        test_ai_generator_import,
        test_rag_system_import,
        test_course_search_tool_execute,
        test_tool_manager,
        test_ai_generator_basic
    ]
    
    passed = 0
    total = len(tests)
    
    print("Running RAG System Diagnostic Tests")
    print("=" * 50)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed < total:
        print("\nSome tests failed. This indicates issues with:")
        print("- Module imports (missing dependencies)")
        print("- Basic functionality (logic errors)")
        print("- Mock setup (test environment issues)")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)