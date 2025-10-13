"""
AI Prompt Configuration File
Centralized management of all AI interaction prompts for easy modification and optimization
"""

class Prompts:
    """Prompt configuration class"""
    
    # ==================== System Role Prompts ====================
    
    # Customer Manager Role
    CUSTOMER_MANAGER = "You are a professional customer manager, skilled at understanding customer needs through in-depth questioning. You must strictly ask questions based on the provided information and cannot fabricate any details."
    
    # Customer Relationship Management Expert
    CRM_EXPERT = "You are a professional customer relationship management expert, skilled at analyzing the relevance of historical information."
    
    # Business Information Analyst
    BUSINESS_ANALYST = "You are a professional business information analyst, skilled at extracting basic company information from public sources."
    
    # Business News Analyst
    NEWS_ANALYST = "You are a professional business news analyst, skilled at generating news summaries that align with actual situations."
    
    # Business Analyst
    BUSINESS_SUMMARY_ANALYST = "You are a professional business analyst, skilled at extracting key information from news and generating comprehensive summaries."
    
    # Market Analyst
    MARKET_ANALYST = "You are a professional market analyst, skilled at analyzing industry trends and competitive landscape."
    
    # Customer Analysis Expert
    CUSTOMER_ANALYSIS_EXPERT = "You are a professional customer analysis expert, skilled at generating professional customer profile analysis reports based on collected information."
    
    # Conversation Summary Expert
    CONVERSATION_SUMMARY_EXPERT = "You are a professional customer relationship management expert, skilled at summarizing customer conversations."
    
    # Data Extraction Expert
    DATA_EXTRACTION_EXPERT = "You are a professional data extraction expert, skilled at extracting structured data from conversations."
    
    # History Analysis Expert
    HISTORY_ANALYSIS_EXPERT = "You are a professional customer relationship management expert, skilled at analyzing the timeliness and effectiveness of historical information."
    
    # Data Analyst
    DATA_ANALYST = "You are a professional data analyst, skilled at detecting and analyzing data changes."
    
    # Strategic Account Manager
    STRATEGIC_ACCOUNT_MANAGER = "As a strategic account management expert, based on the following customer profile information, generate a professional strategic action plan for {company_name}."
    
    # ==================== Conversation Management Prompts ====================
    
    # Initial Question Generation
    INITIAL_QUESTION_GENERATION = """
Based on the following customer information and question templates, generate 3-5 initial questions to understand the customer's basic situation and needs.

Customer Information:
{account_info}

Question Templates:
{question_templates}

Requirements:
1. Questions should be open-ended and encourage detailed responses
2. Cover different aspects: cooperation history, products/services, challenges, key contacts, future plans, resource needs
3. Questions should be professional and business-oriented
4. Avoid overly personal or sensitive questions
5. Each question should be clear and specific

Please generate questions in the following format:
1. [Question content]
2. [Question content]
3. [Question content]
...
"""

    # Follow-up Question Generation
    FOLLOW_UP_QUESTION_GENERATION = """
Based on the customer's previous response, generate 2-3 follow-up questions to gain deeper understanding.

Previous Question: {previous_question}
Customer Response: {customer_response}
Question Category: {category}

Requirements:
1. Questions should be based on the customer's response
2. Dig deeper into specific points mentioned
3. Explore potential opportunities or challenges
4. Maintain professional tone
5. Avoid repetitive questions

Please generate follow-up questions in the following format:
1. [Question content]
2. [Question content]
3. [Question content]
"""

    # AI Response Generation
    AI_RESPONSE_GENERATION = """
As a professional customer manager, provide a thoughtful response to the customer's question.

Customer Question: {question}
Customer Response: {response}

Requirements:
1. Acknowledge the customer's response
2. Provide professional insights or suggestions
3. Ask relevant follow-up questions if appropriate
4. Maintain a helpful and professional tone
5. Keep responses concise but informative

Please provide your response:
"""

    # Conversation Summary
    CONVERSATION_SUMMARY = """
Summarize the following conversation between the customer manager and customer, extracting key information and insights.

Previous Summary: {previous_summary}

Current Conversation:
{conversation_content}

Requirements:
1. Integrate with previous summary if provided
2. Extract key information and insights
3. Identify important details and action items
4. Maintain professional tone
5. Structure the summary clearly

Please provide a comprehensive summary:
"""

    # ==================== Question Management Prompts ====================
    
    # Follow-up Question Analysis
    FOLLOW_UP_QUESTION_ANALYSIS = """
Based on the customer's response, analyze what additional information is needed and generate relevant follow-up questions.

Customer Response: {response}
Question Category: {category}
Historical Context: {historical_context}

Requirements:
1. Analyze the response for missing information
2. Identify areas that need clarification
3. Generate 2-3 targeted follow-up questions
4. Consider the question category and context
5. Maintain professional and helpful tone

Please provide your analysis and questions:
"""

    # Structured Data Extraction
    STRUCTURED_DATA_EXTRACTION = """
Extract structured data from the following conversation content.

Conversation Content: {conversation_content}
Question Category: {category}

Requirements:
1. Extract key information based on the question category
2. Structure the data in a clear format
3. Identify important details and insights
4. Maintain data accuracy and completeness
5. Use appropriate data types and formats

Please extract the structured data:
"""

    # Historical Context Analysis
    HISTORICAL_CONTEXT_ANALYSIS = """
Analyze the relevance of historical information to the current question.

Current Question: {current_question}
Historical Information: {historical_info}

Requirements:
1. Assess the relevance of historical information
2. Identify useful context and insights
3. Suggest how to use historical information
4. Maintain professional analysis standards
5. Provide clear recommendations

Please provide your analysis:
"""

    # ==================== History Management Prompts ====================
    
    # Relevance Analysis
    RELEVANCE_ANALYSIS = """
Analyze the relevance of historical information to the current question.

Current Question: {current_question}
Historical Information: {historical_info}

Requirements:
1. Assess the relevance level (high/medium/low)
2. Identify specific relevant information
3. Explain the relevance reasoning
4. Suggest how to use the information
5. Maintain objective analysis

Please provide your relevance analysis:
"""

    # Prefill Suggestions
    PREFILL_SUGGESTIONS = """
Based on historical information, provide suggestions for pre-filling current questions.

Historical Information: {historical_info}
Current Questions: {current_questions}

Requirements:
1. Identify information that can be pre-filled
2. Provide specific pre-fill suggestions
3. Explain the reasoning behind suggestions
4. Maintain data accuracy
5. Consider information timeliness

Please provide your pre-fill suggestions:
"""

    # Change Analysis
    CHANGE_ANALYSIS = """
Analyze changes in customer information over time.

Historical Information: {historical_info}
Current Information: {current_info}

Requirements:
1. Identify significant changes
2. Analyze the impact of changes
3. Provide insights and recommendations
4. Maintain professional analysis standards
5. Consider business implications

Please provide your change analysis:
"""

    # ==================== External Information Collection Prompts ====================
    
    # Company Profile Analysis
    COMPANY_PROFILE_ANALYSIS = """
Analyze the following company information and extract key details.

Company Information: {company_info}

Requirements:
1. Extract basic company information
2. Identify key business characteristics
3. Analyze company strengths and opportunities
4. Provide professional insights
5. Structure the information clearly

Please provide your analysis:
"""

    # News Summary Generation
    NEWS_SUMMARY_GENERATION = """
Generate a comprehensive summary of the following news information.

News Information: {news_info}

Requirements:
1. Extract key news points
2. Analyze business implications
3. Identify important trends
4. Provide professional insights
5. Maintain objective analysis

Please provide your news summary:
"""

    # Market Analysis
    MARKET_ANALYSIS = """
Analyze the following market information and provide insights.

Market Information: {market_info}

Requirements:
1. Analyze market trends
2. Identify competitive landscape
3. Provide strategic insights
4. Consider business implications
5. Maintain professional analysis

Please provide your market analysis:
"""

    # ==================== Customer Profile Generation Prompts ====================
    
    # Customer Profile Analysis
    CUSTOMER_PROFILE_ANALYSIS = """
Based on the following collected information, generate a comprehensive customer profile analysis report.

External Information: {external_info}
Internal Information: {internal_info}

Requirements:
1. Integrate external and internal information
2. Generate professional analysis
3. Identify key customer characteristics
4. Provide strategic insights
5. Structure the report clearly

Please provide your customer profile analysis:
"""

    # ==================== Plan Generation Prompts ====================
    
    # Strategic Plan Generation
    STRATEGIC_PLAN_GENERATION = """
Based on the following customer profile and plan description, generate a professional strategic account plan.

Customer Profile: {customer_profile}
Plan Description: {plan_description}
Company Name: {company_name}

Requirements:
1. Generate a comprehensive strategic plan
2. Include specific action items
3. Consider customer characteristics
4. Provide professional recommendations
5. Structure the plan clearly

Please provide your strategic plan:
"""

    # ==================== Dynamic Questioning Prompts ====================
    
    # Missing Information Analysis
    MISSING_INFORMATION_ANALYSIS = """
Analyze what information is missing for the current customer and suggest questions to gather it.

Current Information: {current_info}
Question Categories: {question_categories}

Requirements:
1. Identify missing information gaps
2. Suggest relevant questions
3. Prioritize questions by importance
4. Consider information relationships
5. Maintain professional standards

Please provide your analysis and suggestions:
"""

    # Intelligent Question Generation
    INTELLIGENT_QUESTION_GENERATION = """
Generate intelligent questions based on the current context and customer information.

Context: {context}
Customer Information: {customer_info}
Question Category: {category}

Requirements:
1. Generate contextually relevant questions
2. Consider customer characteristics
3. Maintain professional tone
4. Encourage detailed responses
5. Avoid repetitive questions

Please provide your intelligent questions:
"""

    # Follow-up Question Generation
    FOLLOW_UP_QUESTION_GENERATION_DYNAMIC = """
Generate follow-up questions based on the customer's response and context.

Customer Response: {customer_response}
Context: {context}
Question Category: {category}

Requirements:
1. Build on the customer's response
2. Explore deeper insights
3. Maintain conversation flow
4. Consider business objectives
5. Provide value to the customer

Please provide your follow-up questions:
"""

    # Question Adaptation
    QUESTION_ADAPTATION = """
Adapt the following question to better suit the current context and customer.

Original Question: {original_question}
Context: {context}
Customer Information: {customer_info}

Requirements:
1. Adapt the question to the context
2. Make it more relevant to the customer
3. Maintain the original intent
4. Improve question effectiveness
5. Keep it professional

Please provide your adapted question:
"""