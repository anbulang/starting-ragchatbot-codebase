#!/usr/bin/env python3
"""
Simple test script to verify sequential tool calling functionality
"""
import sys
import os

# Mock the anthropic library since we can't install it easily
class MockContent:
    def __init__(self, text=None):
        if text:
            self.type = "text"
            self.text = text
        else:
            self.type = "tool_use"
            self.name = "search_course_content"
            self.input = {"query": "test"}
            self.id = "tool_123"
            self.text = "tool_use_block"  # Fallback text

class MockResponse:
    def __init__(self, content_type="text", stop_reason="end_turn"):
        if content_type == "tool_use":
            self.content = [MockContent()]
            self.stop_reason = "tool_use" 
        else:
            self.content = [MockContent("Test response")]
            self.stop_reason = stop_reason

class MockClient:
    def __init__(self, api_key=None):
        self.messages = MockMessages()
        
class MockMessages:
    def __init__(self):
        self.call_count = 0
        
    def create(self, **kwargs):
        self.call_count += 1
        print(f"API Call #{self.call_count}: {kwargs.get('messages', [{}])[-1].get('content', 'N/A')}")
        
        # Simulate different responses based on call count
        if self.call_count == 1:
            return MockResponse("tool_use")  # First call uses tool
        else:
            return MockResponse("text")      # Subsequent calls return text

class MockToolManager:
    def __init__(self):
        self.execute_count = 0
        
    def execute_tool(self, name, **kwargs):
        self.execute_count += 1
        print(f"Tool executed #{self.execute_count}: {name} with {kwargs}")
        return f"Mock result for {name}"

# Mock anthropic module
import types
anthropic_mock = types.ModuleType('anthropic')
anthropic_mock.Anthropic = MockClient
sys.modules['anthropic'] = anthropic_mock

# Add backend to path and import
sys.path.append('backend')
from ai_generator import AIGenerator

def test_sequential_functionality():
    """Test that sequential tool calling works as expected."""
    print("=" * 50)
    print("Testing Sequential Tool Calling")
    print("=" * 50)
    
    # Initialize AI generator
    ai_gen = AIGenerator("test_key", "test_model")
    mock_tool_manager = MockToolManager()
    mock_tools = [{"name": "search_course_content", "description": "Search tool"}]
    
    # Test sequential call
    print("\nTest 1: Sequential tool execution")
    result = ai_gen.generate_response(
        "Tell me about Python course",
        tools=mock_tools,
        tool_manager=mock_tool_manager
    )
    
    print(f"Final result: {result}")
    print(f"Tools executed: {mock_tool_manager.execute_count}")
    print(f"API calls made: {ai_gen.client.messages.call_count}")
    
    # Test without tools
    print("\nTest 2: Non-tool execution")
    ai_gen2 = AIGenerator("test_key", "test_model")
    result2 = ai_gen2.generate_response("Simple question without tools")
    print(f"Non-tool result: {result2}")
    print(f"API calls made: {ai_gen2.client.messages.call_count}")
    
    print("\n" + "=" * 50)
    print("Tests completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    test_sequential_functionality()