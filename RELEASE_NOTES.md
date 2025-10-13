# Account Plan Agent v1.0.0 - Initial Release

We're excited to announce the first stable release of **Account Plan Agent** - an AI-powered customer account planning and management system!

## 🎉 What is Account Plan Agent?

Account Plan Agent is a comprehensive system that helps businesses manage customer relationships and develop strategic account plans using AI-driven insights. It combines external data collection, internal knowledge gathering through conversational AI, and intelligent analysis to generate actionable strategic plans.

## ✨ Key Features

### 📊 Account Management
- Create and manage customer accounts
- Track company information (industry, size, website, description)
- Country-based categorization

### 🔍 Information Collection
- **External Information**: Automatically gather company profiles, news, and market intelligence
- **Internal Information**: AI-guided conversational Q&A to collect institutional knowledge
- Support for multiple information types and sources

### 🤖 AI-Powered Analysis
- **Customer Profile Generation**: AI analyzes all collected data to create comprehensive customer profiles
- **Strategic Plan Generation**: Automatically generate detailed strategic plans based on:
  - Customer profile analysis
  - External market data
  - Internal Q&A insights
  - Historical interaction records

### 💬 Conversational Intelligence
- Multi-turn conversations with AI
- Context-aware follow-up questions
- Automatic conversation summarization
- Historical context integration

### 👥 User Management
- User authentication with JWT tokens
- Role-based access control (admin/regular users)
- Secure password hashing with salt

### 🎯 Question Management
- Customizable question templates
- Six core categories: Cooperation History, Products & Services, Challenges, Key Contacts, Future Plans, Resource Needs
- Dynamic question generation based on responses

## 🚀 Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Database**: SQLite with SQLAlchemy ORM
- **AI**: OpenAI API (GPT-5, o1-mini, o1-preview)
- **Authentication**: JWT tokens
- **Document Format**: Markdown

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/account-plan-agent-english.git
cd account-plan-agent-english

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env and add your OpenAI API key

# Initialize database
python init_database.py

# Run the application
# Terminal 1: Start backend
python main.py

# Terminal 2: Start frontend
streamlit run app.py
```

## 📋 Requirements

- Python 3.8-3.11 (recommended: 3.10.12)
- OpenAI API key
- Modern web browser

**Note**: Python 3.12+ is not currently supported due to dependency compilation issues.

## 🔧 Configuration

The system supports extensive configuration through environment variables:

- **OpenAI Models**: Configure different models for various tasks (conversation, analysis, plan generation)
- **Reasoning Effort**: Adjust AI reasoning depth (low/medium/high)
- **Database**: SQLite by default, easily extensible
- **API Keys**: Secure configuration via environment variables

See `MODEL_CONFIG.md` for detailed configuration options.

## 📚 Documentation

- [README.md](README.md) - Complete setup and usage guide
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Database structure documentation
- [MODEL_CONFIG.md](MODEL_CONFIG.md) - AI model configuration guide
- [PROMPTS_CONFIG.md](PROMPTS_CONFIG.md) - Prompt templates reference
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) - Detailed change history

## 🐛 Bug Fixes in v1.0.0

This release includes fixes for:
- Password hashing implementation for admin users
- F-string syntax errors in plan generation
- Parameter mismatches in conversation prompts
- Market information type handling for dict/list data
- Plan generation now correctly utilizes all collected data
- Prompt attribute naming corrections

## 🙏 Acknowledgments

Built with:
- OpenAI API for AI capabilities
- FastAPI for robust backend
- Streamlit for rapid UI development
- SQLAlchemy for database management

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📞 Support

- GitHub Issues: [Report bugs or request features](https://github.com/yourusername/account-plan-agent-english/issues)
- Documentation: Check our comprehensive docs in the repository

## 🔮 What's Next?

We're planning for v1.1.0:
- Enhanced data export functionality
- Batch operations for accounts
- Advanced reporting and visualization
- API documentation improvements
- Docker containerization
- Automated testing suite

---

**Happy Planning!** 🎯

We hope Account Plan Agent helps you build stronger customer relationships and develop more effective strategic plans.

*Released on: [Date]*

