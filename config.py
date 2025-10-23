"""
Configuration file
"""
import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings
    from pydantic import ConfigDict
except ImportError:
    from pydantic import BaseSettings
    from pydantic import BaseConfig as ConfigDict

class Settings(BaseSettings):
    # OpenAI API Configuration
    openai_api_key: str = ""
    
    # Database Configuration
    database_url: str = "sqlite:///./account_plan_agent.db"
    
    # External API Configuration
    news_api_key: Optional[str] = None
    search_api_key: Optional[str] = None
    
    # Application Configuration
    debug: bool = True
    host: str = "127.0.0.1"  # Use 127.0.0.1 to ensure local access
    port: int = 8000
    
    # AI Model Configuration (default uses gpt-4o-mini, can be overridden by .env)
    default_model: str = "gpt-4o-mini"
    plan_generation_model: str = "gpt-4o-mini"
    conversation_model: str = "gpt-4o-mini"
    external_info_model: str = "gpt-5-mini"  # Use gpt-5-mini for external info
    # OpenAI Responses API for external info (web search)
    external_responses_model: str = "gpt-5-mini"
    external_use_responses: bool = True  # Keep web search functionality enabled
    question_model: str = "gpt-4o-mini"
    history_model: str = "gpt-4o-mini"
    dynamic_questioning_model: str = "gpt-4o-mini"

    # Default reasoning setup (Responses API)
    default_reasoning_effort: str = "low"
    # Module-specific reasoning effort (can be overridden by .env individually; falls back to default if empty)
    conversation_reasoning_effort: Optional[str] = None
    question_reasoning_effort: Optional[str] = None
    history_reasoning_effort: Optional[str] = None
    dynamic_questioning_reasoning_effort: Optional[str] = None
    plan_generation_reasoning_effort: Optional[str] = None
    external_info_reasoning_effort: Optional[str] = None
    external_responses_reasoning_effort: Optional[str] = None
    
    # Temperature parameters (gpt-5 does not support, keep field but no longer use)
    default_temperature: float = 0.0
    conversation_temperature: float = 0.0
    external_info_temperature: float = 0.0
    question_temperature: float = 0.0
    history_temperature: float = 0.0
    dynamic_questioning_temperature: float = 0.0
    plan_generation_temperature: float = 0.0
    
    # Special purpose temperature parameters (gpt-5 does not support, keep field but no longer use)
    creative_temperature: float = 0.0
    analysis_temperature: float = 0.0
    summary_temperature: float = 0.0
    
    # Prompt configuration
    use_custom_prompts: bool = True
    prompts_file: str = "prompts.py"
    
    # External data source integration (optional)
    # MCP Server Configure
    mcp_enabled: bool = False
    mcp_endpoint: Optional[str] = None  # e.g.: http://localhost:9000/tools
    mcp_api_key: Optional[str] = None
    
    # External AI Agent gateway configuration (e.g. self-built agent or third-party agent service)
    agent_enabled: bool = False
    agent_endpoint: Optional[str] = None  # e.g.: https://agent.example.com/query
    agent_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
