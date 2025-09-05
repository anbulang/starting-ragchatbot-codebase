#!/usr/bin/env python3
"""
Code analysis tests to identify potential issues without external dependencies.
These tests analyze the source code directly to find common RAG chatbot failure patterns.
"""

import sys
import os
import re

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def analyze_search_tools():
    """Analyze search_tools.py for common issues"""
    print("🔍 Analyzing search_tools.py...")
    
    try:
        with open('search_tools.py', 'r') as f:
            content = f.read()
        
        issues = []
        
        # Check for proper error handling in execute method
        if 'results.error' in content:
            print("✅ CourseSearchTool checks for search errors")
        else:
            issues.append("❌ CourseSearchTool missing error checking")
        
        # Check for empty results handling
        if 'is_empty()' in content:
            print("✅ CourseSearchTool checks for empty results")
        else:
            issues.append("❌ CourseSearchTool missing empty results check")
        
        # Check if vector store search is called correctly
        if 'self.store.search(' in content:
            print("✅ CourseSearchTool calls vector store search")
        else:
            issues.append("❌ CourseSearchTool not calling vector store search")
        
        # Check for result formatting
        if '_format_results' in content:
            print("✅ CourseSearchTool has result formatting")
        else:
            issues.append("❌ CourseSearchTool missing result formatting")
        
        # Check tool definition structure
        tool_def_pattern = r'"name":\s*"search_course_content"'
        if re.search(tool_def_pattern, content):
            print("✅ CourseSearchTool has correct tool definition name")
        else:
            issues.append("❌ CourseSearchTool incorrect tool definition")
        
        return issues
        
    except Exception as e:
        return [f"❌ Could not analyze search_tools.py: {e}"]

def analyze_ai_generator():
    """Analyze ai_generator.py for common issues"""
    print("\n🔍 Analyzing ai_generator.py...")
    
    try:
        with open('../ai_generator.py', 'r') as f:
            content = f.read()
        
        issues = []
        
        # Check for tool execution handling
        if 'tool_use' in content and '_handle_tool_execution' in content:
            print("✅ AIGenerator handles tool execution")
        else:
            issues.append("❌ AIGenerator missing tool execution handling")
        
        # Check for proper tool parameters
        if 'tools' in content and 'tool_manager' in content:
            print("✅ AIGenerator accepts tools and tool_manager")
        else:
            issues.append("❌ AIGenerator missing tool support parameters")
        
        # Check for API error handling
        if 'try:' in content or 'except' in content:
            print("✅ AIGenerator has some error handling")
        else:
            issues.append("❌ AIGenerator missing error handling")
        
        # Check system prompt for tool instructions
        if 'tool' in content.lower() and 'search' in content.lower():
            print("✅ AIGenerator system prompt mentions tools")
        else:
            issues.append("❌ AIGenerator system prompt may not instruct tool usage")
        
        return issues
        
    except Exception as e:
        return [f"❌ Could not analyze ai_generator.py: {e}"]

def analyze_rag_system():
    """Analyze rag_system.py for common issues"""
    print("\n🔍 Analyzing rag_system.py...")
    
    try:
        with open('../rag_system.py', 'r') as f:
            content = f.read()
        
        issues = []
        
        # Check if tools are properly initialized
        if 'ToolManager()' in content and 'register_tool' in content:
            print("✅ RAGSystem initializes and registers tools")
        else:
            issues.append("❌ RAGSystem missing tool initialization")
        
        # Check if tools are passed to AI generator
        if 'self.tool_manager.get_tool_definitions()' in content:
            print("✅ RAGSystem passes tool definitions to AI")
        else:
            issues.append("❌ RAGSystem not passing tools to AI generator")
        
        # Check if tool manager is passed
        if 'tool_manager=self.tool_manager' in content:
            print("✅ RAGSystem passes tool manager to AI")
        else:
            issues.append("❌ RAGSystem not passing tool manager to AI")
        
        # Check for error handling in query method
        if 'try:' in content or 'except' in content:
            print("✅ RAGSystem has some error handling")
        else:
            issues.append("❌ RAGSystem missing error handling in query method")
        
        return issues
        
    except Exception as e:
        return [f"❌ Could not analyze rag_system.py: {e}"]

