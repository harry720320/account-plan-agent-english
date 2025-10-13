# 贡献指南

感谢您对 Account Plan Agent 项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 1. Fork 项目
1. 访问 [GitHub 仓库](https://github.com/yourusername/account-plan-agent-english)
2. 点击右上角的 "Fork" 按钮
3. 将项目克隆到您的本地环境

### 2. 创建功能分支
```bash
git checkout -b feature/AmazingFeature
```

### 3. 提交更改
```bash
git commit -m 'Add some AmazingFeature'
```

### 4. 推送到分支
```bash
git push origin feature/AmazingFeature
```

### 5. 创建 Pull Request
1. 在 GitHub 上打开您的 fork
2. 点击 "New Pull Request"
3. 填写详细的描述信息

## 代码规范

### Python 代码规范
- 遵循 PEP 8 代码规范
- 使用 4 个空格缩进
- 行长度不超过 88 字符
- 使用有意义的变量和函数名

### 文档字符串
```python
def example_function(param1: str, param2: int) -> bool:
    """
    示例函数的文档字符串
    
    Args:
        param1: 第一个参数描述
        param2: 第二个参数描述
        
    Returns:
        返回值描述
        
    Raises:
        ValueError: 当参数无效时抛出
    """
    pass
```

### 注释规范
- 为复杂的业务逻辑添加注释
- 解释"为什么"而不是"做什么"
- 保持注释的时效性

## 提交信息规范

### 格式
```
<类型>(<范围>): <描述>

[可选的正文]

[可选的脚注]
```

### 类型
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 示例
```
feat(auth): 添加用户登录功能

- 实现 JWT 令牌认证
- 添加密码加密
- 创建登录页面

Closes #123
```

## 测试要求

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 运行测试并生成覆盖率报告
pytest --cov=src tests/
```

### 测试覆盖率
- 新功能需要至少 80% 的测试覆盖率
- 关键业务逻辑需要 100% 覆盖率

## 问题报告

### Bug 报告
使用 GitHub Issues 报告 bug，请包含：

1. **环境信息**
   - 操作系统
   - Python 版本
   - 依赖包版本

2. **重现步骤**
   - 详细的操作步骤
   - 预期结果
   - 实际结果

3. **错误信息**
   - 完整的错误堆栈
   - 日志信息

### 功能请求
1. 检查现有 Issues 是否已有类似请求
2. 详细描述功能需求
3. 说明使用场景和预期效果

## 开发环境设置

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/account-plan-agent-english.git
cd account-plan-agent-english
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

### 4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

### 5. 初始化数据库
```bash
python init_database.py
```

### 6. 运行测试
```bash
pytest
```

## 代码审查流程

### Pull Request 要求
1. **代码质量**
   - 通过所有测试
   - 符合代码规范
   - 添加必要的文档

2. **功能完整性**
   - 功能按预期工作
   - 处理边界情况
   - 添加错误处理

3. **向后兼容性**
   - 不破坏现有功能
   - 保持 API 兼容性

### 审查要点
- 代码逻辑正确性
- 性能影响
- 安全性考虑
- 可维护性
- 测试覆盖度

## 发布流程

### 版本号规范
遵循 [语义化版本](https://semver.org/lang/zh-CN/)：
- `MAJOR`: 不兼容的 API 修改
- `MINOR`: 向下兼容的功能性新增
- `PATCH`: 向下兼容的问题修正

### 发布步骤
1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 Release
4. 打标签

## 社区准则

### 行为准则
- 保持友善和尊重
- 欢迎不同观点
- 专注于对社区最有利的事情
- 对其他社区成员保持同理心

### 沟通渠道
- GitHub Issues: 问题讨论
- GitHub Discussions: 功能讨论
- Pull Request: 代码审查

## 许可证

通过贡献代码，您同意您的贡献将在 MIT 许可证下发布。

## 联系方式

如有问题，请通过以下方式联系：

- 创建 GitHub Issue
- 发送邮件到项目维护者
- 在 GitHub Discussions 中讨论

感谢您的贡献！🎉
