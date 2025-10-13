# Account Plan Agent

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.100+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

An AI-powered customer account planning management system using Streamlit frontend and FastAPI backend, automatically generating strategic customer plans through AI.

## 🎯 Product Goals

- Automatically generate strategic customer plans (Strategic Account Plan)
- Combine external public information (company profiles, news updates) and internal information (cooperation records, issues, plans)
- Output structured, traceable strategic documents
- Reduce user Account Plan generation time by more than 50%

## 🛠️ Features

### 1. External Information Collection
- Automatically search company basic information (website, profile, industry, size)
- Get news from the last 6 months and generate summaries
- Market trend analysis and competitive landscape

### 2. Internal Information Collection
- Conversational Q&A system
- Intelligent question generation and follow-up questions
- Structured data extraction
- Historical information reuse and pre-filling

### 3. Strategic Plan Generation
- Template-based structured output
- AI intelligent content generation
- Multi-format export (Markdown, Word, PPT)
- Version control and change logs

### 4. Historical Information Management
- Complete interaction history records
- Intelligent relevance analysis
- Data change detection
- Automatic archiving management

### 5. Dynamic Questioning System
- Context-based question generation
- Question flow management
- Customizable question templates
- Intelligent priority sorting

### 6. User Permission Management
- Multi-user support
- Administrator permission control
- Account information management
- Country information management

## 🚀 Quick Start

### Requirements

- **Python**: 3.8 - 3.11 (recommended 3.9 or 3.10)
  - Python 3.8: Minimum version, all features supported
  - Python 3.9-3.10: ⭐ **Recommended** for best compatibility
  - Python 3.11: Supported
  - Python 3.12+: ❌ **Not supported** - some dependencies require compilation and are not yet compatible
- **OpenAI API key**: Required for AI features

### Installation Steps

1. **Clone the project**
```bash
git clone https://github.com/YOUR_USERNAME/account-plan-agent-english.git
cd account-plan-agent-english
```

2. **Install dependencies**

**Option 1: Standard Installation (Recommended)**
```bash
pip install -r requirements.txt
```

**Option 2: Simplified Installation (if you encounter compilation issues)**
```bash
pip install -r requirements-simple.txt
```

**Option 3: Development Installation (includes testing tools)**
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

**Note**: 
- `requirements.txt` - Full production dependencies with version ranges
- `requirements-simple.txt` - Fixed versions, use if compilation issues occur
- `requirements-dev.txt` - Additional development tools (pytest, black, etc.)

3. **Configure environment variables**
Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
```

4. **Initialize database**
```bash
python init_database.py
```

5. **Start services**
```bash
# Terminal 1 - Start backend
python main.py

# Terminal 2 - Start frontend
streamlit run app.py
```

6. **Access application**
- Web interface: http://localhost:8501
- API documentation: http://localhost:8000/docs

## 🔐 Default Login Information

- Username: admin
- Password: admin

## 📖 User Guide

### 1. Create Account
1. Select "Account Management" in the web interface
2. Fill in company basic information
3. Click "Create Account"

### 2. Collect Information
1. Select "Information Collection" page
2. Click "Collect Company Information" to get external information
3. Answer core questions to collect internal information

### 3. Generate Plan
1. Select "Plan Generation" page
2. Enter plan title
3. Click "Generate Plan"

### 4. View History
1. Select "History View" page
2. View complete interaction history
3. Analyze data change trends

## 🏗️ Project Structure

```
├── main.py                 # FastAPI backend
├── app.py                  # Streamlit application entry
├── streamlit_app.py        # Frontend interface
├── login_page.py           # Login page
├── models.py               # Data models
├── schemas.py              # Pydantic models
├── config.py               # Configuration management
├── auth.py                 # Authentication module
├── conversation_manager.py # Conversation management
├── question_manager.py     # Question management
├── history_manager.py      # History management
├── external_info.py        # External information collection
├── plan_generator.py       # Plan generation
├── dynamic_questioning.py  # Dynamic questioning
├── prompts.py              # Prompt management
├── requirements.txt        # Dependencies
└── README.md              # Project documentation
```

## 🔧 API Endpoints

### Account Management
- `POST /accounts/` - Create account
- `GET /accounts/` - Get account list
- `GET /accounts/{account_id}` - Get account details
- `PUT /accounts/{account_id}` - Update account information
- `DELETE /accounts/{account_id}` - Delete account

### External Information
- `POST /accounts/{account_id}/external-info` - Collect external information
- `GET /accounts/{account_id}/external-info` - Get external information

### Q&A Interactions
- `POST /accounts/{account_id}/interactions` - Create interaction record
- `GET /accounts/{account_id}/interactions` - Get interaction history
- `POST /accounts/{account_id}/conversations/start` - Start conversation

### Plan Generation
- `POST /accounts/{account_id}/plans` - Generate plan
- `GET /accounts/{account_id}/plans` - Get plan list
- `GET /plans/{plan_id}` - Get plan details
- `PUT /plans/{plan_id}` - Update plan content
- `DELETE /plans/{plan_id}` - Delete plan

### Customer Profile
- `POST /accounts/{account_id}/generate-customer-profile` - Generate customer profile
- `POST /accounts/{account_id}/save-customer-profile` - Save customer profile
- `GET /accounts/{account_id}/customer-profile` - Get customer profile

### Country Management
- `GET /countries/` - Get country list
- `POST /countries/` - Add country
- `DELETE /countries/` - Delete country

### User Authentication
- `POST /auth/login` - User login
- `POST /auth/change-password` - Change password
- `POST /auth/create-user` - Create user
- `GET /auth/me` - Get current user information

## 🛡️ Security Considerations

- API key secure storage
- JWT token authentication
- User permission control
- Data access permission control
- Sensitive information desensitization
- Regular data backup

## 📊 Data Models

### Core Entities
- **Account**: Customer account
- **AccountPlan**: Customer plan
- **Interaction**: Interaction record
- **QuestionTemplate**: Question template
- **ExternalInfo**: External information
- **User**: User
- **Country**: Country

### Relationship Design
- One account can have multiple plans
- One account can have multiple interaction records
- One plan can be associated with multiple interaction records
- Question templates support derived questions
- Users can have multiple accounts (administrators can manage all accounts)

## 🧪 Testing

```bash
# Run API tests
pytest tests/

# Run integration tests
pytest tests/integration/
```

## 📝 Development Roadmap

### Completed Features
- [x] Basic architecture setup
- [x] External information collection
- [x] Internal information collection
- [x] Plan generation
- [x] History management
- [x] User authentication system
- [x] Country management
- [x] Customer profile generation
- [x] Account management

### Planned Features
- [ ] More external data sources
- [ ] Advanced analysis features
- [ ] Mobile support
- [ ] Team collaboration features
- [ ] Multi-tenant support
- [ ] Advanced permission management
- [ ] Enterprise integration
- [ ] Advanced reporting features

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

## 📄 License

MIT License

## 📞 Support

If you have questions or suggestions, please contact us through:

- Create an Issue
- Send an email
- Online documentation

---

**Account Plan Agent** - Make customer plan generation smarter and more efficient!