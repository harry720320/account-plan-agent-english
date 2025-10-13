"""
Historical information management module
Responsible for storing, retrieving and reusing historical information
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from models import Account, AccountPlan, Interaction, ExternalInfo
from datetime import datetime, timedelta
import json
import openai
from config import settings
from prompts import Prompts

class HistoryManager:
    """Historical information manager"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def save_external_info(self, 
                               db: Session, 
                               account_id: int, 
                               info_type: str, 
                               content: Dict[str, Any], 
                               source_url: str = None) -> int:
        """Save external information (update if exists, avoid unique constraint conflicts)"""
        try:
            existing = db.query(ExternalInfo).filter(
                ExternalInfo.account_id == account_id,
                ExternalInfo.info_type == info_type
            ).first()
            if existing:
                existing.content = json.dumps(content, ensure_ascii=False)
                if source_url is not None:
                    existing.source_url = source_url
                existing.updated_at = datetime.utcnow()
                db.commit()
                return existing.id
            else:
                external_info = ExternalInfo(
                    account_id=account_id,
                    info_type=info_type,
                    content=json.dumps(content, ensure_ascii=False),
                    source_url=source_url
                )
                db.add(external_info)
                db.commit()
                return external_info.id
        
        except Exception as e:
            print(f"Save external information failed: {e}")
            return None

    async def upsert_external_info(self,
                                 db: Session,
                                 account_id: int,
                                 info_type: str,
                                 content: Dict[str, Any],
                                 source_url: str = None) -> int:
        """Explicit upsert method for update interface use"""
        return await self.save_external_info(db, account_id, info_type, content, source_url)
    
    async def get_external_info(self, db: Session, account_id: int) -> Dict[str, Any]:
        """Get external information"""
        try:
            external_records = db.query(ExternalInfo).filter(
                ExternalInfo.account_id == account_id
            ).all()
            
            external_info = {}
            for record in external_records:
                external_info[record.info_type] = {
                    "content": json.loads(record.content) if record.content else {},
                    "source_url": record.source_url,
                    "created_at": record.created_at.isoformat()
                }
            
            return external_info
            
        except Exception as e:
            print(f"GetExternal InformationFailure: {e}")
            return {}

    async def get_account_history(self, 
                                db: Session, 
                                account_id: int, 
                                include_external: bool = True) -> Dict[str, Any]:
        """Get account historical information"""
        try:
            # Get account basic information
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                return {"error": "Account does not exist"}
            
            # Get interaction history
            interactions = db.query(Interaction).filter(
                Interaction.account_id == account_id
            ).order_by(Interaction.created_at.desc()).all()
            
            # GetExternal Information
            external_info = {}
            if include_external:
                external_records = db.query(ExternalInfo).filter(
                    ExternalInfo.account_id == account_id
                ).all()
                
                for record in external_records:
                    external_info[record.info_type] = {
                        "content": json.loads(record.content) if record.content else {},
                        "source_url": record.source_url,
                        "created_at": record.created_at.isoformat()
                    }
            
            # Get plan history
            plans = db.query(AccountPlan).filter(
                AccountPlan.account_id == account_id
            ).order_by(AccountPlan.created_at.desc()).all()
            
            return {
                "account": {
                    "id": account.id,
                    "company_name": account.company_name,
                    "industry": account.industry,
                    "company_size": account.company_size,
                    "website": account.website,
                    "description": account.description,
                    "created_at": account.created_at.isoformat(),
                    "updated_at": account.updated_at.isoformat()
                },
                "interactions": [
                    {
                        "id": i.id,
                        "interaction_type": i.interaction_type,
                        "question": i.question,
                        "answer": i.answer,
                        "structured_data": i.structured_data,
                        "created_at": i.created_at.isoformat()
                    }
                    for i in interactions
                ],
                "external_info": external_info,
                "plans": [
                    {
                        "id": p.id,
                        "title": p.title,
                        "status": p.status,
                        "created_at": p.created_at.isoformat(),
                        "updated_at": p.updated_at.isoformat(),
                        "change_log": p.change_log
                    }
                    for p in plans
                ]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def get_relevant_history(self, 
                                 db: Session, 
                                 account_id: int, 
                                 current_question: str, 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get relevant historical information"""
        try:
            # Get historical interaction records
            interactions = db.query(Interaction).filter(
                Interaction.account_id == account_id,
                Interaction.interaction_type == "question"
            ).order_by(Interaction.created_at.desc()).limit(20).all()
            
            if not interactions:
                return {"has_history": False, "relevant_info": []}
            
            # Use AI to analyze relevance
            relevant_info = await self._analyze_relevance(
                current_question, interactions, context
            )
            
            return {
                "has_history": True,
                "relevant_info": relevant_info,
                "total_interactions": len(interactions)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _analyze_relevance(self, 
                               current_question: str, 
                               interactions: List[Interaction], 
                               context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Analyze relevance of historical information"""
        try:
            # Build historical information text
            history_text = "\n\n".join([
                f"Question: {i.question}\nAnswer: {i.answer}\nTime: {i.created_at.strftime('%Y-%m-%d')}"
                for i in interactions
            ])
            
            prompt = f"""
            Based on the following historical Q&A records, find information related to the current question:
            
            Current question: {current_question}
            
            Historical records:
            {history_text}
            
            Context information: {context or "None"}
            
            Please analyze and return:
            1. Directly related historical Q&A
            2. Information that may need updating
            3. Suggested follow-up directions
            
            Return results in JSON format.
            """
            
            response = self.openai_client.responses.create(
                model=settings.history_model,
                instructions=Prompts.CRM_EXPERT,
                input=prompt,
                reasoning={"effort": (settings.history_reasoning_effort or settings.default_reasoning_effort or "low")}
            )
            
            result = self._extract_responses_text(response)
            try:
                analysis = json.loads(result)
                return analysis.get("relevant_info", [])
            except:
                # If parsing fails, return basic relevance analysis
                return self._basic_relevance_analysis(current_question, interactions)
                
        except Exception as e:
            print(f"AI relevance analysis failed: {e}")
            return self._basic_relevance_analysis(current_question, interactions)
    
    def _basic_relevance_analysis(self, 
                                current_question: str, 
                                interactions: List[Interaction]) -> List[Dict[str, Any]]:
        """Basic relevance analysis (used when AI analysis fails)"""
        relevant_info = []
        current_lower = current_question.lower()
        
        # Simple keyword matching
        for interaction in interactions:
            question_lower = interaction.question.lower()
            answer_lower = interaction.answer.lower()
            
            # Check keyword overlap
            current_words = set(current_lower.split())
            question_words = set(question_lower.split())
            answer_words = set(answer_lower.split())
            
            overlap = len(current_words.intersection(question_words.union(answer_words)))
            
            if overlap > 0:
                relevant_info.append({
                    "interaction_id": interaction.id,
                    "question": interaction.question,
                    "answer": interaction.answer,
                    "relevance_score": overlap,
                    "created_at": interaction.created_at.isoformat(),
                    "structured_data": interaction.structured_data
                })
        
        # Sort by relevance
        relevant_info.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return relevant_info[:5]  # Return top 5 most relevant records
    
    async def prefill_questionnaire(self, 
                                  db: Session, 
                                  account_id: int) -> Dict[str, Any]:
        """Pre-fill questionnaire (based on historical information)"""
        try:
            # Get historical information
            history = await self.get_account_history(db, account_id, include_external=False)
            
            if "error" in history:
                return history
            
            interactions = history.get("interactions", [])
            
            # Organize historical answers by question type
            prefill_data = {}
            for interaction in interactions:
                if interaction["question"] and interaction["answer"]:
                    prefill_data[interaction["question"]] = {
                        "answer": interaction["answer"],
                        "structured_data": interaction["structured_data"],
                        "last_updated": interaction["created_at"]
                    }
            
            # Use AI to generate pre-fill suggestions
            suggestions = await self._generate_prefill_suggestions(prefill_data)
            
            return {
                "prefill_data": prefill_data,
                "suggestions": suggestions,
                "total_questions": len(prefill_data)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _generate_prefill_suggestions(self, prefill_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate pre-fill suggestions"""
        try:
            if not prefill_data:
                return {"message": "No historical information available for pre-filling"}
            
            # Build historical information summary
            history_summary = "\n".join([
                f"Question: {q}\nAnswer: {data['answer']}\nLast Updated: {data['last_updated']}\n"
                for q, data in prefill_data.items()
            ])
            
            prompt = f"""
            Based on the following historical Q&A records, generate pre-fill suggestions:
            
            {history_summary}
            
            Please analyze and return:
            1. Which information may be outdated and needs updating
            2. Which information is still valid and can be pre-filled
            3. Suggested update priority
            4. Missing important information
            
            Return results in JSON format.
            """
            
            response = self.openai_client.responses.create(
                model=settings.history_model,
                instructions=Prompts.HISTORY_ANALYSIS_EXPERT,
                input=prompt,
                reasoning={"effort": (settings.history_reasoning_effort or settings.default_reasoning_effort or "low")}
            )
            
            result = self._extract_responses_text(response)
            try:
                suggestions = json.loads(result)
                return suggestions
            except:
                return {"message": "Unable to generate pre-fill suggestions"}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def detect_changes(self, 
                           db: Session, 
                           account_id: int, 
                           new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect data changes"""
        try:
            # Get latest historical data
            history = await self.get_account_history(db, account_id, include_external=False)
            
            if "error" in history:
                return history
            
            interactions = history.get("interactions", [])
            
            # Build historical data summary
            historical_summary = {}
            for interaction in interactions:
                if interaction["structured_data"]:
                    historical_summary.update(interaction["structured_data"])
            
            # Use AI to detect changes
            changes = await self._analyze_changes(historical_summary, new_data)
            
            return {
                "has_changes": len(changes.get("changes", [])) > 0,
                "changes": changes.get("changes", []),
                "suggestions": changes.get("suggestions", [])
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _analyze_changes(self, 
                             historical_data: Dict[str, Any], 
                             new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data changes"""
        try:
            prompt = f"""
            Compare the following historical data and new data to detect changes:
            
            Historical data:
            {json.dumps(historical_data, ensure_ascii=False, indent=2)}
            
            NewData：
            {json.dumps(new_data, ensure_ascii=False, indent=2)}
            
            Please analyze and return:
            1. Specific change content
            2. Importance level of changes
            3. Suggested update strategy
            
            Return results in JSON format.
            """
            
            response = self.openai_client.responses.create(
                model=settings.history_model,
                instructions=Prompts.DATA_ANALYST,
                input=prompt,
                reasoning={"effort": (settings.history_reasoning_effort or settings.default_reasoning_effort or "low")}
            )
            
            result = self._extract_responses_text(response)
            try:
                changes = json.loads(result)
                return changes
            except:
                return {"changes": [], "suggestions": []}
                
        except Exception as e:
            return {"error": str(e)}

    def _extract_responses_text(self, response: Any) -> str:
        text = getattr(response, "output_text", None)
        if text:
            return text
        for attr in ("content", "output"):
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
        try:
            return response.choices[0].message.content
        except Exception:
            return ""
            try:
                changes = json.loads(result)
                return changes
            except:
                return {"changes": [], "suggestions": []}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def generate_change_log(self, 
                                db: Session, 
                                plan_id: int, 
                                changes: Dict[str, Any]) -> str:
        """Generate change log"""
        try:
            plan = db.query(AccountPlan).filter(AccountPlan.id == plan_id).first()
            if not plan:
                return "Plan does not exist"
            
            # Get existing change log
            change_log = plan.change_log or {}
            
            # Add new changes
            timestamp = datetime.now().isoformat()
            change_log[timestamp] = {
                "changes": changes,
                "timestamp": timestamp,
                "description": f"Updated {len(changes)} items"
            }
            
            # Update plan
            plan.change_log = change_log
            plan.updated_at = datetime.utcnow()
            db.commit()
            
            return f"Change log updated, recorded {len(change_log)} changes"
            
        except Exception as e:
            return f"Update change log failed: {str(e)}"
    
    async def get_plan_history(self, 
                             db: Session, 
                             plan_id: int) -> Dict[str, Any]:
        """Get plan history"""
        try:
            plan = db.query(AccountPlan).filter(AccountPlan.id == plan_id).first()
            if not plan:
                return {"error": "Plan does not exist"}
            
            return {
                "plan_id": plan.id,
                "title": plan.title,
                "status": plan.status,
                "created_at": plan.created_at.isoformat(),
                "updated_at": plan.updated_at.isoformat(),
                "change_log": plan.change_log or {},
                "content_preview": plan.content[:500] + "..." if len(plan.content) > 500 else plan.content
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def archive_old_plans(self, 
                              db: Session, 
                              account_id: int, 
                              keep_latest: int = 3) -> Dict[str, Any]:
        """Archive old plans"""
        try:
            # Get all plans for this account
            plans = db.query(AccountPlan).filter(
                AccountPlan.account_id == account_id,
                AccountPlan.status != "archived"
            ).order_by(AccountPlan.created_at.desc()).all()
            
            if len(plans) <= keep_latest:
                return {"message": "No archiving needed, plan count does not exceed limit"}
            
            # Archive old plans
            plans_to_archive = plans[keep_latest:]
            archived_count = 0
            
            for plan in plans_to_archive:
                plan.status = "archived"
                archived_count += 1
            
            db.commit()
            
            return {
                "message": f"Successfully archived {archived_count} old plans",
                "archived_plans": [p.id for p in plans_to_archive]
            }
            
        except Exception as e:
            return {"error": str(e)}
