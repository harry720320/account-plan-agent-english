"""
Strategic plan generation module
Responsible for generating structured customer plan documents
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from models import Account, AccountPlan, Interaction, ExternalInfo
from datetime import datetime
import json
import openai
from config import settings
from prompts import Prompts
from jinja2 import Template

class PlanGenerator:
    """Strategic plan generator"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        self.template = self._get_plan_template()
    
    def _get_plan_template(self) -> str:
        """Get plan template"""
        return """# Strategic Customer Plan - {{ company_name }}

## 1. Company Overview

**Company Name：** {{ company_name }}  
**Industry：** {{ industry }}  
**Company Size：** {{ company_size }}  
**Official Website：** {{ website }}  

### Company Description
{{ company_description }}

---

## 2. Latest News and Market Dynamics

### News Summary
{{ news_summary }}

### Market Trend Analysis
{{ market_analysis }}

---

## 3. Past Cooperation Summary

### Cooperation Projects
{{ cooperation_projects }}

### Products & Services
{{ products_services }}

### Key Contacts
{{ key_contacts }}

---

## 4. Current Challenges and Issues

### Identified Issues
{{ current_challenges }}

### Issue Impact Analysis
{{ challenge_impact }}

---

## 5. Next Steps

### Short-term Plans (3-6 months)
{{ short_term_plans }}

### Long-term Plans (6-12 months)
{{ long_term_plans }}

### Expected Results
{{ expected_outcomes }}

---

## 6. Gap Analysis

### Resource Gaps
{{ resource_gaps }}

### Capability Gaps
{{ capability_gaps }}

### Opportunity Gaps
{{ opportunity_gaps }}

---

## 7. Action Items

### Immediate Actions
{{ immediate_actions }}

### Medium-term Actions
{{ medium_term_actions }}

### Long-term Actions
{{ long_term_actions }}

### Responsibility Assignment
{{ responsibility_assignment }}

---

## 8. Risk Assessment and Response

### Main Risks
{{ main_risks }}

### Risk Response Strategies
{{ risk_mitigation }}

---

## 9. Success Metrics (KPIs)

### Key Metrics
{{ key_metrics }}

### Monitoring Frequency
{{ monitoring_frequency }}

---

**Plan Generation Time:** {{ generated_at }}  
**Plan Version:** {{ version }}  
**UpdateRecord：** {{ change_log }}

---

*This plan is generated based on AI analysis, it is recommended to adjust and improve based on actual situation.*
"""
    
    async def generate_plan(self, 
                          db: Session, 
                          account_id: int, 
                          plan_title: str = None,
                          plan_description: str = None) -> Dict[str, Any]:
        """Generate complete strategic customer plan"""
        try:
            # Get account information
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                raise ValueError(f"Account ID {account_id} does not exist")
            
            # GetExternal Information
            external_info = await self._get_external_info(db, account_id)
            
            # Get internal information (Q&A records)
            internal_info = await self._get_internal_info(db, account_id)
            
            # GetCustomer Profile
            customer_profile = await self._get_customer_profile(db, account_id)
            
            # Use AI to generate plan content
            plan_content = await self._generate_plan_content(
                account, external_info, internal_info, customer_profile, plan_description
            )
            
            # Create plan record
            plan = AccountPlan(
                account_id=account_id,
                title=plan_title or f"{account.company_name} Strategic Customer Plan",
                content=plan_content,
                status="draft",
                change_log={"created": datetime.now().isoformat()}
            )
            
            db.add(plan)
            db.commit()
            
            return {
                "plan_id": plan.id,
                "title": plan.title,
                "content": plan_content,
                "status": plan.status,
                "generated_at": plan.created_at.isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_external_info(self, db: Session, account_id: int) -> Dict[str, Any]:
        """GetExternal Information"""
        external_records = db.query(ExternalInfo).filter(
            ExternalInfo.account_id == account_id
        ).all()
        
        external_info = {
            "company_profile": {},
            "news_snapshot": {},
            "market_info": {}
        }
        
        for record in external_records:
            try:
                if record.info_type == "company_profile":
                    content = json.loads(record.content) if record.content else {}
                    external_info["company_profile"] = content
                elif record.info_type == "news":
                    content = json.loads(record.content) if record.content else {}
                    external_info["news_snapshot"] = content
                elif record.info_type == "market_info":
                    content = json.loads(record.content) if record.content else {}
                    external_info["market_info"] = content
            except Exception as e:
                print(f"Error loading external info type {record.info_type}: {e}")
        
        return external_info
    
    async def _get_internal_info(self, db: Session, account_id: int) -> Dict[str, Any]:
        """Get internal information (Q&A records)"""
        interactions = db.query(Interaction).filter(
            Interaction.account_id == account_id,
            Interaction.interaction_type == "question"
        ).order_by(Interaction.created_at).all()
        
        # Organize information by category
        organized_info = {
            "cooperation_history": [],
            "products_services": [],
            "challenges": [],
            "key_contacts": [],
            "future_plans": [],
            "resource_needs": []
        }
        
        for interaction in interactions:
            structured_data = interaction.structured_data or {}
            category = self._categorize_question(interaction.question)
            
            organized_info[category].append({
                "question": interaction.question,
                "answer": interaction.answer,
                "structured_data": structured_data,
                "created_at": interaction.created_at.isoformat()
            })
        
        return organized_info
    
    def _categorize_question(self, question: str) -> str:
        """Categorize based on question content"""
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in ["cooperation", "project", "history"]):
            return "cooperation_history"
        elif any(keyword in question_lower for keyword in ["product", "service", "sold"]):
            return "products_services"
        elif any(keyword in question_lower for keyword in ["challenges", "issue", "difficulty"]):
            return "challenges"
        elif any(keyword in question_lower for keyword in ["contact", "key person"]):
            return "key_contacts"
        elif any(keyword in question_lower for keyword in ["plan", "next step", "future"]):
            return "future_plans"
        elif any(keyword in question_lower for keyword in ["resource", "support", "missing"]):
            return "resource_needs"
        else:
            return "cooperation_history"  # Default category
    
    async def _get_customer_profile(self, db: Session, account_id: int) -> Dict[str, Any]:
        """GetCustomer ProfileInfo"""
        try:
            # FindCustomer Profile
            profile_record = db.query(ExternalInfo).filter(
                ExternalInfo.account_id == account_id,
                ExternalInfo.info_type == "customer_profile"
            ).first()
            
            if profile_record and profile_record.content:
                # Parse the content - it might be JSON wrapped
                try:
                    parsed_content = json.loads(profile_record.content)
                    # If it's wrapped in {"profile": "..."}, extract it
                    if isinstance(parsed_content, dict) and "profile" in parsed_content:
                        actual_content = parsed_content["profile"]
                    else:
                        actual_content = profile_record.content
                except:
                    actual_content = profile_record.content
                
                return {
                    "content": actual_content,
                    "created_at": profile_record.created_at.isoformat() if profile_record.created_at else None,
                    "updated_at": profile_record.updated_at.isoformat() if profile_record.updated_at else None
                }
            else:
                return {}
                
        except Exception as e:
            print(f"Error getting customer profile: {e}")
            import traceback
            traceback.print_exc()
            return {}

    async def _generate_plan_content(self, 
                                   account: Account, 
                                   external_info: Dict[str, Any], 
                                   internal_info: Dict[str, Any],
                                   customer_profile: Dict[str, Any] = None,
                                   plan_description: str = None) -> str:
        """Use AI to generate plan content"""
        try:
            # Build context information
            context = self._build_context(account, external_info, internal_info, customer_profile, plan_description)
            
            # Use AI to directly generate plan content, passing all collected data
            plan_content = await self._generate_ai_plan(
                account, 
                external_info, 
                internal_info, 
                customer_profile, 
                plan_description
            )
            
            return plan_content
            
        except Exception as e:
            # If AI generation fails, return basic template
            return self._generate_basic_template(account, external_info, internal_info)
    
    def _build_context(self, 
                      account: Account, 
                      external_info: Dict[str, Any], 
                      internal_info: Dict[str, Any],
                      customer_profile: Dict[str, Any] = None,
                      plan_description: str = None) -> Dict[str, Any]:
        """Build context information"""
        return {
            "company_name": account.company_name,
            "industry": account.industry or "Unknown",
            "company_size": account.company_size or "Unknown",
            "website": account.website or "",
            "company_description": account.description or "No description available",
            "external_info": external_info,
            "internal_info": internal_info,
            "customer_profile": customer_profile or {},
            "plan_description": plan_description or "",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0"
        }
    
    async def _generate_ai_plan(self, 
                               account: Account, 
                               external_info: Dict[str, Any], 
                               internal_info: Dict[str, Any],
                               customer_profile: Dict[str, Any], 
                               plan_description: str = None) -> str:
        """Use AI to generate plan content based on all collected data"""
        try:
            # Get OpenAI client
            client = openai.OpenAI(api_key=settings.openai_api_key)
            
            # Build comprehensive data summary
            company_name = account.company_name
            
            # Extract customer profile
            profile_content = customer_profile.get("content", "No customer profile provided") if customer_profile else "No customer profile provided"
            
            # Extract external information
            external_summary = ""
            if external_info:
                # Company profile
                company_profile_data = external_info.get("company_profile", {})
                if company_profile_data:
                    external_summary += f"\n### Company Profile:\n{json.dumps(company_profile_data, indent=2, ensure_ascii=False)}\n"
                
                # News
                news_data = external_info.get("news_snapshot", {})
                if news_data:
                    external_summary += f"\n### Recent News:\n{json.dumps(news_data, indent=2, ensure_ascii=False)}\n"
                
                # Market info
                market_data = external_info.get("market_info", {})
                if market_data:
                    external_summary += f"\n### Market Information:\n{json.dumps(market_data, indent=2, ensure_ascii=False)}\n"
            
            if not external_summary:
                external_summary = "No external information collected"
            
            # Extract internal information (Q&A)
            internal_summary = ""
            if internal_info:
                for category, items in internal_info.items():
                    if items:
                        internal_summary += f"\n### {category.replace('_', ' ').title()}:\n"
                        for item in items:
                            internal_summary += f"Q: {item['question']}\n"
                            internal_summary += f"A: {item['answer']}\n\n"
            
            if not internal_summary:
                internal_summary = "No internal information (Q&A) collected"
            
            # Build plan description section
            description_section = f"\n### Specific Plan Requirements:\n{plan_description}\n" if plan_description else ""
            
            # Build comprehensive prompt
            prompt = f"""
Please generate a comprehensive strategic customer plan for {company_name} based on ALL the following collected information:

## 1. Customer Profile Analysis
{profile_content}

## 2. External Information (Market, News, Company Data)
{external_summary}

## 3. Internal Information (Q&A Records)
{internal_summary}

## 4. Basic Company Information
- Company Name: {account.company_name}
- Industry: {account.industry or 'Unknown'}
- Company Size: {account.company_size or 'Unknown'}
- Website: {account.website or 'N/A'}
- Description: {account.description or 'No description'}

{description_section}

## Instructions:
Based on ALL the information above (customer profile, external data, and internal Q&A records), generate a detailed strategic plan that includes:

1. **Executive Summary** - Overview of the customer and strategic priorities
2. **Customer Situation Analysis** - Based on customer profile and collected data
3. **Market Position & Competitive Analysis** - Based on external market information
4. **Key Insights from Q&A** - Important findings from internal conversations
5. **Strategic Objectives** - Clear, measurable goals
6. **Action Plan** 
   - Short-term actions (1-3 months)
   - Medium-term actions (3-6 months)
   - Long-term actions (6-12 months)
7. **Resource Requirements** - Based on identified gaps and needs
8. **Risk Assessment** - Potential risks and mitigation strategies
9. **Success Metrics (KPIs)** - How to measure progress
10. **Next Steps** - Immediate actions to take

IMPORTANT: Make sure to reference and utilize ALL the provided data (customer profile, external information, and internal Q&A) in your analysis and recommendations. Do not ignore any section.

Generate the plan in well-structured Markdown format.
"""

            response = client.responses.create(
                model=settings.plan_generation_model,
                instructions=Prompts.STRATEGIC_ACCOUNT_MANAGER.format(company_name=company_name),
                input=prompt,
                reasoning={"effort": (settings.plan_generation_reasoning_effort or settings.default_reasoning_effort or "low")}
            )
            
            return self._extract_responses_text(response)
            
        except Exception as e:
            print(f"Error generating plan content with AI: {e}")
            import traceback
            traceback.print_exc()
            # Return basic plan template
            return f"""
# Strategic Customer Plan - {account.company_name}

## Executive Summary
Develop targeted strategic plans based on customer profile analysis.

## Current Situation Analysis
Need to analyze customer's specific situation and requirement characteristics.

## Target Strategy
Develop targeted market entry and maintenance strategies.

## Action Plan
- Short-term goals (1-3 months)
- Medium-term goals (3-6 months)  
- Long-term goals (6-12 months)

## Expected Results
Set clear success metrics and time nodes.

---
*Plan Generation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Note: This is a basic template. AI plan generation failed.*
"""
    
    async def _fill_template_with_ai(self, template: Template, context: Dict[str, Any]) -> str:
        """Use AI to fill template content"""
        try:
            # Generate content for each template section
            sections = {
                "news_summary": await self._generate_news_summary(context),
                "market_analysis": await self._generate_market_analysis(context),
                "cooperation_projects": await self._generate_cooperation_summary(context),
                "products_services": await self._generate_products_summary(context),
                "key_contacts": await self._generate_contacts_summary(context),
                "current_challenges": await self._generate_challenges_summary(context),
                "challenge_impact": await self._generate_challenge_impact(context),
                "short_term_plans": await self._generate_short_term_plans(context),
                "long_term_plans": await self._generate_long_term_plans(context),
                "expected_outcomes": await self._generate_expected_outcomes(context),
                "resource_gaps": await self._generate_resource_gaps(context),
                "capability_gaps": await self._generate_capability_gaps(context),
                "opportunity_gaps": await self._generate_opportunity_gaps(context),
                "immediate_actions": await self._generate_immediate_actions(context),
                "medium_term_actions": await self._generate_medium_term_actions(context),
                "long_term_actions": await self._generate_long_term_actions(context),
                "responsibility_assignment": await self._generate_responsibility_assignment(context),
                "main_risks": await self._generate_risk_analysis(context),
                "risk_mitigation": await self._generate_risk_mitigation(context),
                "key_metrics": await self._generate_kpis(context),
                "monitoring_frequency": "Monthly evaluation",
                "change_log": "Initial version"
            }
            
            # Merge context and AI-generated content
            full_context = {**context, **sections}
            
            return template.render(**full_context)
            
        except Exception as e:
            print(f"AI template filling failed: {e}")
            return self._generate_basic_template(
                context.get("account"), 
                context.get("external_info", {}), 
                context.get("internal_info", {})
            )

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
    
    async def _generate_news_summary(self, context: Dict[str, Any]) -> str:
        """Generate news summary"""
        news_data = context.get("external_info", {}).get("news_snapshot", {})
        if not news_data:
            return "No relevant news information available."
        
        return news_data.get("summary", "No news summary available.")
    
    async def _generate_market_analysis(self, context: Dict[str, Any]) -> str:
        """Generate market analysis"""
        market_info = context.get("external_info", {}).get("market_info", {})
        if not market_info:
            return "No market analysis information available."
        
        return f"""
**Industry trends:** {market_info.get('trends', 'To be analyzed')}
**Main competitors:** {', '.join(market_info.get('competitors', []))}
**Market opportunities:** {', '.join(market_info.get('opportunities', []))}
**Potential risks:** {', '.join(market_info.get('risks', []))}
        """.strip()
    
    async def _generate_cooperation_summary(self, context: Dict[str, Any]) -> str:
        """Generate cooperation summary"""
        cooperation_data = context.get("internal_info", {}).get("cooperation_history", [])
        if not cooperation_data:
            return "No cooperation history records available."
        
        summary = "### Cooperation ProjectsRecord\n\n"
        for item in cooperation_data:
            summary += f"**Issue：** {item['question']}\n"
            summary += f"**Answer:** {item['answer']}\n\n"
        
        return summary
    
    async def _generate_products_summary(self, context: Dict[str, Any]) -> str:
        """GenerateProducts & ServicesSummary"""
        products_data = context.get("internal_info", {}).get("products_services", [])
        if not products_data:
            return "No products & services records available."
        
        summary = "### Products & ServicesRecord\n\n"
        for item in products_data:
            summary += f"**Issue：** {item['question']}\n"
            summary += f"**Answer:** {item['answer']}\n\n"
        
        return summary
    
    async def _generate_contacts_summary(self, context: Dict[str, Any]) -> str:
        """Generate contacts summary"""
        contacts_data = context.get("internal_info", {}).get("key_contacts", [])
        if not contacts_data:
            return "No key contacts records available."
        
        summary = "### Key Contacts\n\n"
        for item in contacts_data:
            summary += f"**Issue：** {item['question']}\n"
            summary += f"**Answer:** {item['answer']}\n\n"
        
        return summary
    
    async def _generate_challenges_summary(self, context: Dict[str, Any]) -> str:
        """GenerateChallengesSummary"""
        challenges_data = context.get("internal_info", {}).get("challenges", [])
        if not challenges_data:
            return "No challenges & issues records available."
        
        summary = "### Identified Challenges\n\n"
        for item in challenges_data:
            summary += f"**Issue：** {item['question']}\n"
            summary += f"**Answer:** {item['answer']}\n\n"
        
        return summary
    
    async def _generate_challenge_impact(self, context: Dict[str, Any]) -> str:
        """Generate challenges impact analysis"""
        return "Based on identified challenges, analyze their potential impact on cooperation relationships and suggest corresponding response strategies."
    
    async def _generate_short_term_plans(self, context: Dict[str, Any]) -> str:
        """Generate short-term plans"""
        plans_data = context.get("internal_info", {}).get("future_plans", [])
        if not plans_data:
            return "No short-term plan records available."
        
        summary = "### Short-term Plans (3-6 months)\n\n"
        for item in plans_data:
            summary += f"**Plan:** {item['answer']}\n\n"
        
        return summary
    
    async def _generate_long_term_plans(self, context: Dict[str, Any]) -> str:
        """Generate long-term plans"""
        return "Based on the execution of short-term plans, develop long-term strategic cooperation planning."
    
    async def _generate_expected_outcomes(self, context: Dict[str, Any]) -> str:
        """Generate expected results"""
        return "Based on cooperation plans, expect to achieve the following results:\n- Deepen cooperation relationships\n- Expand cooperation scale\n- Improve customer satisfaction\n- Achieve win-win goals"
    
    async def _generate_resource_gaps(self, context: Dict[str, Any]) -> str:
        """Generate resource gap analysis"""
        resource_data = context.get("internal_info", {}).get("resource_needs", [])
        if not resource_data:
            return "No resource needs records available."
        
        summary = "### Resource GapsAnalysis\n\n"
        for item in resource_data:
            summary += f"**Requirement：** {item['answer']}\n\n"
        
        return summary
    
    async def _generate_capability_gaps(self, context: Dict[str, Any]) -> str:
        """Generate capability gap analysis"""
        return "Based on cooperation requirements, identify current capability gaps and develop capability improvement plans."
    
    async def _generate_opportunity_gaps(self, context: Dict[str, Any]) -> str:
        """Generate opportunity gap analysis"""
        return "Analyze market opportunities and cooperation potential, identify underutilized opportunities."
    
    async def _generate_immediate_actions(self, context: Dict[str, Any]) -> str:
        """Generate immediate action items"""
        return """
1. ConfirmKey ContactsInfo
2. Schedule regular communication meetings
3. Develop specific cooperation plans
4. Assign responsibilities and timeline
        """.strip()
    
    async def _generate_medium_term_actions(self, context: Dict[str, Any]) -> str:
        """Generate medium-term action items"""
        return """
1. Execute cooperation projects
2. Monitor project progress
3. Resolve emerging issues
4. Evaluate cooperation effectiveness
        """.strip()
    
    async def _generate_long_term_actions(self, context: Dict[str, Any]) -> str:
        """Generate long-term action items"""
        return """
1. Expand cooperation scope
2. Establish strategic partnerships
3. Continuously optimize cooperation models
4. Explore new cooperation opportunities
        """.strip()
    
    async def _generate_responsibility_assignment(self, context: Dict[str, Any]) -> str:
        """Generate responsibility assignment"""
        return """
- **Project Manager:** Responsible for overall coordination and progress management
- **Technical Lead:** Responsible for technical solutions and implementation
- **Account Manager:** Responsible for customer relationship maintenance
- **Finance Lead:** Responsible for budget and cost control
        """.strip()
    
    async def _generate_risk_analysis(self, context: Dict[str, Any]) -> str:
        """GenerateRiskAnalysis"""
        return """
1. **Technical Risk:** Technical implementation difficulty and compatibility issues
2. **Market Risk:** Market changes and competitive pressure
3. **Cooperation Risk:** Cooperation relationship stability and communication issues
4. **Resource Risk:** Insufficient resources and cost overruns
        """.strip()
    
    async def _generate_risk_mitigation(self, context: Dict[str, Any]) -> str:
        """Generate risk response strategies"""
        return """
1. **Technical Risk Response:** Conduct technical validation in advance, develop backup plans
2. **Market Risk Response:** Closely monitor market dynamics, adjust strategies timely
3. **Cooperation Risk Response:** Establish regular communication mechanisms, resolve issues timely
4. **Resource Risk Response:** Plan resources reasonably, establish monitoring mechanisms
        """.strip()
    
    async def _generate_kpis(self, context: Dict[str, Any]) -> str:
        """Generate key metrics"""
        return """
- **Cooperation Project Count:** Target number of completed projects
- **Customer Satisfaction:** Customer feedback score
- **Revenue Growth:** Revenue growth from cooperation
- **Project Success Rate:** Percentage of successfully completed projects
        """.strip()
    
    def _generate_basic_template(self, account: Account, external_info: Dict[str, Any], internal_info: Dict[str, Any]) -> str:
        """Generate basic template (used when AI generation fails)"""
        template = Template(self.template)
        context = self._build_context(account, external_info, internal_info)
        
        # Fill basic information
        basic_sections = {
            "news_summary": "No news information available",
            "market_analysis": "No market analysis available",
            "cooperation_projects": "No cooperation records available",
            "products_services": "No products & services records available",
            "key_contacts": "No contact records available",
            "current_challenges": "No challenges records available",
            "challenge_impact": "To be analyzed",
            "short_term_plans": "To be developed",
            "long_term_plans": "To be developed",
            "expected_outcomes": "To be clarified",
            "resource_gaps": "To be analyzed",
            "capability_gaps": "To be analyzed",
            "opportunity_gaps": "To be analyzed",
            "immediate_actions": "To be developed",
            "medium_term_actions": "To be developed",
            "long_term_actions": "To be developed",
            "responsibility_assignment": "To be assigned",
            "main_risks": "To be identified",
            "risk_mitigation": "To be developed",
            "key_metrics": "To be determined",
            "monitoring_frequency": "To be determined",
            "change_log": "Initial version"
        }
        
        full_context = {**context, **basic_sections}
        return template.render(**full_context)
    
    async def update_plan(self, 
                         db: Session, 
                         plan_id: int, 
                         updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update plan"""
        try:
            plan = db.query(AccountPlan).filter(AccountPlan.id == plan_id).first()
            if not plan:
                raise ValueError(f"Plan ID {plan_id} does not exist")
            
            # Update plan content
            if "content" in updates:
                plan.content = updates["content"]
            
            if "title" in updates:
                plan.title = updates["title"]
            
            if "status" in updates:
                plan.status = updates["status"]
            
            # Update change log
            change_log = plan.change_log or {}
            change_log[datetime.now().isoformat()] = updates
            plan.change_log = change_log
            
            plan.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                "plan_id": plan.id,
                "title": plan.title,
                "status": plan.status,
                "updated_at": plan.updated_at.isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
