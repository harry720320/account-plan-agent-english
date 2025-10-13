# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-XX

### Added
- Complete customer account plan management system
- AI-driven customer information collection
- Intelligent customer profile generation
- Strategic plan development and management
- Multi-user permission management system
- Country information management
- Conversational Q&A system
- Historical information management and reuse
- Automatic external information retrieval
- Dynamic question generation system
- User authentication and authorization
- Admin features (account management, country management, user management)
- Customer profile generation and editing
- Plan content editing and saving
- Question template management
- External information collection (company profile, news, market information)
- Internal information collection (Q&A records)
- Customer profile AI analysis
- Strategic plan generation based on collected data
- Multi-turn conversation support with AI summaries
- OpenAI GPT-5 / o1 series model support
- Responses API integration for advanced AI reasoning

### Features
- **Account Management**: Create, view, edit, and delete customer accounts
- **Information Collection**: 
  - External: Company profiles, news, market information
  - Internal: Conversational Q&A with AI-guided questioning
- **AI Analysis**: Generate customer profiles based on collected data
- **Plan Generation**: Create strategic plans using all collected information
- **User Management**: Admin can manage users and permissions
- **Country Management**: Manage country lists for account categorization
- **Question Templates**: Customize and manage question templates for information gathering

### Technical
- FastAPI backend with RESTful API
- Streamlit frontend for user interface
- SQLite database for data persistence
- OpenAI API integration (GPT-5, o1-mini, o1-preview)
- SQLAlchemy ORM for database operations
- JWT-based authentication
- Salted password hashing for security
- Async/await support for AI operations
- Structured data extraction from conversations
- Markdown support for plan documents

### Fixed
- Admin password hashing now uses salted SHA-256 (matches auth.py implementation)
- F-string syntax errors with backslashes in expressions
- Parameter mismatches in conversation prompts:
  - `_generate_follow_up_question()` now correctly passes `previous_question`, `customer_response`, `category`
  - `_generate_conversation_summary()` now passes both `previous_summary` and `conversation_content`
  - `_generate_initial_question()` rewritten with inline prompt instead of non-existent template
- Market information display now handles both string lists and dict lists
- Plan generation now correctly uses all collected data:
  - Customer profile (AI-generated analysis)
  - External information (company profile, news, market data)
  - Internal information (all Q&A records organized by category)
- Prompt attribute name corrected from `STRATEGY_PLANNER` to `STRATEGIC_ACCOUNT_MANAGER`

### Security
- Salted password hashing (SHA-256 with random salt)
- JWT token-based authentication
- Session management
- User role-based access control (admin/regular users)

### Documentation
- Comprehensive README with setup instructions
- Database schema documentation
- Model configuration guide
- Prompts configuration documentation
- Project summary and architecture overview
- Contributing guidelines
- MIT License

### Dependencies
- Python 3.8-3.11 (recommended: 3.10.12)
- FastAPI 0.104.0+
- Streamlit 1.28.0+
- OpenAI 1.54.0+
- SQLAlchemy 2.0.23+
- Pydantic 2.5.0+
- PyJWT 2.8.0
- python-multipart 0.0.6+
- Jinja2 3.1.2+
- python-pptx 0.6.23

### Known Issues
- Python 3.12+ not supported due to dependency compilation issues
- Async operations may show harmless RuntimeError on Windows (overlapped operations)

### Internationalization
- Full English translation of UI, code comments, and documentation
- All user-facing text in English
- All code comments and docstrings in English

---

## Version History

### [1.0.0] - Initial Release
First stable release with complete functionality for customer account plan management using AI-driven insights.
