#!/usr/bin/env python3
"""
Live diagnosis script to test the RAG system components in the actual environment.
This script will be run inside Docker container to diagnose real issues.
"""

import sys
import os
import traceback
import json

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test if all modules can be imported successfully"""
    print("🔍 Testing imports...")
    modules = {}
    
    try:
        from models import Course, Lesson, CourseChunk
        modules['models'] = "✅ SUCCESS"
        print("✅ Models imported successfully")
    except Exception as e:
        modules['models'] = f"❌ FAILED: {e}"
        print(f"❌ Models import failed: {e}")
    
    try:
        from vector_store import VectorStore, SearchResults
        modules['vector_store'] = "✅ SUCCESS" 
        print("✅ VectorStore imported successfully")
    except Exception as e:
        modules['vector_store'] = f"❌ FAILED: {e}"
        print(f"❌ VectorStore import failed: {e}")
    
    try:
        from search_tools import CourseSearchTool, CourseOutlineTool, ToolManager
        modules['search_tools'] = "✅ SUCCESS"
        print("✅ SearchTools imported successfully")
    except Exception as e:
        modules['search_tools'] = f"❌ FAILED: {e}"
        print(f"❌ SearchTools import failed: {e}")
    
    try:
        from ai_generator import AIGenerator
        modules['ai_generator'] = "✅ SUCCESS"
        print("✅ AIGenerator imported successfully")
    except Exception as e:
        modules['ai_generator'] = f"❌ FAILED: {e}"
        print(f"❌ AIGenerator import failed: {e}")
    
    try:
        from rag_system import RAGSystem
        modules['rag_system'] = "✅ SUCCESS"
        print("✅ RAGSystem imported successfully")
    except Exception as e:
        modules['rag_system'] = f"❌ FAILED: {e}"
        print(f"❌ RAGSystem import failed: {e}")
    
    return modules

def test_vector_store_initialization():
    """Test VectorStore initialization"""
    print("\n🔍 Testing VectorStore initialization...")
    
    try:
        from vector_store import VectorStore
        
        # Try to initialize vector store with test parameters
        vs = VectorStore(
            chroma_path="./test_chroma",
            embedding_model="all-MiniLM-L6-v2",
            max_results=5
        )
        print("✅ VectorStore initialized successfully")
        
        # Test search with empty store
        from vector_store import SearchResults
        results = vs.search("test query")
        
        if isinstance(results, SearchResults):
            print("✅ VectorStore search returns SearchResults")
            if results.is_empty():
                print("✅ Empty store returns empty results correctly")
            else:
                print("⚠️ Empty store returned non-empty results")
        else:
            print(f"❌ VectorStore search returned wrong type: {type(results)}")
        
        return True
        
    except Exception as e:
        print(f"❌ VectorStore initialization failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_search_tool():
    """Test CourseSearchTool functionality"""
    print("\n🔍 Testing CourseSearchTool...")
    
    try:
        from search_tools import CourseSearchTool
        from vector_store import VectorStore, SearchResults
        
        # Create mock vector store
        vs = VectorStore(
            chroma_path="./test_chroma",
            embedding_model="all-MiniLM-L6-v2",
            max_results=5
        )
        
        # Create search tool
        search_tool = CourseSearchTool(vs)
        
        # Test tool definition
        tool_def = search_tool.get_tool_definition()
        if tool_def.get('name') == 'search_course_content':
            print("✅ CourseSearchTool has correct tool definition")
        else:
            print(f"❌ CourseSearchTool wrong tool name: {tool_def.get('name')}")
        
        # Test execution with empty store
        result = search_tool.execute("test query")
        if isinstance(result, str) and len(result) > 0:
            print(f"✅ CourseSearchTool execute returned: {result[:50]}...")
        else:
            print(f"❌ CourseSearchTool execute failed: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ CourseSearchTool test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_ai_generator():
    """Test AIGenerator with mock data"""
    print("\n🔍 Testing AIGenerator...")
    
    try:
        from ai_generator import AIGenerator
        
        # Try to create AIGenerator (this might fail if no API key)
        try:
            ai_gen = AIGenerator("dummy_key", "claude-3-sonnet")
            print("✅ AIGenerator initialized")
            
            # Test system prompt
            if hasattr(ai_gen, 'SYSTEM_PROMPT') and ai_gen.SYSTEM_PROMPT:
                print("✅ AIGenerator has system prompt")
                if 'tool' in ai_gen.SYSTEM_PROMPT.lower():
                    print("✅ System prompt mentions tools")
                else:
                    print("⚠️ System prompt may not properly instruct tool usage")
            else:
                print("❌ AIGenerator missing system prompt")
                
        except Exception as e:
            print(f"⚠️ AIGenerator init failed (expected without API key): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ AIGenerator test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_rag_system_initialization():
    """Test RAGSystem initialization"""
    print("\n🔍 Testing RAGSystem initialization...")
    
    try:
        # Create mock config
        class MockConfig:
            CHUNK_SIZE = 1000
            CHUNK_OVERLAP = 200
            CHROMA_PATH = "./test_chroma"
            EMBEDDING_MODEL = "all-MiniLM-L6-v2"
            MAX_RESULTS = 5
            ANTHROPIC_API_KEY = "dummy_key"
            ANTHROPIC_MODEL = "claude-3-sonnet"
            MAX_HISTORY = 10
        
        from rag_system import RAGSystem
        config = MockConfig()
        
        rag = RAGSystem(config)
        print("✅ RAGSystem initialized successfully")
        
        # Check tool manager
        if hasattr(rag, 'tool_manager') and rag.tool_manager:
            print("✅ RAGSystem has tool manager")
            
            # Check tool definitions
            tools = rag.tool_manager.get_tool_definitions()
            if isinstance(tools, list) and len(tools) > 0:
                print(f"✅ RAGSystem has {len(tools)} tools registered")
                for tool in tools:
                    print(f"  - {tool.get('name', 'Unknown')}")
            else:
                print("❌ RAGSystem has no tools registered")
        else:
            print("❌ RAGSystem missing tool manager")
        
        return True
        
    except Exception as e:
        print(f"❌ RAGSystem initialization failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_full_query_flow():
    """Test the complete query flow (without API calls)"""
    print("\n🔍 Testing full query flow (mock)...")
    
    try:
        # Mock config
        class MockConfig:
            CHUNK_SIZE = 1000
            CHUNK_OVERLAP = 200
            CHROMA_PATH = "./test_chroma"
            EMBEDDING_MODEL = "all-MiniLM-L6-v2"
            MAX_RESULTS = 5
            ANTHROPIC_API_KEY = "dummy_key"
            ANTHROPIC_MODEL = "claude-3-sonnet"
            MAX_HISTORY = 10
        
        from rag_system import RAGSystem
        config = MockConfig()
        rag = RAGSystem(config)
        
        print("✅ RAGSystem ready for query")
        
        # Test if we can call the query method (it will fail at AI call)
        try:
            response, sources = rag.query("What is Python?")
            print(f"❌ Unexpected success: {response}")
        except Exception as e:
            # This is expected to fail at the AI API call
            if "api" in str(e).lower() or "key" in str(e).lower() or "anthropic" in str(e).lower():
                print("✅ Query flow reaches AI API call (as expected)")
            else:
                print(f"❌ Query failed before AI API call: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Full query flow test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def check_data_directory():
    """Check if docs directory exists and has content"""
    print("\n🔍 Checking data directory...")
    
    docs_path = "../docs"
    if os.path.exists(docs_path):
        files = os.listdir(docs_path)
        if files:
            print(f"✅ Found {len(files)} files in docs directory:")
            for file in files[:5]:  # Show first 5 files
                print(f"  - {file}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")
        else:
            print("⚠️ docs directory is empty - no course content to search")
    else:
        print("❌ docs directory not found - no course content available")

def run_live_diagnosis():
    """Run all live diagnostic tests"""
    print("RAG System Live Diagnosis")
    print("=" * 50)
    
    results = {}
    
    # Run all tests
    results['imports'] = test_imports()
    results['vector_store_init'] = test_vector_store_initialization()
    results['search_tool'] = test_search_tool()
    results['ai_generator'] = test_ai_generator()
    results['rag_system_init'] = test_rag_system_initialization()
    results['query_flow'] = test_full_query_flow()
    
    check_data_directory()
    
    print("\n" + "=" * 50)
    print("DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    # Count successful tests
    import_successes = sum(1 for status in results['imports'].values() if "SUCCESS" in status)
    total_imports = len(results['imports'])
    
    other_successes = sum(1 for key, success in results.items() if key != 'imports' and success)
    total_other = len(results) - 1
    
    print(f"✅ Imports: {import_successes}/{total_imports}")
    print(f"✅ Other tests: {other_successes}/{total_other}")
    
    # Identify potential issues
    print(f"\nPOTENTIAL ISSUES:")
    failed_imports = [module for module, status in results['imports'].items() if "FAILED" in status]
    if failed_imports:
        print(f"❌ Failed imports: {failed_imports}")
    
    failed_tests = [test for test, success in results.items() if test != 'imports' and not success]
    if failed_tests:
        print(f"❌ Failed tests: {failed_tests}")
    
    if not failed_imports and not failed_tests:
        print("✅ All basic functionality appears to be working!")
        print("The 'query failed' issue may be:")
        print("1. Missing course documents in docs/")
        print("2. Anthropic API key issues")
        print("3. ChromaDB data corruption")
        print("4. Runtime errors during actual queries")
    
    return results

if __name__ == "__main__":
    results = run_live_diagnosis()
    
    # Save results for analysis
    try:
        with open('diagnosis_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to diagnosis_results.json")
    except Exception as e:
        print(f"Could not save results: {e}")
    
    sys.exit(0)