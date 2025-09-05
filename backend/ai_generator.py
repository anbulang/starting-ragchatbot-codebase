import anthropic
from typing import List, Optional, Dict, Any

class AIGenerator:
    """Handles interactions with Anthropic's Claude API for generating responses"""
    
    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to comprehensive search and outline tools for course information.

Sequential Tool Usage (Up to 2 rounds):
- **Round 1**: Make initial tool calls to gather information
- **Round 2**: Optionally make additional tool calls based on Round 1 results to provide comprehensive answers
- You can reason about previous tool results before deciding on next actions
- Maximum 2 rounds of tool usage allowed per query

Tool Usage Guidelines:
- **Content Search Tool** (`search_course_content`): Use for questions about specific course content, lessons, or detailed educational materials
- **Course Outline Tool** (`get_course_outline`): Use for questions about course structure, lesson lists, course overviews, or when users ask "what's in this course" or similar outline requests
- **Tool Chaining Examples**:
  - Get course outline → Search for specific lesson content based on outline
  - Search for topic → Get detailed content from specific courses found
  - Compare courses: Search one → Search another → Provide comparison
- Synthesize all tool results into accurate, fact-based responses
- If tools yield no results, state this clearly without offering alternatives

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without using tools
- **Course content questions**: Use content search tool first, then refine with additional searches if needed
- **Course outline/structure questions**: Use outline tool first, then search for specific details if helpful
- **Complex queries**: Break down into multiple tool calls across rounds to build comprehensive answers
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, tool explanations, or question-type analysis
 - Do not mention "based on the search results" or "using the outline tool"

For outline queries, always include:
- Course title and link (if available)
- Complete lesson list with numbers and titles
- Instructor information (if available)

