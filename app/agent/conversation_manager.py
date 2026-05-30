from sqlalchemy.orm import Session
from google.genai import types
from app.repositories.customer_repository import CustomerRepository
from app.repositories.message_repository import MessageRepository
from app.database.models import Message
from app.agent.gemini_client import gemini_agent_client
from app.agent.system_prompt import SYSTEM_PROMPT
from app.agent.memory_manager import MemoryManager
from app.agent.tool_executor import ALL_AGENT_TOOLS, TOOL_DISPATCH_MAP
from app.core.logger import logger

class ConversationManager:
    @staticmethod
    def process_message(db: Session, phone_number: str, user_name: str, message_content: str, whatsapp_message_id: str = None) -> str:
        """
        Orchestrates session memory loading, Gemini generation, recursive tool execution,
        and database message persistence.
        """
        cust_repo = CustomerRepository(db)
        msg_repo = MessageRepository(db)
        
        # 1. Fetch or create customer profile
        customer = cust_repo.get_or_create(phone_number, name=user_name)
        
        # 2. Log user's incoming message in database
        user_msg = Message(
            customer_id=customer.id,
            sender_type="USER",
            content=message_content,
            whatsapp_message_id=whatsapp_message_id
        )
        msg_repo.create(user_msg)
        
        # 3. Load chronological conversation history
        contents = MemoryManager.get_conversation_history(db, customer, message_content)
        
        # 4. Invoke Gemini in a tool execution loop
        max_tool_loops = 5
        loop_count = 0
        final_reply = ""
        
        while loop_count < max_tool_loops:
            response = gemini_agent_client.generate_response(
                contents=contents,
                tools=ALL_AGENT_TOOLS,
                system_instruction=SYSTEM_PROMPT
            )
            
            # Check if Gemini wants to call a tool
            function_calls = []
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                function_calls = [p.function_call for p in response.candidates[0].content.parts if p.function_call]
                
            if function_calls:
                logger.info(f"Gemini requested tool execution: {len(function_calls)} calls.")
                
                # Append model's response (with tool calls) to the history
                contents.append(response.candidates[0].content)
                
                tool_parts = []
                for call in function_calls:
                    tool_name = call.name
                    tool_args = call.args
                    
                    # Execute tool
                    if tool_name in TOOL_DISPATCH_MAP:
                        try:
                            # If phone number is needed but not provided in arguments, inject it
                            if tool_name == "create_order" and "phone_number" not in tool_args:
                                tool_args["phone_number"] = phone_number
                                
                            result = TOOL_DISPATCH_MAP[tool_name](**tool_args)
                            logger.info(f"Tool {tool_name} returned: {result}")
                        except Exception as err:
                            logger.error(f"Tool execution failed for {tool_name}: {str(err)}")
                            result = {"error": f"Internal execution error: {str(err)}"}
                    else:
                        logger.warning(f"Requested unknown tool: {tool_name}")
                        result = {"error": f"Tool '{tool_name}' is not registered."}
                        
                    # Build function response part
                    # The response object must be wrapped in a dict
                    wrapped_result = result if isinstance(result, dict) else {"result": result}
                    part = types.Part.from_function_response(
                        name=tool_name,
                        response=wrapped_result
                    )
                    tool_parts.append(part)
                    
                # Append tool responses as a new message of role 'tool'
                tool_content = types.Content(
                    role="tool",
                    parts=tool_parts
                )
                contents.append(tool_content)
                
                loop_count += 1
            else:
                # No more tool calls; we have the final text reply
                final_reply = response.text
                break
                
        if not final_reply:
            final_reply = "I'm sorry, I encountered an issue processing that request. How can I help you today? 🎂"
            
        # 5. Log agent's final outgoing message in database
        agent_msg = Message(
            customer_id=customer.id,
            sender_type="AGENT",
            content=final_reply
        )
        msg_repo.create(agent_msg)
        
        logger.info(f"Final response resolved for {phone_number}: '{final_reply[:50]}...'")
        return final_reply