def analyze_vector_store():
    """Analyze vector_store.py for common issues"""
    print("\n🔍 Analyzing vector_store.py...")
    
    try:
        with open('../vector_store.py', 'r') as f:
            content = f.read()
        
        issues = []
        
        # Check SearchResults class
        if 'class SearchResults:' in content:
            print("✅ VectorStore has SearchResults class")
        else:
            issues.append("❌ VectorStore missing SearchResults class")
        
        # Check for error handling in search method
        if 'error' in content and 'SearchResults' in content:
            print("✅ VectorStore search method handles errors")
        else:
            issues.append("❌ VectorStore search missing error handling")
        
        # Check for empty results handling
        if 'is_empty' in content:
            print("✅ VectorStore has empty results checking")
        else:
            issues.append("❌ VectorStore missing empty results check")
        
        # Check for proper ChromaDB integration
        if 'chromadb' in content and 'query' in content:
            print("✅ VectorStore integrates with ChromaDB")
        else:
            issues.append("❌ VectorStore missing ChromaDB integration")
        
        return issues
        
    except Exception as e:
        return [f"❌ Could not analyze vector_store.py: {e}"]

def check_file_dependencies():
    """Check if all required files exist"""
    print("\n🔍 Checking file dependencies...")
    
    required_files = [
        'search_tools.py',
        'ai_generator.py', 
        'rag_system.py',
        'vector_store.py',
        'models.py',
        'app.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file} exists")
    
    if missing_files:
        return [f"❌ Missing files: {missing_files}"]
    
    return []

def identify_potential_query_failure_causes():
    """Identify potential causes for 'query failed' responses"""
    print("\n🔍 Identifying potential 'query failed' causes...")
    
    potential_causes = []
    
    # Check if there's any hardcoded "query failed" message
    files_to_check = ['../app.py', '../rag_system.py', '../ai_generator.py', '../search_tools.py']
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if 'query failed' in content.lower():
                    potential_causes.append(f"❌ Found 'query failed' hardcoded in {file_path}")
        except Exception as e:
            potential_causes.append(f"❌ Could not check {file_path}: {e}")
    
    # Check for exception handling that might swallow errors
    try:
        with open('../rag_system.py', 'r') as f:
            content = f.read()
            # Look for bare except clauses that might hide real errors
            if re.search(r'except:\s*$', content, re.MULTILINE):
                potential_causes.append("❌ RAGSystem has bare except clause that might hide errors")
    except Exception as e:
        potential_causes.append(f"❌ Could not check exception handling: {e}")
    
    # Check if AI system prompt allows for failure responses
    try:
        with open('../ai_generator.py', 'r') as f:
            content = f.read()
            if 'SYSTEM_PROMPT' in content:
                print("✅ Found system prompt in AIGenerator")
                # Extract system prompt to analyze
                prompt_match = re.search(r'SYSTEM_PROMPT\s*=\s*"""(.*?)"""', content, re.DOTALL)
                if prompt_match:
                    prompt = prompt_match.group(1)
                    if 'error' in prompt.lower() or 'fail' in prompt.lower():
                        potential_causes.append("⚠️ System prompt mentions errors/failures - might encourage failure responses")
                    if 'tools' not in prompt.lower():
                        potential_causes.append("❌ System prompt doesn't mention tools usage")
            else:
                potential_causes.append("❌ No system prompt found in AIGenerator")
    except Exception as e:
        potential_causes.append(f"❌ Could not analyze system prompt: {e}")
    
    return potential_causes

def run_code_analysis():
    """Run complete code analysis"""
    print("RAG System Code Analysis")
    print("=" * 50)
    
    all_issues = []
    
    # Run all analyses
    all_issues.extend(check_file_dependencies())
    all_issues.extend(analyze_search_tools()) 
    all_issues.extend(analyze_ai_generator())
    all_issues.extend(analyze_rag_system())
    all_issues.extend(analyze_vector_store())
    all_issues.extend(identify_potential_query_failure_causes())
    
    print("\n" + "=" * 50)
    print("ANALYSIS SUMMARY")
    print("=" * 50)
    
    if all_issues:
        print("Issues found:")
        for issue in all_issues:
            print(issue)
    else:
        print("✅ No obvious code issues found!")
    
    print(f"\nTotal issues: {len(all_issues)}")
    
    return all_issues

if __name__ == "__main__":
    issues = run_code_analysis()
    
    if issues:
        print("\n" + "=" * 50)
        print("RECOMMENDATIONS:")
        print("=" * 50)
        print("1. Fix missing dependencies in Docker environment")
        print("2. Add proper error handling where missing") 
        print("3. Verify tool registration and execution flow")
        print("4. Check system prompts for tool usage instructions")
        print("5. Add logging to trace execution flow")
    
    sys.exit(1 if issues else 0)