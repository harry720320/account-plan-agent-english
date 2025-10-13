# 模型配置说明（Responses API + .env 可覆盖）

## 概述
所有AI模型设置现在都通过`.env`文件进行配置，支持灵活调整不同场景下的模型和参数。全局默认采用 Responses API，模型默认 `gpt-5-mini`，并可逐模块覆盖。推理强度（reasoning.effort）默认 `low`，也可逐模块覆盖。

## 创建.env文件
在项目根目录创建`.env`文件，复制以下内容并填入您的API密钥：

```env
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here

# 数据库配置
DATABASE_URL=sqlite:///./account_plan_agent.db

# 外部API配置（可选）
NEWS_API_KEY=
SEARCH_API_KEY=

# 应用配置
DEBUG=true
HOST=127.0.0.1
PORT=8000

# AI模型配置（默认 gpt-5-mini，可被 .env 覆盖）
DEFAULT_MODEL=gpt-5-mini
PLAN_GENERATION_MODEL=gpt-5-mini
CONVERSATION_MODEL=gpt-5-mini
EXTERNAL_INFO_MODEL=gpt-5-mini
EXTERNAL_RESPONSES_MODEL=gpt-5-mini
QUESTION_MODEL=gpt-5-mini
HISTORY_MODEL=gpt-5-mini
DYNAMIC_QUESTIONING_MODEL=gpt-5-mini

# Responses API 推理强度（默认 low，可按模块覆盖）
DEFAULT_REASONING_EFFORT=low
CONVERSATION_REASONING_EFFORT=low
QUESTION_REASONING_EFFORT=low
HISTORY_REASONING_EFFORT=low
DYNAMIC_QUESTIONING_REASONING_EFFORT=low
PLAN_GENERATION_REASONING_EFFORT=low
EXTERNAL_INFO_REASONING_EFFORT=low
EXTERNAL_RESPONSES_REASONING_EFFORT=low
```

## 配置说明

### 模型配置
- **DEFAULT_MODEL**: 默认使用的模型
- **PLAN_GENERATION_MODEL**: 计划生成专用模型
- **CONVERSATION_MODEL**: 对话管理模型
- **EXTERNAL_INFO_MODEL**: 外部信息处理模型
- **EXTERNAL_RESPONSES_MODEL**: Responses API 联网检索模型
- **QUESTION_MODEL**: 问题生成模型
- **HISTORY_MODEL**: 历史分析模型
- **DYNAMIC_QUESTIONING_MODEL**: 动态提问模型

### Responses API 推理强度
- `DEFAULT_REASONING_EFFORT`: 默认推理强度（low/medium/high）
- 其余模块同名变量用于覆盖默认值

## Responses API 调用示例

所有调用均采用：

```python
client.responses.create(
    model=settings.conversation_model,
    instructions=Prompts.CUSTOMER_MANAGER,
    input=prompt,
    reasoning={"effort": settings.conversation_reasoning_effort or settings.default_reasoning_effort}
)
```

## 注意事项
1. 确保`.env`文件在项目根目录
2. 不要将`.env`文件提交到版本控制系统
3. 修改配置后需要重启应用才能生效
4. 若未设置模块级 reasoning，将回退到 `DEFAULT_REASONING_EFFORT`
