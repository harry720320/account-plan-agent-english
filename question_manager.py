"""
Question management module
Responsible for managing question templates and dynamic questioning
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models import QuestionTemplate, Interaction, Account
import json
import openai
from config import settings
from prompts import Prompts

class QuestionManager:
    """Question manager"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        self.core_questions = self._get_default_core_questions()
    
    def _get_default_core_questions(self) -> List[Dict[str, Any]]:
        """Get default core questions"""
        return [
            {
                "category": "Cooperation History",
                "question_text": "What cooperation projects have you had with this company in the past?",
                "is_core": True,
                "follow_up_questions": [
                    "What is the specific time range of the cooperation projects?",
                    "What is the scale and value of the projects?",
                    "ProjectIsNoSuccessComplete？"
                ],
                "order": 1
            },
            {
                "category": "Products & Services",
                "question_text": "What products or services have you sold?",
                "is_core": True,
                "follow_up_questions": [
                    "How is the sales performance of these products?",
                    "What is the customer feedback on the products?",
                    "Are there any repeat purchases?"
                ],
                "order": 2
            },
            {
                "category": "Challenges & Issues",
                "question_text": "What challenges or issues have you encountered in cooperation?",
                "is_core": True,
                "follow_up_questions": [
                    "How are these issues resolved?",
                    "Are there any unresolved issues?",
                    "What impact do these issues have on the cooperation relationship?"
                ],
                "order": 3
            },
            {
                "category": "Key Contacts",
                "question_text": "Who are the key contacts?",
                "is_core": True,
                "follow_up_questions": [
                    "What are the positions and influence of these contacts?",
                    "What is the relationship with them?",
                    "Who is the most important decision maker?"
                ],
                "order": 4
            },
            {
                "category": "Future Plans",
                "question_text": "What are the next cooperation plans?",
                "is_core": True,
                "follow_up_questions": [
                    "What is the timeline of the plan?",
                    "What is the expected cooperation scale?",
                    "What resource support is needed?"
                ],
                "order": 5
            },
            {
                "category": "Resource Needs",
                "question_text": "Are there any missing support or resources currently?",
                "is_core": True,
                "follow_up_questions": [
                    "How important are these resources to cooperation?",
                    "How to obtain these resources?",
                    "Are there any alternatives?"
                ],
                "order": 6
            }
        ]
    
    async def initialize_questions(self, db: Session):
        """Initialize question templates to database"""
        for question_data in self.core_questions:
            existing = db.query(QuestionTemplate).filter(
                QuestionTemplate.question_text == question_data["question_text"]
            ).first()
            
            if not existing:
                question = QuestionTemplate(
                    category=question_data["category"],
                    question_text=question_data["question_text"],
                    is_core=question_data["is_core"],
                    follow_up_questions=question_data["follow_up_questions"],
                    order=question_data["order"]
                )
                db.add(question)
        
        db.commit()
    
    async def get_core_questions(self, db: Session) -> List[Dict[str, Any]]:
        """Get core question list"""
        questions = db.query(QuestionTemplate).filter(
            QuestionTemplate.is_core == True,
            QuestionTemplate.is_active == True
        ).order_by(QuestionTemplate.order).all()
        
        return [
            {
                "id": q.id,
                "category": q.category,
                "question_text": q.question_text,
                "follow_up_questions": q.follow_up_questions or [],
                "order": q.order
            }
            for q in questions
        ]
    
    async def generate_follow_up_questions(self, 
                                         question: str, 
                                         answer: str, 
                                         context: Dict[str, Any] = None) -> List[str]:
        """Generate derived questions based on answers"""
        try:
            prompt = f"""
            Based on the following question and answer, generate 3-5 related derived questions to get deeper information:
            
            Original question: {question}
            Answer: {answer}
            
            Context information: {context or "None"}
            
            Please generate specific, targeted questions to help better understand the customer situation.
            Return question list in JSON array format.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.question_model,
                messages=[
                    {"role": "system", "content": Prompts.CUSTOMER_MANAGER},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            try:
                follow_up_questions = json.loads(result)
                return follow_up_questions if isinstance(follow_up_questions, list) else []
            except:
                return []
                
        except Exception as e:
            print(f"Generate derived questions failed: {e}")
            return []
    
    async def extract_structured_data(self, 
                                    question: str, 
                                    answer: str, 
                                    category: str) -> Dict[str, Any]:
        """Extract structured data from answers"""
        try:
            prompt = f"""
            Extract structured information from the following Q&A:
            
            Question category: {category}
            Question: {question}
            Answer: {answer}
            
            Please extract the following information (if exists):
            1. Key people (name, position, contact information)
            2. Products/Services names
            3. Time information (dates, time ranges)
            4. Amount/budget information
            5. Project names
            6. Challenges/Issues description
            7. Plans/goals
            8. Other key information
            
            Please return extracted information in JSON format.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.question_model,
                messages=[
                    {"role": "system", "content": Prompts.DATA_EXTRACTION_EXPERT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=2000
            )
            
            result = self._extract_responses_text(response)
            try:
                structured_data = json.loads(result)
                return structured_data
            except:
                return {"raw_answer": answer, "extraction_error": "Unable to parse structured data"}
                
        except Exception as e:
            return {"raw_answer": answer, "extraction_error": str(e)}
    
    async def get_historical_context(self, 
                                   db: Session, 
                                   account_id: int, 
                                   current_question: str) -> Dict[str, Any]:
        """Get historical context information"""
        # Get historical interaction records for this account
        interactions = db.query(Interaction).filter(
            Interaction.account_id == account_id
        ).order_by(Interaction.created_at.desc()).limit(10).all()
        
        if not interactions:
            return {"has_history": False, "context": ""}
        
        # Build historical context
        context_parts = []
        for interaction in interactions:
            if interaction.question and interaction.answer:
                context_parts.append(f"Q: {interaction.question}\nA: {interaction.answer}")
        
        context = "\n\n".join(context_parts)
        
        # Use AI to analyze relevance of historical information
        try:
            prompt = f"""
            Based on the following historical Q&A records, analyze which information is related to the current question:
            
            Current question: {current_question}
            
            Historical records:
            {context}
            
            Please return:
            1. Related historical information summary
            2. Information that needs confirmation or updating
            3. Suggested follow-up directions
            
            Return in JSON format.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.question_model,
                messages=[
                    {"role": "system", "content": Prompts.CRM_EXPERT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=2000
            )
            
            result = self._extract_responses_text(response)
            try:
                analysis = json.loads(result)
            except:
                analysis = {"relevant_info": context[:500], "suggestions": []}
            
            return {
                "has_history": True,
                "context": context,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "has_history": True,
                "context": context,
                "analysis": {"error": str(e)}
            }

    
    async def save_interaction(self, 
                             db: Session, 
                             account_id: int, 
                             plan_id: Optional[int],
                             question: str, 
                             answer: str, 
                             structured_data: Dict[str, Any] = None):
        """Save interaction record"""
        interaction = Interaction(
            account_id=account_id,
            plan_id=plan_id,
            interaction_type="question",
            question=question,
            answer=answer,
            structured_data=structured_data or {}
        )
        
        db.add(interaction)
        db.commit()
        
        return interaction
    
    async def get_question_progress(self, db: Session, account_id: int) -> Dict[str, Any]:
        """Get question progress"""
        try:
            # Get all answered questions (including question and conversation types)
            all_interactions = db.query(Interaction).filter(
                Interaction.account_id == account_id,
                Interaction.interaction_type.in_(["question", "conversation"]),
                Interaction.question.isnot(None),
                Interaction.answer.isnot(None)
            ).all()
            
            # Get all core questions
            all_core_questions = await self.get_core_questions(db)
            
            # DebugInfo
            print(f"Account {account_id} interaction record count: {len(all_interactions)}")
            print(f"Core question count: {len(all_core_questions)}")
            
            answered_question_ids = set()
            answered_questions_debug = []
            
            for interaction in all_interactions:
                question_text = interaction.question
                if not question_text:
                    continue
                    
                # Try multiple matching methods to find corresponding question
                matched_question = None
                
                # Method 1: Exact match
                for q in all_core_questions:
                    if q["question_text"] == question_text:
                        matched_question = q
                        break
                
                # Method 2: Include match (handle possible formatting differences)
                if not matched_question:
                    for q in all_core_questions:
                        if question_text.strip() in q["question_text"] or q["question_text"] in question_text.strip():
                            matched_question = q
                            break
                
                # Method 3: Keyword matching (more flexible matching)
                if not matched_question:
                    question_keywords = set(question_text.replace('？', '').replace('?', '').split())
                    for q in all_core_questions:
                        q_keywords = set(q["question_text"].replace('？', '').replace('?', '').split())
                        # If more than 60% keyword overlap, consider it the same question
                        if question_keywords and q_keywords:
                            overlap = len(question_keywords & q_keywords)
                            total = len(question_keywords | q_keywords)
                            if total > 0 and overlap / total >= 0.6:
                                matched_question = q
                                break
                
                if matched_question:
                    answered_question_ids.add(matched_question["id"])
                    answered_questions_debug.append({
                        "question_id": matched_question["id"],
                        "question_text": question_text,
                        "interaction_type": interaction.interaction_type,
                        "created_at": interaction.created_at.isoformat() if interaction.created_at else None
                    })
                else:
                    print(f"Question not matched: {question_text[:50]}...")
            
            total_questions = len(all_core_questions)
            answered_count = len(answered_question_ids)
            completion_rate = 0
            
            if total_questions > 0:
                completion_rate = answered_count / total_questions * 100
            
            # DebugInfo
            print(f"Answered question IDs: {answered_question_ids}")
            print(f"Completion rate: {completion_rate:.1f}%")
            
            progress = {
                "total_questions": total_questions,
                "answered_questions": answered_count,
                "completion_rate": completion_rate,
                "remaining_questions": [
                    q for q in all_core_questions 
                    if q["id"] not in answered_question_ids
                ],
                "answered_questions_detail": answered_questions_debug,  # DebugInfo
                "debug_info": {
                    "total_interactions": len(all_interactions),
                    "matched_questions": answered_count,
                    "unmatched_interactions": len(all_interactions) - answered_count
                }
            }
            
            return progress
            
        except Exception as e:
            print(f"Get question progress failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "total_questions": 0,
                "answered_questions": 0,
                "completion_rate": 0,
                "remaining_questions": [],
                "error": str(e)
            }
