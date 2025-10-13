# Prompts Configuration Guide

## Overview
All AI interaction prompts are now centrally managed in the `prompts.py` file for easy modification, optimization, and maintenance.

## Configuration File Structure

### 1. System Role Prompts
Defines professional roles for different AI tasks:

- **CUSTOMER_MANAGER**: Customer manager role
- **CRM_EXPERT**: Customer relationship management expert
- **BUSINESS_ANALYST**: Business information analyst
- **NEWS_ANALYST**: Business news analyst
- **BUSINESS_SUMMARY_ANALYST**: Business analyst
- **MARKET_ANALYST**: Market analyst
- **CUSTOMER_ANALYSIS_EXPERT**: Customer analysis expert
- **CONVERSATION_SUMMARY_EXPERT**: Conversation summary expert
- **DATA_EXTRACTION_EXPERT**: Information extraction expert
- **HISTORY_ANALYSIS_EXPERT**: Historical analysis expert
- **DATA_ANALYST**: Data analyst
- **STRATEGIC_ACCOUNT_MANAGER**: Strategic account management expert

### 2. Functional Module Prompts

#### Conversation Management (ConversationManager)
- **INITIAL_QUESTION_GENERATION**: Initial question generation
- **CONVERSATION_START**: Conversation start prompt
- **FOLLOW_UP_QUESTION_GENERATION**: Follow-up question generation
- **CONVERSATION_SUMMARY**: Conversation summary

#### External Information Collection (ExternalInfoCollector)
- **COMPANY_INFO_EXTRACTION**: Company profile extraction
- **NEWS_SUMMARY_GENERATION**: News summary generation
- **MARKET_ANALYSIS**: Market analysis

#### Customer Profile Generation (CustomerProfile)
- **CUSTOMER_PROFILE_ANALYSIS**: Customer profile analysis

#### Plan Generation (PlanGenerator)
- **STRATEGIC_PLAN_GENERATION**: Strategic plan generation

#### Question Management (QuestionManager)
- **QUESTION_GENERATION**: Question generation
- **INFO_COMPLETENESS_ANALYSIS**: Information completeness analysis
- **HISTORY_ANALYSIS**: Historical information analysis
- **DATA_CHANGE_ANALYSIS**: Data change analysis

#### Dynamic Questioning (DynamicQuestioning)
- **INTELLIGENT_QUESTION_GENERATION**: Intelligent question generation
- **DERIVATIVE_QUESTION_GENERATION**: Derivative question generation
- **BACKGROUND_ADAPTED_QUESTIONS**: Background-adapted question generation

## Usage

### 1. Modifying Prompts
Directly edit the corresponding prompt in the `prompts.py` file:

```python
# Example: Modify customer manager role
CUSTOMER_MANAGER = "You are a professional customer manager who excels at understanding customer needs through in-depth questioning. You must strictly base your questions on the provided information and not fabricate any details."
```

### 2. Adding New Prompts
Add new prompt constants to the `Prompts` class:

```python
class Prompts:
    # Existing prompts...
    
    # New prompt
    NEW_PROMPT = "New prompt content, supports {variable} formatting"
```

### 3. Using Prompts
Use configured prompts in your code:

```python
from prompts import Prompts

# Use system role
{"role": "system", "content": Prompts.CUSTOMER_MANAGER}

# Use functional prompt
prompt = Prompts.INITIAL_QUESTION_GENERATION.format(
    question=question,
    history_summary=history_summary
)
```

## Prompt Design Principles

### 1. Clear Roles
Each prompt defines a clear AI role to ensure professionalism and consistency in responses.

### 2. Task-Oriented
Prompts are designed for specific tasks and include clear task requirements and output formats.

### 3. Parameterized
Uses `{variable}` format to support dynamic content insertion, improving prompt flexibility.

### 4. Structured Output
For tasks requiring structured data, explicitly specify JSON format requirements.

### 5. Language Optimization
All prompts are optimized for English to ensure output quality.

## Configuration Management

### 1. Environment Variable Control
In `config.py`, you can control prompt usage through environment variables:

```python
# Prompt configuration
use_custom_prompts: bool = True
prompts_file: str = "prompts.py"
```

### 2. Version Control
- Prompt files are under version control
- Important changes require changelog entries
- Recommend maintaining different prompt versions for different environments

### 3. Testing and Validation
After modifying prompts:
1. Run related functional tests
2. Check output quality and format
3. Verify parameterization works correctly

## Optimization Recommendations

### 1. Performance Optimization
- Keep prompts concise and clear
- Avoid overly complex instructions
- Use appropriate temperature parameters

### 2. Quality Improvement
- Regularly evaluate prompt effectiveness
- Adjust based on actual usage
- Collect user feedback for optimization

### 3. Maintenance Management
- Establish prompt change processes
- Document reasons for important modifications
- Keep prompt documentation updated

## Important Notes

1. **Format Consistency**: Ensure all prompts use uniform format and style
2. **Parameter Security**: Pay attention to input validation and escaping when using parameterization
3. **Version Compatibility**: Consider backward compatibility when modifying prompts
4. **Test Coverage**: Important prompt modifications require thorough testing
5. **Documentation Sync**: Update related documentation promptly after prompt modifications

## Model Configuration

The system supports different OpenAI models for various tasks:

- **Conversation Model**: GPT-5, o1-mini (configurable)
- **Analysis Model**: o1-mini, o1-preview (configurable)
- **Plan Generation Model**: o1-preview (configurable)

See `MODEL_CONFIG.md` for detailed model configuration options.

## Reasoning Effort

For o1 series models, you can configure reasoning effort levels:

- **low**: Fast responses, basic reasoning
- **medium**: Balanced performance (default)
- **high**: Deep analysis, comprehensive reasoning

Configure in environment variables:
```bash
DEFAULT_REASONING_EFFORT=medium
CONVERSATION_REASONING_EFFORT=low
PROFILE_GENERATION_REASONING_EFFORT=high
PLAN_GENERATION_REASONING_EFFORT=high
```

## Best Practices

1. **Test Before Deploy**: Always test prompt changes before deploying to production
2. **Keep History**: Maintain a history of prompt changes and their effects
3. **Document Changes**: Document why prompts were changed and what improved
4. **Use Variables**: Leverage parameterization for flexible, reusable prompts
5. **Monitor Quality**: Continuously monitor AI output quality and adjust prompts accordingly

By centrally managing prompts, you can better control AI behavior and improve system consistency and maintainability.
