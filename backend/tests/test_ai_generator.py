import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai_generator import AIGenerator

class MockToolUseBlock:
    """Mock for Anthropic's tool use content block."""
    def __init__(self, name, input_data, block_id="test_id"):
        self.type = "tool_use"
        self.name = name
        self.input = input_data
        self.id = block_id

class MockTextBlock:
    """Mock for Anthropic's text content block."""
    def __init__(self, text):
        self.type = "text"
        self.text = text

class MockAnthropicResponse:
    """Mock for Anthropic API response."""
    def __init__(self, content, stop_reason="end_turn"):
        self.content = content
        self.stop_reason = stop_reason

class TestAIGenerator:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test_api_key"
        self.model = "claude-3-sonnet-20240229"
        
        # Mock the Anthropic client
        with patch('anthropic.Anthropic') as mock_anthropic:
            self.mock_client = Mock()
            mock_anthropic.return_value = self.mock_client
            self.ai_generator = AIGenerator(self.api_key, self.model)
    
    def test_generate_response_without_tools(self):
        """Test basic response generation without tools."""
        # Mock response
        mock_response = MockAnthropicResponse([MockTextBlock("This is a test response")])
        self.mock_client.messages.create.return_value = mock_response
        
        result = self.ai_generator.generate_response("What is Python?")
        
        assert result == "This is a test response"
        
        # Verify API call
        self.mock_client.messages.create.assert_called_once()
        call_args = self.mock_client.messages.create.call_args[1]
        assert call_args["model"] == self.model
        assert call_args["temperature"] == 0
        assert call_args["max_tokens"] == 800
        assert len(call_args["messages"]) == 1
        assert call_args["messages"][0]["role"] == "user"
        assert call_args["messages"][0]["content"] == "What is Python?"
    
    def test_generate_response_with_conversation_history(self):
        """Test response generation with conversation history."""
        mock_response = MockAnthropicResponse([MockTextBlock("Response with history")])
        self.mock_client.messages.create.return_value = mock_response
        
        history = "Previous conversation context"
        result = self.ai_generator.generate_response("Follow up question", conversation_history=history)
        
        assert result == "Response with history"
        
        # Verify system prompt includes history
        call_args = self.mock_client.messages.create.call_args[1]
        assert "Previous conversation context" in call_args["system"]
    
    def test_generate_response_with_tools_no_tool_use(self):
        """Test response generation with tools available but not used."""
        mock_response = MockAnthropicResponse([MockTextBlock("Regular response")])
        self.mock_client.messages.create.return_value = mock_response
        
        mock_tools = [{"name": "search_course_content", "description": "Search tool"}]
        result = self.ai_generator.generate_response("General question", tools=mock_tools)
        
        assert result == "Regular response"
        
        # Verify tools were included in API call
        call_args = self.mock_client.messages.create.call_args[1]
        assert "tools" in call_args
        assert call_args["tools"] == mock_tools
        assert call_args["tool_choice"] == {"type": "auto"}
    
    def test_generate_response_with_tool_use(self):
        """Test response generation when AI decides to use tools."""
        # Mock initial response with tool use
        tool_use_block = MockToolUseBlock("search_course_content", {"query": "Python basics"})
        initial_response = MockAnthropicResponse([tool_use_block], stop_reason="tool_use")
        
        # Mock final response after tool execution
        final_response = MockAnthropicResponse([MockTextBlock("Final response with tool results")])
        
        # Set up multiple returns for the create method
        self.mock_client.messages.create.side_effect = [initial_response, final_response]
        
        # Mock tool manager
        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.return_value = "Search results: Python is a programming language"
        
        mock_tools = [{"name": "search_course_content", "description": "Search tool"}]
        
        result = self.ai_generator.generate_response(
            "What is Python?",
            tools=mock_tools,
            tool_manager=mock_tool_manager
        )
        
        assert result == "Final response with tool results"
        
        # Verify tool was executed
        mock_tool_manager.execute_tool.assert_called_once_with(
            "search_course_content",
            query="Python basics"
        )
        
        # Verify two API calls were made
        assert self.mock_client.messages.create.call_count == 2
    
    def test_handle_tool_execution_single_tool(self):
        """Test the internal _handle_tool_execution method with single tool."""
        # Create mock initial response with tool use
        tool_use_block = MockToolUseBlock(
            "search_course_content", 
            {"query": "test query", "course_name": "Python"},
            "tool_123"
        )
        initial_response = MockAnthropicResponse([tool_use_block], stop_reason="tool_use")
        
        # Mock final response
        final_response = MockAnthropicResponse([MockTextBlock("Tool execution complete")])
        self.mock_client.messages.create.return_value = final_response
        
        # Mock tool manager
        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.return_value = "Mock search results"
        
        # Test base parameters
        base_params = {
            "model": self.model,
            "messages": [{"role": "user", "content": "test query"}],
            "system": "test system prompt",
            "temperature": 0,
            "max_tokens": 800
        }
        
        result = self.ai_generator._handle_tool_execution(initial_response, base_params, mock_tool_manager)
        
        assert result == "Tool execution complete"
        
        # Verify tool execution
        mock_tool_manager.execute_tool.assert_called_once_with(
            "search_course_content",
            query="test query",
            course_name="Python"
        )
        
        # Verify final API call structure
        call_args = self.mock_client.messages.create.call_args[1]
        assert len(call_args["messages"]) == 3  # Original user + assistant tool use + user tool results
        
        # Check tool result structure
        tool_result_message = call_args["messages"][2]
        assert tool_result_message["role"] == "user"
        assert len(tool_result_message["content"]) == 1
        
        tool_result = tool_result_message["content"][0]
        assert tool_result["type"] == "tool_result"
        assert tool_result["tool_use_id"] == "tool_123"
        assert tool_result["content"] == "Mock search results"
    
    def test_handle_tool_execution_multiple_tools(self):
        """Test handling of multiple tool calls in one response."""
        # Create multiple tool use blocks
        tool1 = MockToolUseBlock("search_course_content", {"query": "Python"}, "tool_1")
        tool2 = MockToolUseBlock("get_course_outline", {"course_title": "Python"}, "tool_2")
        
        initial_response = MockAnthropicResponse([tool1, tool2], stop_reason="tool_use")
        
        # Mock final response
        final_response = MockAnthropicResponse([MockTextBlock("Multiple tools executed")])
        self.mock_client.messages.create.return_value = final_response
        
        # Mock tool manager
        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.side_effect = ["Search result", "Outline result"]
        
        base_params = {
            "model": self.model,
            "messages": [{"role": "user", "content": "test"}],
            "system": "test system",
            "temperature": 0,
            "max_tokens": 800
        }
        
        result = self.ai_generator._handle_tool_execution(initial_response, base_params, mock_tool_manager)
        
        assert result == "Multiple tools executed"
        assert mock_tool_manager.execute_tool.call_count == 2
        
        # Check both tool calls
        calls = mock_tool_manager.execute_tool.call_args_list
        assert calls[0][0][0] == "search_course_content"
        assert calls[1][0][0] == "get_course_outline"
    
    def test_tool_execution_with_exception(self):
        """Test handling when tool execution raises an exception."""
        # This test simulates what happens if the tool_manager.execute_tool fails
        tool_use_block = MockToolUseBlock("search_course_content", {"query": "test"}, "tool_123")
        initial_response = MockAnthropicResponse([tool_use_block], stop_reason="tool_use")
        
        # Mock tool manager that raises exception
        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.side_effect = Exception("Tool execution failed")
        
        base_params = {
            "model": self.model,
            "messages": [{"role": "user", "content": "test"}],
            "system": "test system",
            "temperature": 0,
            "max_tokens": 800
        }
        
        # This should raise the exception since we don't have error handling in the method
        with pytest.raises(Exception, match="Tool execution failed"):
            self.ai_generator._handle_tool_execution(initial_response, base_params, mock_tool_manager)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])