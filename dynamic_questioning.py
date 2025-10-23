"""
Dynamic questioning module
Responsible for generating intelligent questions based on context and historical information
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from models import QuestionTemplate, Interaction, Account
from question_manager import QuestionManager
from history_manager import HistoryManager
import json
import openai
from config import settings
from prompts import Prompts
from datetime import datetime

class DynamicQuestioning:
    """Dynamic questioning system"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        self.question_manager = QuestionManager()
        self.history_manager = HistoryManager()
    
    async def generate_contextual_questions(self, 
                                          db: Session, 
                                          account_id: int, 
                                          current_question: str = None,
                                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate context-related questions"""
        try:
            # Get account historical information
            history = await self.history_manager.get_account_history(db, account_id)
            
            if "error" in history:
                return {"error": "Unable to get account historical information"}
            
            # Get answered questions
            answered_questions = self._get_answered_questions(history.get("interactions", []))
            
            # Get core question templates
            core_questions = await self.question_manager.get_core_questions(db)
            
            # Analyze missing information
            missing_info = await self._analyze_missing_information(
                answered_questions, core_questions, context
            )
            
            # Generate intelligent questions
            intelligent_questions = await self._generate_intelligent_questions(
                missing_info, history, context
            )
            
            # Generate derived questions
            follow_up_questions = []
            if current_question:
                follow_up_questions = await self._generate_follow_up_questions(
                    current_question, context
                )
            
            return {
                "core_questions": core_questions,
                "answered_questions": answered_questions,
                "missing_info": missing_info,
                "intelligent_questions": intelligent_questions,
                "follow_up_questions": follow_up_questions,
                "suggested_next_questions": self._prioritize_questions(
                    intelligent_questions, follow_up_questions
                )
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_answered_questions(self, interactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get answered questions"""
        answered = []
        for interaction in interactions:
            if interaction["interaction_type"] == "question" and interaction["question"]:
                answered.append({
                    "question": interaction["question"],
                    "answer": interaction["answer"],
                    "structured_data": interaction["structured_data"],
                    "created_at": interaction["created_at"]
                })
        return answered
    
    async def _analyze_missing_information(self, 
                                         answered_questions: List[Dict[str, Any]], 
                                         core_questions: List[Dict[str, Any]], 
                                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze missing information"""
        try:
            # Build summary of answered questions
            answered_summary = "\n".join([
                f"Question: {q['question']}\nAnswer: {q['answer']}\n"
                for q in answered_questions
            ])
            
            # Build core question list
            core_questions_text = "\n".join([
                f"- {q['question_text']} ({q['category']})"
                for q in core_questions
            ])
            
            prompt = f"""
            Based on the following information, analyze missing important information:
            
            Answered questions:
            {answered_summary}
            
            Core question list:
            {core_questions_text}
            
            Context information:
            {context or "None"}
            
            Please analyze and return:
            1. Unanswered core questions
            2. Incomplete answers
            3. Information areas that need deeper exploration
            4. New discovery points based on answered information
            
            Return results in JSON format.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.dynamic_questioning_model,
                messages=[
                    {"role": "system", "content": Prompts.CRM_EXPERT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            try:
                missing_info = json.loads(result)
                return missing_info
            except:
                return {"unanswered_core": [], "incomplete_answers": [], "new_areas": []}
                
        except Exception as e:
            print(f"Analyze missing information failed: {e}")
            return {"unanswered_core": [], "incomplete_answers": [], "new_areas": []}
    
    async def _generate_intelligent_questions(self, 
                                            missing_info: Dict[str, Any], 
                                            history: Dict[str, Any], 
                                            context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate intelligent questions"""
        try:
            # Build historical information summary
            history_summary = self._build_history_summary(history)
            
            prompt = f"""
            Based on the following information, generate 3-5 intelligent questions to get missing important information:
            
            Missing information analysis:
            {json.dumps(missing_info, ensure_ascii=False, indent=2)}
            
            Historical information summary:
            {history_summary}
            
            Context information:
            {context or "None"}
            
            Please generate specific, targeted questions to help:
            1. Fill information gaps
            2. Deeply understand customer requirements
            3. Discover new cooperation opportunities
            4. Identify potential risks
            
            Each question should include:
            - Question text
            - Question type/category
            - Expected information value
            - Suggested follow-up direction
            
            Return results in JSON format.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.dynamic_questioning_model,
                messages=[
                    {"role": "system", "content": Prompts.CUSTOMER_MANAGER},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            try:
                questions = json.loads(result)
                return questions if isinstance(questions, list) else []
            except:
                return []
                
        except Exception as e:
            print(f"Generate intelligent questions failed: {e}")
            return []
    
    async def _generate_follow_up_questions(self, 
                                          current_question: str, 
                                          context: Dict[str, Any] = None) -> List[str]:
        """Generate derived questions"""
        try:
            prompt = f"""
            Based on the current question, generate 3-5 related derived questions:
            
            Current question: {current_question}
            
            Context information:
            {context or "None"}
            
            Please generate specific, targeted derived questions to help:
            1. Deepen understanding of current topic
            2. Get more detailed information
            3. Explore related areas
            4. Confirm important information
            
            Return question list in JSON array format.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.dynamic_questioning_model,
                messages=[
                    {"role": "system", "content": Prompts.CUSTOMER_MANAGER},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            try:
                questions = json.loads(result)
                return questions if isinstance(questions, list) else []
            except:
                return []
                
        except Exception as e:
            print(f"Generate derived questions failed: {e}")
            return []
    
    def _build_history_summary(self, history: Dict[str, Any]) -> str:
        """Build historical information summary"""
        interactions = history.get("interactions", [])
        external_info = history.get("external_info", {})
        
        summary_parts = []
        
        # Interaction history summary
        if interactions:
            summary_parts.append("Interaction History:")
            for interaction in interactions[:5]:  # Only take the latest 5
                if interaction["question"] and interaction["answer"]:
                    summary_parts.append(f"- {interaction['question']}: {interaction['answer'][:100]}...")
        
        # External InformationAbstract
        if external_info:
            summary_parts.append("\nExternal Information：")
            for info_type, info_data in external_info.items():
                summary_parts.append(f"- {info_type}: {str(info_data)[:100]}...")
        
        return "\n".join(summary_parts) if summary_parts else "No historical information available"
    
    def _prioritize_questions(self, 
                            intelligent_questions: List[Dict[str, Any]], 
                            follow_up_questions: List[str]) -> List[Dict[str, Any]]:
        """Question priority sorting"""
        prioritized = []
        
        # Add intelligent questions
        for q in intelligent_questions:
            if isinstance(q, dict):
                prioritized.append({
                    "question": q.get("question", ""),
                    "type": "intelligent",
                    "category": q.get("category", "Other"),
                    "priority": q.get("priority", "medium"),
                    "value": q.get("value", "Medium")
                })
        
        # Add derived questions
        for q in follow_up_questions:
            prioritized.append({
                "question": q,
                "type": "follow_up",
                "category": "Derived",
                "priority": "medium",
                "value": "Medium"
            })
        
        # Sort by priority
        priority_order = {"high": 1, "medium": 2, "low": 3}
        prioritized.sort(key=lambda x: priority_order.get(x["priority"], 2))
        
        return prioritized[:10]  # Return top 10 questions
    
    async def adapt_questions_to_context(self, 
                                       db: Session, 
                                       account_id: int, 
                                       industry: str = None,
                                       company_size: str = None,
                                       current_focus: str = None) -> List[Dict[str, Any]]:
        """Adjust questions based on context"""
        try:
            # GetBasicQuestion Templates
            core_questions = await self.question_manager.get_core_questions(db)
            
            # Adjust questions based on context
            adapted_questions = []
            
            for question in core_questions:
                adapted_question = await self._adapt_single_question(
                    question, industry, company_size, current_focus
                )
                adapted_questions.append(adapted_question)
            
            return adapted_questions
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _adapt_single_question(self, 
                                   question: Dict[str, Any], 
                                   industry: str = None,
                                   company_size: str = None, 
                                   current_focus: str = None) -> Dict[str, Any]:
        """Adjust single question"""
        try:
            context_info = {
                "industry": industry or "Unknown",
                "company_size": company_size or "Unknown",
                "current_focus": current_focus or "None"
            }
            
            prompt = f"""
            Based on the following context information, adjust the question to make it more specific and relevant:
            
            Original question: {question['question_text']}
            Question category: {question['category']}
            
            Context information:
            - Industry: {context_info['industry']}
            - Company Size: {context_info['company_size']}
            - Current Focus: {context_info['current_focus']}
            
            Please return the adjusted question to better fit the current context.
            If no adjustment is needed, return the original question.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.dynamic_questioning_model,
                messages=[
                    {"role": "system", "content": Prompts.CUSTOMER_MANAGER},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=1000
            )
            
            adapted_text = (response.choices[0].message.content or "").strip()
            
            return {
                "id": question["id"],
                "category": question["category"],
                "original_question": question["question_text"],
                "adapted_question": adapted_text,
                "is_adapted": adapted_text != question["question_text"],
                "context": context_info
            }
            
        except Exception as e:
            return {
                "id": question["id"],
                "category": question["category"],
                "original_question": question["question_text"],
                "adapted_question": question["question_text"],
                "is_adapted": False,
                "error": str(e)
            }

    
    async def generate_question_flow(self, 
                                   db: Session, 
                                   account_id: int, 
                                   flow_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate questions process"""
        try:
            # Get account information
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                return {"error": "Account does not exist"}
            
            # Generate different question flows based on process type
            if flow_type == "comprehensive":
                flow = await self._generate_comprehensive_flow(account)
            elif flow_type == "quick":
                flow = await self._generate_quick_flow(account)
            elif flow_type == "focused":
                flow = await self._generate_focused_flow(account)
            else:
                flow = await self._generate_comprehensive_flow(account)
            
            return flow
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _generate_comprehensive_flow(self, account: Account) -> Dict[str, Any]:
        """Generate comprehensive question flow"""
        return {
            "flow_type": "comprehensive",
            "description": "Comprehensive customer information collection process",
            "phases": [
                {
                    "phase": 1,
                    "name": "BasicInformation Collection",
                    "description": "Collect basic company information and cooperation history",
                    "questions": [
                        "What cooperation projects have you had with this company in the past?",
                        "What products or services have you sold?",
                        "Who are the key contacts?"
                    ]
                },
                {
                    "phase": 2,
                    "name": "Issue Identification",
                    "description": "Identify challenges and issues in cooperation",
                    "questions": [
                        "What challenges or issues have you encountered in cooperation?",
                        "How were these issues resolved?",
                        "Are there any unresolved issues?"
                    ]
                },
                {
                    "phase": 3,
                    "name": "Future Planning",
                    "description": "Understand future cooperation plans",
                    "questions": [
                        "What are the next cooperation plans?",
                        "Are there any missing support or resources currently?",
                        "What are the expected cooperation outcomes?"
                    ]
                }
            ],
            "estimated_time": "30-45 minutes",
            "completion_criteria": "Complete all phase questions"
        }
    
    async def _generate_quick_flow(self, account: Account) -> Dict[str, Any]:
        """Generate quick question flow"""
        return {
            "flow_type": "quick",
            "description": "Quick customer information collection process",
            "phases": [
                {
                    "phase": 1,
                    "name": "Core Information",
                    "description": "Collect the most core customer information",
                    "questions": [
                        "What cooperation projects have you had with this company in the past?",
                        "What are the next cooperation plans?",
                        "Are there any missing support or resources currently?"
                    ]
                }
            ],
            "estimated_time": "10-15 minutes",
            "completion_criteria": "Complete core questions"
        }
    
    async def _generate_focused_flow(self, account: Account) -> Dict[str, Any]:
        """Generate focused question flow"""
        return {
            "flow_type": "focused",
            "description": "Focused question flow for specific areas",
            "phases": [
                {
                    "phase": 1,
                    "name": "Issue Focus",
                    "description": "Deep dive into specific issue areas",
                    "questions": [
                        "What challenges or issues have you encountered in cooperation?",
                        "What impact do these issues have on the cooperative relationship?",
                        "How to prevent similar issues?"
                    ]
                }
            ],
            "estimated_time": "20-30 minutes",
            "completion_criteria": "Deep analysis of specific issues"
        }
    
    async def update_question_templates(self, 
                                      db: Session, 
                                      template_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """UpdateQuestion Templates"""
        try:
            updated_count = 0
            
            for update in template_updates:
                template_id = update.get("id")
                if not template_id:
                    continue
                
                template = db.query(QuestionTemplate).filter(
                    QuestionTemplate.id == template_id
                ).first()
                
                if template:
                    # Update template fields
                    if "question_text" in update:
                        template.question_text = update["question_text"]
                    if "category" in update:
                        template.category = update["category"]
                    if "follow_up_questions" in update:
                        template.follow_up_questions = update["follow_up_questions"]
                    if "order" in update:
                        template.order = update["order"]
                    if "is_active" in update:
                        template.is_active = update["is_active"]
                    
                    updated_count += 1
            
            db.commit()
            
            return {
                "message": f"Successfully updated {updated_count} Question Templates",
                "updated_count": updated_count
            }
            
        except Exception as e:
            return {"error": str(e)}
