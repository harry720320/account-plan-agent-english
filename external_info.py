"""
External information collection module
Responsible for collecting company information and news from external APIs
"""
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from config import settings
from prompts import Prompts
import openai

class ExternalInfoCollector:
    """External information collector"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        self.mcp_enabled = bool(getattr(settings, "mcp_enabled", False) and getattr(settings, "mcp_endpoint", None))
        self.agent_enabled = bool(getattr(settings, "agent_enabled", False) and getattr(settings, "agent_endpoint", None))

    # ===================== External data source common calls =====================
    def _call_mcp(self, tool: str, payload: Dict[str, Any]) -> Optional[Any]:
        """Call MCP Server tool (assuming HTTP JSON interface)"""
        if not self.mcp_enabled:
            return None
        try:
            headers = {"Content-Type": "application/json"}
            if getattr(settings, "mcp_api_key", None):
                headers["Authorization"] = f"Bearer {settings.mcp_api_key}"
            resp = requests.post(
                settings.mcp_endpoint,
                json={"tool": tool, "input": payload},
                headers=headers,
                timeout=12
            )
            if resp.status_code == 200:
                data = resp.json()
                # Compatible with data / result field
                return data.get("data") or data.get("result") or data
        except Exception as e:
            print(f"MCP call failed ({tool}): {e}")
        return None

    # ===================== OpenAI Chat Completions + web_search =====================
    def _responses_web_search(self, query: str, system_prompt: str, expect_json: bool = False) -> Optional[Any]:
        """Use OpenAI Responses API for information generation (simulated web search)"""
        try:
            client = self.openai_client
            # Temporarily remove web_search tool to test basic functionality
            # tools = [{"type": "web_search"}]
            # Responses API recommends using instructions instead of system; input can be String or MessageList
            response = client.responses.create(
                model=getattr(settings, "external_responses_model", settings.external_info_model),
                instructions=f"{system_prompt}\n\nPlease generate realistic data based on the query. If you cannot find real information, generate plausible simulated data that would be typical for the requested information.",
                input=query,
                # tools=tools,
                # tool_choice="auto",
                reasoning={"effort": (settings.external_responses_reasoning_effort or settings.default_reasoning_effort or "low")}
            )

            # Extract text, compatible with many SDK structures
            text = getattr(response, "output_text", None)
            if not text:
                try:
                    # Try to extract from content stack
                    # Some SDKs return response.output[0].content[0].text.value
                    output = getattr(response, "output", None) or []
                    if output and isinstance(output, list):
                        contents = output[0].get("content") or []
                        if contents and isinstance(contents, list):
                            text_part = contents[0].get("text") or {}
                            text = text_part.get("value")
                except Exception:
                    pass

            if not text:
                return None

            if expect_json and isinstance(text, str):
                # Try strict JSON parsing
                try:
                    return json.loads(text)
                except Exception:
                    # Extract first JSON block from text
                    import re
                    json_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
                    if json_match:
                        try:
                            return json.loads(json_match.group(1))
                        except Exception:
                            return text
                    return text
            return text
        except Exception as e:
            print(f"Responses+web_search Failure: {e}")
            return None

    def _call_agent(self, task: str, payload: Dict[str, Any]) -> Optional[Any]:
        """Call external AI Agent gateway (HTTP JSON interface)"""
        if not self.agent_enabled:
            return None
        try:
            headers = {"Content-Type": "application/json"}
            if getattr(settings, "agent_api_key", None):
                headers["Authorization"] = f"Bearer {settings.agent_api_key}"
            resp = requests.post(
                settings.agent_endpoint,
                json={"task": task, "input": payload},
                headers=headers,
                timeout=12
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data") or data.get("result") or data
        except Exception as e:
            print(f"Agent call failed ({task}): {e}")
        return None
    
    async def get_company_profile(self, company_name: str) -> Dict[str, Any]:
        """
        Get company basic information
        """
        try:
            # 0) Priority: Responses+web_search (online retrieval)
            if getattr(settings, "external_use_responses", True):
                query = (
                    f"Search and summarize basic information about {company_name}, "
                    "output JSON with fields: company_name, industry, company_size, website, description."
                )
                res = self._responses_web_search(query, Prompts.BUSINESS_ANALYST, expect_json=True)
                if isinstance(res, dict) and res.get("company_name"):
                    return {
                        "company_name": res.get("company_name", company_name),
                        "industry": res.get("industry", "To be confirmed"),
                        "company_size": res.get("company_size", "To be confirmed"),
                        "website": res.get("website", ""),
                        "description": res.get("description", "")
                    }

            # 1) MCP Server
            if self.mcp_enabled:
                mcp_res = self._call_mcp("company_profile", {"company_name": company_name})
                if isinstance(mcp_res, dict) and mcp_res:
                    return {
                        "company_name": mcp_res.get("company_name", company_name),
                        "industry": mcp_res.get("industry", "To be confirmed"),
                        "company_size": mcp_res.get("company_size", "To be confirmed"),
                        "website": mcp_res.get("website", ""),
                        "description": mcp_res.get("description", "")
                    }

            # 2) ExternalAgent
            if self.agent_enabled:
                agent_res = self._call_agent("company_profile", {"company_name": company_name})
                if isinstance(agent_res, dict) and agent_res:
                    return {
                        "company_name": agent_res.get("company_name", company_name),
                        "industry": agent_res.get("industry", "To be confirmed"),
                        "company_size": agent_res.get("company_size", "To be confirmed"),
                        "website": agent_res.get("website", ""),
                        "description": agent_res.get("description", "")
                    }

            # 3) Fallback to OpenAI solution
            company_info = await self._search_company_info(company_name)
            return company_info
        except Exception as e:
            print(f"Get company information failed: {e}")
            return {
                "company_name": company_name,
                "industry": "Unknown",
                "company_size": "Unknown",
                "website": "",
                "description": "Unable to get detailed company information",
                "error": str(e)
            }
    
    async def get_news_snapshot(self, company_name: str, months: int = 6) -> Dict[str, Any]:
        """
        Get company news snapshot
        """
        try:
            # Calculate time range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            # Get news data
            news_data = await self._search_news(company_name, start_date, end_date)
            
            # Use AI to generate news summary
            summary = await self._generate_news_summary(news_data, company_name)
            
            return {
                "company_name": company_name,
                "time_range": f"{months} months",
                "news_count": len(news_data),
                "news_data": news_data,
                "summary": summary,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Get news information failed: {e}")
            return {
                "company_name": company_name,
                "time_range": f"{months} months",
                "news_count": 0,
                "news_data": [],
                "summary": "Unable to get relevant news information",
                "error": str(e)
            }
    
    async def _search_company_info(self, company_name: str) -> Dict[str, Any]:
        """
        Search company basic information
        """
        # Here you can integrate various search APIs, such as Google Custom Search, Bing Search, etc.
        # For demonstration, we use simulated data
        search_query = f"{company_name} Company Description official website"
        
        # Use OpenAI for information extraction and summary
        prompt = f"""
        Please search and summarize basic information about "{company_name}" company, including:
        1. Company industry
        2. Company size (number of employees, annual revenue, etc.)
        3. Official website URL
        4. Company description (100-200 words)
        
        Please return results in JSON format.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.external_info_model,
                messages=[
                    {"role": "system", "content": Prompts.BUSINESS_ANALYST},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_completion_tokens=2000
            )
            
            result = response.choices[0].message.content
            # Try to parse JSON results
            try:
                company_data = json.loads(result)
            except:
                # If parsing fails, create default structure
                company_data = {
                    "company_name": company_name,
                    "industry": "To be confirmed",
                    "company_size": "To be confirmed",
                    "website": "",
                    "description": result
                }
            
            return company_data
            
        except Exception as e:
            # Return default information
            return {
                "company_name": company_name,
                "industry": "To be confirmed",
                "company_size": "To be confirmed", 
                "website": "",
                "description": f"Unable to get detailed information about {company_name}, please supplement manually.",
                "error": str(e)
            }
    
    async def _search_news(self, company_name: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Search company related news
        """
        # 0) Responses+web_search (online news retrieval)
        if getattr(settings, "external_use_responses", True):
            query = (
                f"Search news related to {company_name} from {start_date.date()} to {end_date.date()}, "
                "output JSON array, each item include: title, summary, date, source"
            )
            res = self._responses_web_search(query, Prompts.NEWS_ANALYST, expect_json=True)
            if isinstance(res, list) and res:
                return res
            # Loose handling: if returned is string, try to parse
            if isinstance(res, str):
                try:
                    parsed = json.loads(res)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass

        # 1) MCP/Agent pull news
        if self.mcp_enabled:
            mcp_news = self._call_mcp("company_news", {"company_name": company_name, "start": start_date.isoformat(), "end": end_date.isoformat()})
            if isinstance(mcp_news, list) and mcp_news:
                return mcp_news
        if self.agent_enabled:
            agent_news = self._call_agent("company_news", {"company_name": company_name, "start": start_date.isoformat(), "end": end_date.isoformat()})
            if isinstance(agent_news, list) and agent_news:
                return agent_news

        # 2) Fallback: use OpenAI to generate simulated news data (demo)
        prompt = f"""
        Please generate simulated news titles and summaries for "{company_name}" company in the last 6 months, including:
        1. Business development dynamics
        2. Product releases
        3. Cooperation news
        4. Market performance
        5. Personnel changes
        
        Please return in JSON array format, each news include: title, summary, date, source
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.external_info_model,
                messages=[
                    {"role": "system", "content": Prompts.NEWS_ANALYST},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_completion_tokens=2000
            )
            
            result = response.choices[0].message.content
            try:
                news_data = json.loads(result)
                return news_data if isinstance(news_data, list) else []
            except:
                return []
                
        except Exception as e:
            print(f"Search news failed: {e}")
            return []
    
    async def _generate_news_summary(self, news_data: List[Dict[str, Any]], company_name: str) -> str:
        """
        Generate news summary
        """
        if not news_data:
            return f"No relevant news information about {company_name} available."
        
        # Build news content
        news_text = "\n".join([
            f"Title: {news.get('title', '')}\nSummary: {news.get('summary', '')}\nDate: {news.get('date', '')}\n"
            for news in news_data
        ])
        
        prompt = f"""
        Please generate a comprehensive summary for the following news about "{company_name}" company, highlighting:
        1. Main business dynamics
        2. Market performance
        3. Development trends
        4. Key events
        
        News content:
        {news_text}
        
        Please generate a 200-300 word summary.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.external_info_model,
                messages=[
                    {"role": "system", "content": Prompts.BUSINESS_SUMMARY_ANALYST},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_completion_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Unable to generate news summary for {company_name}: {str(e)}"
    
    async def get_market_info(self, company_name: str, industry: str = None) -> Dict[str, Any]:
        """
        Get market information
        """
        try:
            # 0) Responses+web_search (online market information retrieval)
            if getattr(settings, "external_use_responses", True):
                query = (
                    f"Search and analyze market situation of {company_name} in industry ({industry or 'Unknown'}), "
                    "output JSON with fields: industry, trends, competitors, opportunities, risks"
                )
                res = self._responses_web_search(query, Prompts.MARKET_ANALYST, expect_json=True)
                if isinstance(res, dict) and res:
                    return res
                if isinstance(res, str):
                    try:
                        parsed = json.loads(res)
                        if isinstance(parsed, dict):
                            return parsed
                    except Exception:
                        pass

            # 1) MCP Server
            if self.mcp_enabled:
                mcp_market = self._call_mcp("market_info", {"company_name": company_name, "industry": industry})
                if isinstance(mcp_market, dict) and mcp_market:
                    return mcp_market
            # 2) ExternalAgent
            if self.agent_enabled:
                agent_market = self._call_agent("market_info", {"company_name": company_name, "industry": industry})
                if isinstance(agent_market, dict) and agent_market:
                    return agent_market

            # 3) Fallback to OpenAI analysis
            prompt = f"""
            Please analyze market situation of "{company_name}" company in industry "{industry or 'Unknown'}", including:
            1. Industry development trends
            2. Main competitors
            3. Market opportunities
            4. Potential risks
            
            Please return analysis results in JSON format.
            """
            response = self.openai_client.chat.completions.create(
                model=settings.external_info_model,
                messages=[
                    {"role": "system", "content": Prompts.MARKET_ANALYST},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_completion_tokens=2000
            )
            result = getattr(response, "output_text", None) or ""
            if not result:
                result = self._extract_text_fallback(response)
            try:
                market_data = json.loads(result)
            except:
                market_data = {
                    "industry": industry or "Unknown",
                    "trends": "To be analyzed",
                    "competitors": [],
                    "opportunities": [],
                    "risks": []
                }
            
            return market_data
            
        except Exception as e:
            return {
                "industry": industry or "Unknown",
                "trends": "Unable to get market information",
                "competitors": [],
                "opportunities": [],
                "risks": [],
                "error": str(e)
            }

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
