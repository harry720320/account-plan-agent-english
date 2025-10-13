"""
Conversation management module
Responsible for managing multi-turn conversations and AI summaries
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from models import Interaction, Account
from datetime import datetime
import json
import openai
from config import settings
from prompts import Prompts

class ConversationManager:
    """Conversation manager"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def start_conversation(self, 
                               db: Session, 
                               account_id: int, 
                               question: str, 
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start Conversation"""
        try:
            # Check if there is historical summary for this question
            previous_summary = await self._get_question_summary(db, account_id, question)
            
            # Generate AI's initial question
            ai_question = await self._generate_initial_question(question, previous_summary, context)
            
            # Create conversation records
            conversation = {
                "conversation_id": f"conv_{account_id}_{int(datetime.now().timestamp())}",
                "account_id": account_id,
                "original_question": question,
                "previous_summary": previous_summary,
                "messages": [
                    {"role": "assistant", "content": ai_question}
                ],
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
            
            return conversation
            
        except Exception as e:
            return {"error": str(e)}
    
    async def continue_conversation(self, 
                                  conversation: Dict[str, Any], 
                                  user_message: str) -> Dict[str, Any]:
        """Continue conversation"""
        try:
            # Add user response
            conversation["messages"].append({
                "role": "user", 
                "content": user_message
            })
            
            # Generate AI's next question
            ai_question = await self._generate_follow_up_question(conversation)
            
            # Add AI question
            conversation["messages"].append({
                "role": "assistant", 
                "content": ai_question
            })
            
            return conversation
            
        except Exception as e:
            return {"error": str(e)}
    
    async def end_conversation(self, 
                              db: Session, 
                              conversation: Dict[str, Any]) -> Dict[str, Any]:
        """End conversation and generate summary"""
        try:
            # Generate conversation summary
            summary = await self._generate_conversation_summary(conversation)
            
            # Extract structured data
            structured_data = await self._extract_structured_data(conversation, summary)
            
            # Save to database
            interaction = await self._save_conversation_to_db(
                db, conversation, summary, structured_data
            )
            
            return {
                "conversation_id": conversation["conversation_id"],
                "interaction_id": interaction.id,
                "summary": summary,
                "structured_data": structured_data,
                "message": "Conversation saved"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_question_summary(self, db: Session, account_id: int, question: str) -> str:
        """Get historical summary for specific question"""
        try:
            # Find historical summary for this question
            interaction = db.query(Interaction).filter(
                Interaction.account_id == account_id,
                Interaction.question == question,
                Interaction.interaction_type == "conversation"
            ).order_by(Interaction.created_at.desc()).first()
            
            if interaction and interaction.structured_data:
                return interaction.structured_data.get("summary", "")
            
            return ""
            
        except Exception as e:
            return ""
    
    async def _generate_initial_question(self, 
                                       original_question: str, 
                                       previous_summary: str, 
                                       context: Dict[str, Any] = None) -> str:
        """Generate initial question"""
        try:
            # Build a prompt to start the conversation based on the original question
            prompt = f"""
            You are starting a conversation with a customer to gather information about: {original_question}
            
            {f"Historical context from previous conversations: {previous_summary}" if previous_summary else "This is the first conversation on this topic."}
            
            {f"Additional context: {context}" if context else ""}
            
            Generate an opening question to initiate this conversation. The question should:
            1. Be professional and friendly
            2. Encourage the customer to share detailed information
            3. Be specific to the topic: {original_question}
            4. Be open-ended to allow for comprehensive responses
            
            Please provide a single opening question:
            """
            
            # gpt-5 uses Responses API
            response = self.openai_client.responses.create(
                model=settings.conversation_model,
                instructions=Prompts.CUSTOMER_MANAGER,
                input=prompt,
                reasoning={"effort": (settings.conversation_reasoning_effort or settings.default_reasoning_effort or "low")}
            )
            text = self._extract_responses_text(response)
            return text or "To better understand the situation, please briefly describe the background and current status of this issue."
            
        except Exception as e:
            return f"AI question generation failed: {str(e)}"
    
    async def _generate_follow_up_question(self, conversation: Dict[str, Any]) -> str:
        """Generate follow-up question"""
        try:
            # Build conversation history
            messages = conversation.get("messages", [])
            
            # Get the previous question (last assistant message)
            previous_question = ""
            customer_response = ""
            
            # Find the last AI question and user response
            for i in range(len(messages) - 1, -1, -1):
                if messages[i]["role"] == "user" and not customer_response:
                    customer_response = messages[i]["content"]
                elif messages[i]["role"] == "assistant" and not previous_question:
                    previous_question = messages[i]["content"]
                
                if previous_question and customer_response:
                    break
            
            # Get category from original question
            original_question = conversation.get("original_question", "")
            category = original_question.split(":")[0] if ":" in original_question else "General"
            
            prompt = Prompts.FOLLOW_UP_QUESTION_GENERATION.format(
                previous_question=previous_question or original_question,
                customer_response=customer_response or "No response yet",
                category=category
            )
            
            response = self.openai_client.responses.create(
                model=settings.conversation_model,
                instructions=Prompts.CUSTOMER_MANAGER,
                input=prompt,
                reasoning={"effort": (settings.conversation_reasoning_effort or settings.default_reasoning_effort or "low")}
            )
            text = self._extract_responses_text(response)
            return text or "Can you specifically explain the key points in the previous answer? For example, which departments, time periods, or goals are involved?"
            
        except Exception as e:
            return f"AI question generation failed: {str(e)}"

    async def _get_historical_context(self, db: Session, account_id: int) -> str:
        """Get historical context"""
        try:
            # Get recent interaction records
            recent_interactions = db.query(Interaction).filter(
                Interaction.account_id == account_id
            ).order_by(Interaction.created_at.desc()).limit(5).all()
            
            if not recent_interactions:
                return "No historical conversation records available"
            
            context_parts = []
            for interaction in recent_interactions:
                if interaction.question and interaction.answer:
                    context_parts.append(f"Q: {interaction.question}\nA: {interaction.answer}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            return f"Get historical context failed: {str(e)}"
    
    def _build_conversation_context(self, 
                                  question: str, 
                                  historical_context: str, 
                                  context: Dict[str, Any] = None) -> str:
        """Build conversation context"""
        context_parts = [
            f"Current question: {question}",
            f"Historical conversation: {historical_context}"
        ]
        
        if context:
            context_parts.append(f"Additional context: {json.dumps(context, ensure_ascii=False)}")
        
        return "\n\n".join(context_parts)
    
    async def _generate_ai_response(self, 
                                  user_message: str, 
                                  conversation: Dict[str, Any], 
                                  is_initial: bool = False) -> str:
        """Generate AI response"""
        try:
            # Build system prompt
            if is_initial:
                question = conversation.get('question', 'Unknown question')
                system_prompt = f"""
                You are a professional customer manager collecting customer information. Please ask in-depth questions based on the following question to get detailed information:
                
                Question: {question}
                
                Please:
                1. Confirm understanding of the question
                2. Ask 2-3 specific follow-up questions
                3. Guide the user to provide detailed information
                4. Maintain a professional and friendly tone
                
                Please respond in English.
                """
            else:
                system_prompt = """
                You are a professional customer manager collecting customer information. Please:
                1. Show understanding and appreciation for the user's response
                2. Ask 1-2 in-depth questions based on the response
                3. Guide the user to provide more details
                4. Keep the conversation natural and flowing
                
                Please respond in English.
                """
            
            # Build message history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (last 10 rounds)
            conversation_messages = conversation.get("messages", [])
            recent_messages = conversation_messages[-10:]  # Last 10 messages
            messages.extend(recent_messages)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # gpt-5: Use Responses API, concatenate conversation as input
            conversation_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            response = self.openai_client.responses.create(
                model=settings.conversation_model,
                instructions="You are a professional customer service/customer manager, keep concise and clear English responses.",
                input=conversation_text,
                reasoning={"effort": (settings.conversation_reasoning_effort or settings.default_reasoning_effort or "low")}
            )
            text = self._extract_responses_text(response)
            return text or "Thank you for the information. Based on this, what do you think is the biggest obstacle that needs to be resolved currently?"
            
        except Exception as e:
            return f"AI response generation failed: {str(e)}"
    
    async def _generate_conversation_summary(self, conversation: Dict[str, Any]) -> str:
        """Generate conversation summary (including historical summary)"""
        try:
            # Build conversation text
            conversation_messages = conversation.get("messages", [])
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_messages
            ])
            
            # Get historical summary
            previous_summary = conversation.get("previous_summary", "")
            
            # Build prompt including historical summary
            # Always use the template with proper parameters
            prompt = Prompts.CONVERSATION_SUMMARY.format(
                previous_summary=previous_summary or "No previous summary available",
                conversation_content=conversation_text
            )
            
            response = self.openai_client.responses.create(
                model=settings.conversation_model,
                instructions=Prompts.CONVERSATION_SUMMARY_EXPERT,
                input=prompt,
                reasoning={"effort": (settings.conversation_reasoning_effort or settings.default_reasoning_effort or "low")}
            )
            text = self._extract_responses_text(response)
            return text or "(No available summary)"
            
        except Exception as e:
            return f"Conversation summary generation failed: {str(e)}"
    
    async def _extract_structured_data(self, 
                                     conversation: Dict[str, Any], 
                                     summary: str) -> Dict[str, Any]:
        """Extract structured data"""
        try:
            conversation_messages = conversation.get("messages", [])
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_messages
            ])
            
            prompt = f"""
            Extract structured information from the following conversation:
            
            Conversation content:
            {conversation_text}
            
            Summary:
            {summary}
            
            Please extract the following information (if exists):
            1. Key people (name, position, contact information)
            2. Products/Services names
            3. Time information (dates, time ranges)
            4. Amount/budget information
            5. Project names
            6. Challenges/Issues description
            7. Plans/goals
            8. Other key information
            
            Please return the extracted information in JSON format.
            """
            
            response = self.openai_client.responses.create(
                model=settings.conversation_model,
                instructions="You are a professional information extraction expert, skilled at extracting structured data from conversations. Please output only JSON.",
                input=prompt,
                reasoning={"effort": (settings.conversation_reasoning_effort or settings.default_reasoning_effort or "low")}
            )
            result = self._extract_responses_text(response)
            try:
                structured_data = json.loads(result)
                return structured_data
            except:
                return {
                    "raw_conversation": conversation_text,
                    "summary": summary,
                    "extraction_error": "Unable to parse structured data"
                }
                
        except Exception as e:
            return {
                "raw_conversation": conversation_text,
                "summary": summary,
                "extraction_error": str(e)
            }
    
    async def _save_conversation_to_db(self, 
                                     db: Session, 
                                     conversation: Dict[str, Any], 
                                     summary: str, 
                                     structured_data: Dict[str, Any]) -> Interaction:
        """Save conversation to database"""
        try:
            # Get original question
            original_question = conversation.get("original_question", "Unknown question")
            
            # Build complete answer (including conversation and summary)
            conversation_messages = conversation.get("messages", [])
            full_answer = f"Conversation summary:\n{summary}\n\nComplete conversation records:\n" + "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_messages
            ])
            
            # Create interaction record
            interaction = Interaction(
                account_id=conversation.get("account_id"),
                interaction_type="conversation",
                question=original_question,
                answer=full_answer,
                structured_data={
                    **structured_data,
                    "conversation_id": conversation.get("conversation_id"),
                    "message_count": len(conversation_messages),
                    "summary": summary
                }
            )

            db.add(interaction)
            db.commit()
            db.refresh(interaction)

            return interaction
        except Exception as e:
            raise Exception(f"Save conversation failed: {str(e)}")

    def _extract_responses_text(self, response: Any) -> str:
        """Compatible with various Responses API return structures, extract pure text."""
        # 1) Convenient field provided by SDK
        text = getattr(response, "output_text", None)
        if text:
            return text
        # 2) Deep traverse content/output 
        for attr in ("content", "output"):
            try:
                container = getattr(response, attr, None)
                if container:
                    parts: List[str] = []
                    def walk(node: Any):
                        if isinstance(node, dict):
                            if "text" in node and isinstance(node["text"], dict) and "value" in node["text"]:
                                parts.append(str(node["text"]["value"]))
                            for v in node.values():
                                walk(v)
                        elif isinstance(node, list):
                            for v in node:
                                walk(v)
                    walk(container)
                    if parts:
                        return "\n".join(parts)
            except Exception:
                pass
        # 3) Compatible with chat.completions structure (error tolerant)
        try:
            return response.choices[0].message.content
        except Exception:
            return ""
    
    async def get_conversation_history(self, 
                                     db: Session, 
                                     account_id: int) -> List[Dict[str, Any]]:
        """Get conversation history"""
        try:
            conversations = db.query(Interaction).filter(
                Interaction.account_id == account_id,
                Interaction.interaction_type == "conversation"
            ).order_by(Interaction.created_at.desc()).all()
            
            result = []
            for conv in conversations:
                result.append({
                    "id": conv.id,
                    "question": conv.question,
                    "summary": conv.structured_data.get("summary", ""),
                    "message_count": conv.structured_data.get("message_count", 0),
                    "created_at": conv.created_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            return []
