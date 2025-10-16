from strands.hooks import MessageAddedEvent, HookProvider, HookRegistry, AgentInitializedEvent, BeforeToolCallEvent, AfterToolCallEvent
import logging

logger = logging.getLogger(__name__)

class MemoryHookProvider(HookProvider):
    def __init__(self, memory_client, memory_id: str):
        self.memory_client = memory_client
        self.memory_id = memory_id
    
    def on_agent_initialized(self, event: AgentInitializedEvent):
        """Load recent conversation history when agent starts"""
        try:
            # Get session info from agent state
            actor_id = event.agent.state.get("actor_id")
            session_id = event.agent.state.get("session_id")
            
            print(f"🔍 DEBUG: Loading memory for session: {session_id}, actor: {actor_id}")
            
            if not actor_id or not session_id:
                logger.warning("Missing actor_id or session_id in agent state")
                return
            
            # Load the last 5 conversation turns from memory
            recent_turns = self.memory_client.get_last_k_turns(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id=session_id,
                k=10
            )
            
            print(f"🔍 DEBUG: Found {len(recent_turns)} recent turns in memory")
            
            if recent_turns:
                # Format conversation history for context
                context_messages = []
                for turn in recent_turns:
                    for message in turn:
                        role = message['role']
                        content = message['content']['text']
                        context_messages.append(f"{role}: {content}")
                        # print(f"🔍 DEBUG: Loading - {role}: {content[:50]}...")
                
                context = "\n".join(context_messages)
                # Add context to agent's system prompt
                original_length = len(event.agent.system_prompt)
                event.agent.system_prompt += f"\n\nRecent conversation:\n{context}"
                
                # print(f"🔍 DEBUG: Added {len(context_messages)} messages to system prompt")
                # print(f"🔍 DEBUG: Prompt length: {original_length} → {len(event.agent.system_prompt)}")
                
            else:
                print("🔍 DEBUG: No previous conversation found in memory")
                
        except Exception as e:
            print(f"❌ DEBUG: Memory load error: {e}")
            logger.error(f"Memory load error: {e}")
    
    def on_message_added(self, event: MessageAddedEvent):
        """Store messages in memory"""
        messages = event.agent.messages
        try:
            # Get session info from agent state
            actor_id = event.agent.state.get("actor_id")
            session_id = event.agent.state.get("session_id")

            if messages and messages[-1]["content"][0].get("text"):
                message_text = messages[-1]["content"][0]["text"]
                message_role = messages[-1]["role"]
                
                print(f"💬 DEBUG: Storing message - {message_role}: {message_text[:50]}...")
                
                self.memory_client.create_event(
                    memory_id=self.memory_id,
                    actor_id=actor_id,
                    session_id=session_id,
                    messages=[(message_text, message_role)]
                )
                
        except Exception as e:
            print(f"❌ DEBUG: Message storage error: {e}")
            logger.error(f"Memory save error: {e}")
    
    def on_before_tool_call(self, event: BeforeToolCallEvent):
        """Store tool execution start in memory"""
        try:
            actor_id = event.agent.state.get("actor_id")
            session_id = event.agent.state.get("session_id")
            
            # Extract tool information from the event
            tool_name = event.tool_use.get('name', 'unknown_tool')
            tool_input = event.tool_use.get('input', {})
            
            print(f"🔧 DEBUG: Tool starting - {tool_name} for session: {session_id}")
            print(f"🔧 DEBUG: Tool input: {tool_input}")
            
            # Store tool call start
            self.memory_client.create_event(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id=session_id,
                messages=[(f"🔧 Tool starting: {tool_name} with input: {tool_input}", "TOOL")]
            )
            
        except Exception as e:
            print(f"❌ DEBUG: Tool start storage error: {e}")
            logger.error(f"Tool start memory error: {e}")
    
    def on_after_tool_call(self, event: AfterToolCallEvent):
        """Store tool results in memory - THIS IS CRITICAL!"""
        try:
            actor_id = event.agent.state.get("actor_id")
            session_id = event.agent.state.get("session_id")
            
            # Extract tool information
            tool_name = event.tool_use.get('name', 'unknown_tool')
            
            # Extract tool output from event.result
            tool_output = "No output"
            if event.result and 'content' in event.result:
                content_list = event.result['content']
                if content_list and 'text' in content_list[0]:
                    tool_output = content_list[0]['text']
            
            print(f"✅ DEBUG: Tool completed - {tool_name} for session: {session_id}")
            print(f"✅ DEBUG: Tool output: {tool_output[:200]}...")
            
            # Store tool result - THIS IS WHAT OTHER TOOLS NEED!
            self.memory_client.create_event(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id=session_id,
                messages=[(f"✅ Tool completed: {tool_name}\nOutput: {tool_output}", "TOOL")]
            )
            
            print(f"✅ DEBUG: Stored tool result for {tool_name}")
            
        except Exception as e:
            print(f"❌ DEBUG: Tool end storage error: {e}")
            logger.error(f"Tool end memory error: {e}")
    
    def register_hooks(self, registry: HookRegistry):
        # Register ALL FOUR hooks - your workflow depends on them!
        registry.add_callback(MessageAddedEvent, self.on_message_added)
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)
        registry.add_callback(BeforeToolCallEvent, self.on_before_tool_call)
        registry.add_callback(AfterToolCallEvent, self.on_after_tool_call)
        
        print("✅ DEBUG: All memory hooks registered successfully")