All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""
    
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        
        # Pre-build base API parameters
        self.base_params = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 800
        }
        
        # Configuration for sequential tool calling
        self.max_tool_rounds = 2
    
    def generate_response(self, query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None) -> str:
        """
        Generate AI response with optional tool usage and conversation context.
        
        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools
            
        Returns:
            Generated response as string
        """
        
        # Build system content efficiently - avoid string ops when possible
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history 
            else self.SYSTEM_PROMPT
        )
        
        # Prepare API call parameters efficiently
        api_params = {
            **self.base_params,
            "messages": [{"role": "user", "content": query}],
            "system": system_content
        }
        
        # Add tools if available
        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = {"type": "auto"}
        
        # Use sequential tool execution if tools and tool_manager are available
        if tools and tool_manager:
            return self._execute_tool_rounds(api_params, tool_manager)
        
        # Handle non-tool requests with single API call
        response = self.client.messages.create(**api_params)
        return response.content[0].text
    
    def _execute_tool_rounds(self, initial_params: Dict[str, Any], tool_manager) -> str:
        """
        Execute up to 2 rounds of tool calling, allowing Claude to reason about results.
        
        Args:
            initial_params: Base API parameters including messages, system prompt, and tools
            tool_manager: Manager to execute tools
            
        Returns:
            Final response text after all rounds completed
        """
        current_messages = initial_params["messages"].copy()
        system_prompt = initial_params["system"]
        tools = initial_params["tools"]
        
        for round_num in range(1, self.max_tool_rounds + 1):
            # Process current round
            response, updated_messages, should_continue = self._process_tool_round(
                current_messages, system_prompt, tools, tool_manager, round_num
            )
            
            # Update messages for next round
            current_messages = updated_messages
            
            # Check if we should continue to next round
            if not should_continue or round_num >= self.max_tool_rounds:
                # Extract final response text
                if hasattr(response.content[0], 'text'):
                    return response.content[0].text
                else:
                    return str(response.content[0])
        
        # Fallback - should not reach here due to loop conditions
        return "Error: Maximum rounds exceeded without proper termination"
    
    def _process_tool_round(self, current_messages: List[Dict], system_prompt: str, 
                           tools: List, tool_manager, round_num: int) -> tuple:
        """
        Process a single round of tool execution.
        
        Args:
            current_messages: Current conversation messages
            system_prompt: System prompt for the AI
            tools: Available tool definitions
            tool_manager: Manager to execute tools
            round_num: Current round number (1-based)
            
        Returns:
            Tuple of (response, updated_messages, should_continue)
        """
        try:
            # Prepare API parameters for this round
            api_params = {
                **self.base_params,
                "messages": current_messages,
                "system": system_prompt,
                "tools": tools,
                "tool_choice": {"type": "auto"}
            }
            
            # Make API call
            response = self.client.messages.create(**api_params)
            
            # Check if tools were used
            if response.stop_reason == "tool_use":
                # Execute tools and prepare for next round
                updated_messages = self._execute_tools_in_round(
                    response, current_messages, tool_manager
                )
                
                # Determine if we should continue (only if we haven't hit max rounds)
                should_continue = self._should_continue_rounds(response, round_num)
                
                if should_continue:
                    return response, updated_messages, True
                else:
                    # This was the final round - get the final response
                    final_response = self._get_final_response_after_tools(
                        updated_messages, system_prompt
                    )
                    return final_response, updated_messages, False
            else:
                # No tool use - return response directly
                return response, current_messages, False
                
        except Exception as e:
            # Handle errors gracefully
            error_response = self._create_error_response(f"Error in round {round_num}: {str(e)}")
            return error_response, current_messages, False
    
    def _should_continue_rounds(self, response, round_num: int) -> bool:
        """
        Determine if another round of tool execution should occur.
        
        Args:
            response: Current API response
            round_num: Current round number
            
        Returns:
            True if another round should be executed
        """
        # Don't continue if we've reached max rounds
        if round_num >= self.max_tool_rounds:
            return False
        
        # Continue only if tools were used and we haven't hit the limit
        return response.stop_reason == "tool_use"
    
    def _execute_tools_in_round(self, response, current_messages: List[Dict], tool_manager) -> List[Dict]:
        """
        Execute all tools in the current response and return updated messages.
        
        Args:
            response: API response containing tool use requests
            current_messages: Current conversation messages
            tool_manager: Manager to execute tools
            
        Returns:
            Updated messages list with tool results
        """
        # Add AI's tool use response to messages
        messages = current_messages.copy()
        messages.append({"role": "assistant", "content": response.content})
        
        # Execute all tool calls and collect results
        tool_results = []
        for content_block in response.content:
            if content_block.type == "tool_use":
                try:
                    tool_result = tool_manager.execute_tool(
                        content_block.name, 
                        **content_block.input
                    )
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": tool_result
                    })
                except Exception as e:
                    # Handle tool execution errors
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": f"Tool execution error: {str(e)}"
                    })
        
        # Add tool results as user message
        if tool_results:
            messages.append({"role": "user", "content": tool_results})
        
        return messages
    
    def _get_final_response_after_tools(self, messages: List[Dict], system_prompt: str):
        """
        Get final response after tool execution without providing tools for another round.
        
        Args:
            messages: Messages including tool results
            system_prompt: System prompt
            
        Returns:
            Final API response
        """
        final_params = {
            **self.base_params,
            "messages": messages,
            "system": system_prompt
            # Note: No tools provided - this prevents further tool usage
        }
        
        return self.client.messages.create(**final_params)
    
    def _create_error_response(self, error_msg: str):
        """
        Create a mock response object for error cases.
        
        Args:
            error_msg: Error message to include
            
        Returns:
            Mock response with error text
        """
        class ErrorResponse:
            def __init__(self, message):
                self.content = [ErrorContent(message)]
                self.stop_reason = "error"
        
        class ErrorContent:
            def __init__(self, message):
                self.text = message
        
        return ErrorResponse(error_msg)
    
    def _handle_tool_execution(self, initial_response, base_params: Dict[str, Any], tool_manager):
        """
        Handle execution of tool calls and get follow-up response.
        
        Args:
            initial_response: The response containing tool use requests
            base_params: Base API parameters
            tool_manager: Manager to execute tools
            
        Returns:
            Final response text after tool execution
        """
        # Start with existing messages
        messages = base_params["messages"].copy()
        
        # Add AI's tool use response
        messages.append({"role": "assistant", "content": initial_response.content})
        
        # Execute all tool calls and collect results
        tool_results = []
        for content_block in initial_response.content:
            if content_block.type == "tool_use":
                tool_result = tool_manager.execute_tool(
                    content_block.name, 
                    **content_block.input
                )
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": tool_result
                })
        
        # Add tool results as single message
        if tool_results:
            messages.append({"role": "user", "content": tool_results})
        
        # Prepare final API call without tools
        final_params = {
            **self.base_params,
            "messages": messages,
            "system": base_params["system"]
        }
        
        # Get final response
        final_response = self.client.messages.create(**final_params)
        return final_response.content[0].text