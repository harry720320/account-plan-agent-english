"""
Main API Interface
Provides RESTful API services
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uvicorn
import json
from datetime import datetime

# Authentication-related data models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False

from database import get_db, create_tables
from models import Account, AccountPlan, Interaction, QuestionTemplate, ExternalInfo, User, Country
from external_info import ExternalInfoCollector
from question_manager import QuestionManager
from plan_generator import PlanGenerator
from history_manager import HistoryManager
from dynamic_questioning import DynamicQuestioning
from config import settings
from auth import authenticate_user, create_access_token, get_current_user, hash_password, init_admin_user
from schemas import (
    AccountCreate, AccountResponse, InteractionCreate, InteractionResponse,
    PlanCreate, PlanResponse, ExternalInfoRequest, QuestionResponse
)
from conversation_manager import ConversationManager
from prompts import Prompts

# Create FastAPI application
app = FastAPI(
    title="Strategic Account Plan AI Agent",
    description="System for automatically generating strategic customer plans through AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
external_collector = ExternalInfoCollector()
question_manager = QuestionManager()
plan_generator = PlanGenerator()
history_manager = HistoryManager()
dynamic_questioning = DynamicQuestioning()
conversation_manager = ConversationManager()

# AuthenticationDependency
async def get_current_user_dependency(request: Request, db: Session = Depends(get_db)):
    """Get current user dependency"""
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No valid authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = token.split(" ")[1]
    user = get_current_user(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has been disabled",
        )
    
    return user

# CreateDataLibraryTable
create_tables()

# InitializeQuestion Templates
@app.on_event("startup")
async def startup_event():
    """Initialize when application starts"""
    # Initialize administrator user
    db = next(get_db())
    try:
        init_admin_user(db)
        print("✅ Administrator user initialization complete")
    except Exception as e:
        print(f"❌ Administrator user initialization failed: {e}")
    finally:
        db.close()

# Authentication related APIs
@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """User login"""
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin,
            "is_active": user.is_active
        }
    }

@app.post("/auth/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """ModifyPassword"""
    # ValidateOldPassword
    if not authenticate_user(db, current_user.username, request.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OldPasswordIncorrect"
        )
    
    # UpdatePassword
    current_user.password_hash = hash_password(request.new_password)
    db.commit()
    
    return {"message": "PasswordModifySuccess"}

@app.post("/auth/create-user")
async def create_user(
    request: CreateUserRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Create new user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users"
        )
    
    # CheckUsernameIsNoAlready exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UsernameAlready exists"
        )
    
    # Create new user
    new_user = User(
        username=request.username,
        password_hash=hash_password(request.password),
        is_admin=request.is_admin,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    
    return {"message": f"User {request.username} created successfully"}

@app.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user_dependency)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat()
    }

@app.get("/auth/users")
async def get_users(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view user list"
        )
    
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]

# Root path
@app.get("/")
async def root():
    return {"message": "Strategic Account Plan AI Agent API", "version": "1.0.0"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# Account management APIs
@app.post("/accounts/", response_model=AccountResponse)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Create new account"""
    try:
        # Check if account already exists
        existing_account = db.query(Account).filter(
            Account.company_name == account_data.company_name
        ).first()
        
        if existing_account:
            raise HTTPException(
                status_code=400,
                detail=f"Account '{account_data.company_name}' already exists"
            )
        
        # Create new account
        account = Account(
            company_name=account_data.company_name,
            industry=account_data.industry,
            company_size=account_data.company_size,
            website=account_data.website,
            country=account_data.country,
            description=account_data.description
        )
        
        db.add(account)
        db.commit()
        db.refresh(account)
        
        return AccountResponse(
            id=account.id,
            company_name=account.company_name,
            industry=account.industry,
            company_size=account.company_size,
            website=account.website,
            country=account.country,
            description=account.description,
            created_at=account.created_at,
            updated_at=account.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/")
async def list_accounts(
    skip: int = 0,
    limit: int = 100,
    country: Optional[str] = None,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get account list"""
    try:
        query = db.query(Account)
        
        # If country is specified, filter
        if country and country != "All Countries":
            query = query.filter(Account.country == country)
        
        accounts = query.offset(skip).limit(limit).all()
        
        return {
            "accounts": [
                {
                    "id": account.id,
                    "company_name": account.company_name,
                    "industry": account.industry,
                    "company_size": account.company_size,
                    "website": account.website,
                    "country": account.country,
                    "description": account.description,
                    "created_at": account.created_at.isoformat(),
                    "updated_at": account.updated_at.isoformat()
                }
                for account in accounts
            ],
            "total": len(accounts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/countries/")
async def get_countries(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get all country list"""
    try:
        # Get all active countries from country table
        countries = db.query(Country).filter(Country.is_active == True).all()
        country_list = [country.name for country in countries]
        country_list.sort()
        return {"countries": country_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/countries/")
async def add_country(
    request: dict,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Add new country (admin only)"""
    try:
        # Check if user is admin
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Only administrators can manage countries")
        
        country_name = request.get("country_name", "").strip()
        if not country_name:
            raise HTTPException(status_code=400, detail="Country name cannot be empty")
        
        # CheckCountryIsNoAlready exists
        existing_country = db.query(Country).filter(Country.name == country_name).first()
        if existing_country:
            if existing_country.is_active:
                raise HTTPException(status_code=400, detail="CountryAlready exists")
            else:
                # If country exists but is disabled, reactivate it
                existing_country.is_active = True
                existing_country.updated_at = datetime.utcnow()
                db.commit()
                return {
                    "message": f"Country '{country_name}' has been reactivated",
                    "country_name": country_name
                }
        
        # CreateNewCountryRecord
        new_country = Country(
            name=country_name,
            is_active=True
        )
        db.add(new_country)
        db.commit()
        
        return {
            "message": f"Country '{country_name}' has been added to the optional list",
            "country_name": country_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/countries/")
async def delete_country(
    country_name: str,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Delete country (admin only)"""
    try:
        # Check if user is admin
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Only administrators can manage countries")
        
        if not country_name:
            raise HTTPException(status_code=400, detail="Country name cannot be empty")
        
        # Check if any accounts are using this country
        accounts_using_country = db.query(Account).filter(Account.country == country_name).count()
        
        if accounts_using_country > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete country '{country_name}', {accounts_using_country} accounts are currently using this country"
            )
        
        # Soft delete country (set to inactive state)
        country = db.query(Country).filter(Country.name == country_name).first()
        if country:
            country.is_active = False
            country.updated_at = datetime.utcnow()
            db.commit()
        
        return {
            "message": f"Country '{country_name}' has been removed from the optional list",
            "country_name": country_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/{account_id}")
async def get_account(account_id: int, db: Session = Depends(get_db)):
    """Get account details"""
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account does not exist")
        
        return {
            "id": account.id,
            "company_name": account.company_name,
            "industry": account.industry,
            "company_size": account.company_size,
            "website": account.website,
            "country": account.country,
            "description": account.description,
            "created_at": account.created_at.isoformat(),
            "updated_at": account.updated_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/accounts/{account_id}")
async def update_account(
    account_id: int,
    request: dict,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Update account information (admin only)"""
    try:
        # Check if user is admin
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Only administrators can modify account information")
        
        # Find account
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account does not exist")
        
        # Update account information
        if "company_name" in request:
            # Check if company name conflicts with other accounts
            existing_account = db.query(Account).filter(
                Account.company_name == request["company_name"],
                Account.id != account_id
            ).first()
            if existing_account:
                raise HTTPException(status_code=400, detail="Company NameAlready exists")
            account.company_name = request["company_name"]
        
        if "industry" in request:
            account.industry = request["industry"]
        if "company_size" in request:
            account.company_size = request["company_size"]
        if "website" in request:
            account.website = request["website"]
        if "country" in request:
            account.country = request["country"]
        if "description" in request:
            account.description = request["description"]
        
        # Update modification time
        account.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(account)
        
        return {
            "message": "Account information updated successfully",
            "account": {
                "id": account.id,
                "company_name": account.company_name,
                "industry": account.industry,
                "company_size": account.company_size,
                "website": account.website,
                "country": account.country,
                "description": account.description,
                "created_at": account.created_at.isoformat(),
                "updated_at": account.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/accounts/{account_id}")
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Delete account (admin only)"""
    try:
        # Check if user is admin
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Only administrators can delete accounts")
        
        # Find account
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account does not exist")
        
        # Delete account (cascade delete all related data)
        db.delete(account)
        db.commit()
        
        return {"message": f"Account '{account.company_name}' and all related data have been deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# External InformationGetAPI
@app.post("/accounts/{account_id}/external-info")
async def collect_external_info(
    account_id: int,
    request: ExternalInfoRequest,
    db: Session = Depends(get_db)
):
    """Collect external information"""
    try:
        # Check if account exists
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account does not exist")
        
        info_type = request.info_type
        results = {}
        
        if info_type in ["all", "company_profile"]:
            # Get company basic information
            company_profile = await external_collector.get_company_profile(account.company_name)
            results["company_profile"] = company_profile
            
            # Save to database
            await history_manager.save_external_info(
                db, account_id, "company_profile", company_profile
            )
        
        if info_type in ["all", "news"]:
            # Get news information
            news_snapshot = await external_collector.get_news_snapshot(account.company_name)
            results["news_snapshot"] = news_snapshot
            
            # Save to database
            await history_manager.save_external_info(
                db, account_id, "news", news_snapshot
            )
        
        if info_type in ["all", "market_info"]:
            # Get market information
            market_info = await external_collector.get_market_info(
                account.company_name, account.industry
            )
            results["market_info"] = market_info
            
            # Save to database
            await history_manager.save_external_info(
                db, account_id, "market_info", market_info
            )
        
        return {
            "account_id": account_id,
            "info_type": info_type,
            "results": results,
            "message": "ExternalInformation CollectionComplete",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/{account_id}/external-info")
async def get_external_info(
    account_id: int,
    info_type: str = "all",  # all, company_profile, news, market_info
    db: Session = Depends(get_db)
):
    """GetExternal Information"""
    try:
        # Check if account exists
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account does not exist")
        
        # GetExternal Information
        external_info = await history_manager.get_external_info(db, account_id)
        
        if info_type == "all":
            return {
                "account_id": account_id,
                "company_name": account.company_name,
                "external_info": external_info,
                "message": "External InformationGetSuccess"
            }
        else:
            specific_info = external_info.get(info_type, {})
            return {
                "account_id": account_id,
                "company_name": account.company_name,
                "info_type": info_type,
                "data": specific_info,
                "message": f"{info_type}InfoGetSuccess"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# External InformationUpdate/SaveAPI（EditSave）
@app.put("/accounts/{account_id}/external-info")
async def update_external_info(
    account_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update/Save external information (supports edit and save)
    Request body example: {"info_type": "company_profile", "content": {...}, "source_url": "..."}
    """
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account does not exist")

        info_type = payload.get("info_type")
        content = payload.get("content")
        source_url = payload.get("source_url")
        if not info_type or content is None:
            raise HTTPException(status_code=400, detail="Missing info_type or content")

        ext_id = await history_manager.upsert_external_info(db, account_id, info_type, content, source_url)
        if not ext_id:
            raise HTTPException(status_code=500, detail="SaveFailure")

        return {"success": True, "id": ext_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# IssueManageAPI
@app.get("/questions/core")
async def get_core_questions(db: Session = Depends(get_db)):
    """Get core question list"""
    try:
        questions = await question_manager.get_core_questions(db)
        return {"questions": questions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/questions/initialize")
async def initialize_questions(db: Session = Depends(get_db)):
    """InitializeQuestion Templates"""
    try:
        await question_manager.initialize_questions(db)
        return {"message": "Question TemplatesInitializeComplete"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/questions/")
async def create_question(
    request: dict,
    db: Session = Depends(get_db)
):
    """CreateNewIssue"""
    try:
        question_text = request.get("question_text")
        category = request.get("category")
        description = request.get("description")
        
        if not question_text or not category:
            raise HTTPException(status_code=400, detail="Question content and category cannot be empty")
        
        # CreateIssueRecord
        question = QuestionTemplate(
            question_text=question_text,
            category=category,
            description=description,
            is_core=True
        )
        
        db.add(question)
        db.commit()
        db.refresh(question)
        
        return {
            "id": question.id,
            "question_text": question.question_text,
            "category": question.category,
            "description": question.description,
            "is_core": question.is_core,
            "created_at": question.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/questions/{question_id}")
async def update_question(
    question_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """UpdateIssue"""
    try:
        question = db.query(QuestionTemplate).filter(QuestionTemplate.id == question_id).first()
        
        if not question:
            raise HTTPException(status_code=404, detail="IssueNot Exist")
        
        # UpdateField
        if "question_text" in request:
            question.question_text = request["question_text"]
        if "category" in request:
            question.category = request["category"]
        if "description" in request:
            question.description = request["description"]
        
        db.commit()
        db.refresh(question)
        
        return {
            "id": question.id,
            "question_text": question.question_text,
            "category": question.category,
            "description": question.description,
            "is_core": question.is_core,
            "updated_at": question.updated_at.isoformat() if question.updated_at else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    """DeleteIssue"""
    try:
        question = db.query(QuestionTemplate).filter(QuestionTemplate.id == question_id).first()
        
        if not question:
            raise HTTPException(status_code=404, detail="IssueNot Exist")
        
        db.delete(question)
        db.commit()
        
        return {"message": "IssueDeleteSuccess"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/accounts/{account_id}/generate-customer-profile")
async def generate_customer_profile(
    account_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """GenerateCustomer Profile"""
    try:
        # Collect all information for the account
        external_info = request.get("external_info", {})
        internal_info = request.get("internal_info", {})
        
        # Build input data and enhance prompt
        external_summary = ""
        internal_summary = ""
        
        # HandleExternal InformationAbstract
        if external_info:
            for info_type, content in external_info.items():
                external_summary += f"\n### {info_type}:\n"
                if isinstance(content, dict):
                    for key, value in content.items():
                        value_str = str(value)
                        if len(value_str) > 100:
                            external_summary += f"- {key}: {value_str[:100]}...\n"
                        else:
                            external_summary += f"- {key}: {value}\n"
                else:
                    content_str = str(content)
                    if len(content_str) > 200:
                        external_summary += f"- {content_str[:200]}...\n"
                    else:
                        external_summary += f"- {content}\n"
        else:
            external_summary = "No external information collected"
            
        # HandleInternal InformationAbstract
        if internal_info:
            for key, value in internal_info.items():
                value_str = str(value)
                if len(value_str) > 100:
                    internal_summary += f"- {key}: {value_str[:100]}...\n"
                else:
                    internal_summary += f"- {key}: {value}\n"
        else:
            internal_summary = "No internal information collected"
        
        profile_data = f"""
        Based on the following collected information, generate detailed customer profile analysis:
        
        ## External InformationAbstract：
        {external_summary}
        
        ## Internal InformationAbstract：
        {internal_summary}
        
        CompleteData：
        ### External Information raw data:
        {json.dumps(external_info, ensure_ascii=False, indent=2)}
        
        ### Internal Information raw data:
        {json.dumps(internal_info, ensure_ascii=False, indent=2)}
        """
        
        # Directly call AI to generate customer profile
        import openai
        from config import settings
        
        # Extract first line for preview (avoid backslash in f-string)
        newline = '\n'
        external_preview = external_summary.partition(newline)[0][:100]
        internal_preview = internal_summary.partition(newline)[0][:100]
        
        analysis_prompt = f"""
        You are a professional customer analysis expert. Please generate a detailed customer profile analysis report based on the following truly collected customer data information.

        Data source and completeness check:
        - External Information ({len(external_info)} items): {external_preview}...
        - Internal Information ({len(internal_info)} items): {internal_preview}...
        
        Please use the following content as analysis basis:
        
        {profile_data}
        
        The generated structured analysis report must include these key sections and must be based on the actual collected data above:
        
        1. **Company Basic Overview**: Based on company basic information and industry information in External Information
        2. **Business Characteristics and Scale**: Combined with financial, scale, and operational data
        3. **Technical Requirements and Preferences**: Based on technical information in cooperation records and Q&A
        4. **Decision Characteristics and Process**: Decision process information found in Q&A records
        5. **Cooperation History and Experience**: Directly reference historical cooperation Q&A
        6. **Future Development Requirements**: Based on Future Plans and pain points in Q&A records for promotion suggestions
        7. **Key Pain Points and Challenges**: Summarize specific difficulties mentioned in issue records
        8. **Decision Team Structure**: Include Key Contacts information mentioned in conversations
        9. **Budget Cycle and Investment**: Reference funding and cycle information in cooperation Q&A
        10. **Cooperation Value Points**: Extract value points from Cooperation History and Q&A analysis
        
        Analysis requirements (strictly follow actual situation):
        - ✅ Conduct specific situation analysis and inference based on provided data
        - ✅ Must reference specific conversation content, hardware information or enterprise data
        - ✅ Use facts and data, not generic or hypothetical descriptions
        - ✅ Highlight unique characteristics found in the provided collected data
        - ✅ Do not fabricate or assume content not mentioned in the input data
        - ✅ If there is no data for a certain item, state it directly without making meaningless speculation
        """
        
        try:
            # Use OpenAI Chat Completions API for better performance
            openai_client = openai.OpenAI(api_key=settings.openai_api_key)
            response = openai_client.chat.completions.create(
                model=settings.conversation_model,
                messages=[
                    {"role": "system", "content": Prompts.CUSTOMER_ANALYSIS_EXPERT},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.0,
                max_tokens=4000
            )
            
            profile_content = response.choices[0].message.content
            profile = f"# Customer ProfileAnalysisReport\n\n{profile_content}"
            
        except Exception as e:
            # Fallback: Generate basic customer profile template
            import traceback
            print(f"AIGenerateCustomer ProfileFailure: {e}")
            
            # Create simple profile based on actual data
            company_name = ""
            industry = ""
            if external_info and "company_profile" in external_info:
                comp_info = external_info["company_profile"]
                company_name = comp_info.get("company_name", "Unknown company")
                industry = comp_info.get("industry", "UnknownIndustry")
            
            profile = f"""# Customer ProfileAnalysisReport
            
## Company Basic Overview
- Company Name: {company_name}
- Industry: {industry}
- Company Overview: Based on collected External Information

## Business Characteristics Analysis
- Cooperation History: {internal_info.get('Cooperation History', 'See Conversation Records') if internal_info else 'To be collected'}
- Products & Services: {internal_info.get('Products & Services', 'To be supplemented') if internal_info else 'To be collected'}
- Key Pain Points: {internal_info.get('Challenges & Issues', 'To be understood') if internal_info else 'To be collected'}

## Key Decision Makers
- Contact Information: {internal_info.get('Key Contacts', 'To be collected') if internal_info else 'To be collected'}

## Next Steps
- Future Requirements: {internal_info.get('Future Plans', 'To be planned') if internal_info else 'To be understood'}
- Resource Support: {internal_info.get('Resource Needs', 'To be assessed') if internal_info else 'To be collected'}

**Note:** This profile is a quick generation version. For more detailed analysis, please manually add more information.
"""
        
        return {"profile": profile}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/accounts/{account_id}/save-customer-profile")
async def save_customer_profile(
    account_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """SaveCustomer Profile"""
    try:
        customer_profile = request.get("customer_profile", "")
        
        # Get account record
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account does not exist")
        
        # Ensure each account has only one Customer Profile: find existing record
        existing_profile = db.query(ExternalInfo).filter(
            ExternalInfo.account_id == account_id,
            ExternalInfo.info_type == "customer_profile"
        ).first()
        
        if existing_profile:
            # Update existing unique Customer Profile record
            existing_profile.content = json.dumps({"profile": customer_profile}, ensure_ascii=False)
            existing_profile.updated_at = datetime.utcnow()
            profile_id = existing_profile.id
            action = "Update"
        else:
            # Create new Customer Profile record (only one per account allowed)
            external_info = ExternalInfo(
                account_id=account_id,
                info_type="customer_profile",
                content=json.dumps({"profile": customer_profile}, ensure_ascii=False)
            )
            db.add(external_info)
            db.flush()  # Execute first to get ID
            profile_id = external_info.id
            action = "Create"
        
        db.commit()
        
        return {
            "message": "Customer ProfileSaveSuccess",
            "profile_id": profile_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/{account_id}/customer-profile")
async def get_customer_profile(
    account_id: int,
    db: Session = Depends(get_db)
):
    """GetCustomer Profile"""
    try:
        # Check if account exists
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account does not exist")
        
        # Find unique customer profile from External Information (only one per account allowed)
        external_info = db.query(ExternalInfo).filter(
            ExternalInfo.account_id == account_id,
            ExternalInfo.info_type == "customer_profile"
        ).first()
        
        if external_info:
            profile_content = json.loads(external_info.content)
            return {
                "exists": True,
                "profile": profile_content.get("profile", ""),
                "created_at": external_info.created_at.isoformat() if external_info.created_at else None,
                "updated_at": external_info.updated_at.isoformat() if external_info.updated_at else None,
                "profile_id": external_info.id
            }
        else:
            return {
                "exists": False,
                "profile": "",
                "message": "No saved Customer Profile found"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Q&A interaction APIs
@app.post("/accounts/{account_id}/interactions")
async def create_interaction(
    account_id: int,
    request: InteractionCreate,
    db: Session = Depends(get_db)
):
    """Create interaction record"""
    try:
        # Check if account exists
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account does not exist")
        
        # Extract parameters from request
        question = request.question
        answer = request.answer
        plan_id = request.plan_id
        
        # Extract structured data
        structured_data = await question_manager.extract_structured_data(
            question, answer, "general"
        )
        
        # Save interaction record
        interaction = await question_manager.save_interaction(
            db, account_id, plan_id, question, answer, structured_data
        )
        
        return {
            "interaction_id": interaction.id,
            "account_id": account_id,
            "question": question,
            "answer": answer,
            "structured_data": structured_data,
            "message": "Interaction record created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/{account_id}/interactions")
async def get_interactions(
    account_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get interaction records"""
    try:
        interactions = db.query(Interaction).filter(
            Interaction.account_id == account_id
        ).offset(skip).limit(limit).all()
        
        return {
            "interactions": [
                {
                    "id": i.id,
                    "interaction_type": i.interaction_type,
                    "question": i.question,
                    "answer": i.answer,
                    "structured_data": i.structured_data,
                    "created_at": i.created_at.isoformat()
                }
                for i in interactions
            ],
            "total": len(interactions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dynamic questioning APIs
@app.get("/accounts/{account_id}/questions/contextual")
async def get_contextual_questions(
    account_id: int,
    current_question: str = None,
    context: Dict[str, Any] = None,
    db: Session = Depends(get_db)
):
    """Get context-related questions"""
    try:
        questions = await dynamic_questioning.generate_contextual_questions(
            db, account_id, current_question, context
        )
        return questions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/{account_id}/questions/flow")
async def get_question_flow(
    account_id: int,
    flow_type: str = "comprehensive",
    db: Session = Depends(get_db)
):
    """Get question progress"""
    try:
        flow = await dynamic_questioning.generate_question_flow(
            db, account_id, flow_type
        )
        return flow
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Plan GenerationAPI
@app.post("/accounts/{account_id}/plans")
async def create_plan(
    account_id: int,
    request: PlanCreate,
    db: Session = Depends(get_db)
):
    """Create strategic customer plan"""
    try:
        # Check if account exists
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account does not exist")
        
        # Generate Plan
        plan_result = await plan_generator.generate_plan(
            db, account_id, request.title, request.description
        )
        
        if "error" in plan_result:
            raise HTTPException(status_code=500, detail=plan_result["error"])
        
        return plan_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/{account_id}/plans")
async def list_plans(
    account_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get plan list"""
    try:
        plans = db.query(AccountPlan).filter(
            AccountPlan.account_id == account_id
        ).offset(skip).limit(limit).all()
        
        return {
            "plans": [
                {
                    "id": plan.id,
                    "title": plan.title,
                    "status": plan.status,
                    "created_at": plan.created_at.isoformat(),
                    "updated_at": plan.updated_at.isoformat()
                }
                for plan in plans
            ],
            "total": len(plans)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plans/{plan_id}")
async def get_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get plan details"""
    try:
        plan = db.query(AccountPlan).filter(AccountPlan.id == plan_id).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan does not exist")
        
        return {
            "id": plan.id,
            "account_id": plan.account_id,
            "title": plan.title,
            "content": plan.content,
            "status": plan.status,
            "created_at": plan.created_at.isoformat(),
            "updated_at": plan.updated_at.isoformat(),
            "change_log": plan.change_log
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/plans/{plan_id}")
async def update_plan(
    plan_id: int,
    updates: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update plan"""
    try:
        result = await plan_generator.update_plan(db, plan_id, updates)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """Delete plan"""
    try:
        # Find plan
        plan = db.query(AccountPlan).filter(AccountPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan does not exist")
        
        # Delete plan
        db.delete(plan)
        db.commit()
        
        return {"message": "Plan deleted successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Historical information APIs
@app.get("/accounts/{account_id}/history")
async def get_account_history(
    account_id: int,
    include_external: bool = True,
    db: Session = Depends(get_db)
):
    """Get account historical information"""
    try:
        history = await history_manager.get_account_history(
            db, account_id, include_external
        )
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/{account_id}/history/relevant")
async def get_relevant_history(
    account_id: int,
    current_question: str,
    context: Dict[str, Any] = None,
    db: Session = Depends(get_db)
):
    """Get relevant historical information"""
    try:
        relevant = await history_manager.get_relevant_history(
            db, account_id, current_question, context
        )
        return relevant
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/{account_id}/history/prefill")
async def get_prefill_data(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Get prefill data"""
    try:
        prefill = await history_manager.prefill_questionnaire(db, account_id)
        return prefill
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Conversation management APIs
@app.post("/accounts/{account_id}/conversations/start")
async def start_conversation(
    account_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """Start Conversation"""
    try:
        # Check if account exists
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account does not exist")
        
        # Check if using simplified mode
        if request.get("simplified", False):
            # Simplified mode: directly return basic conversation structure, but include historical summary
            # Get historical summary
            previous_summary = await conversation_manager._get_question_summary(
                db, account_id, request.get("question")
            )
            
            conversation = {
                "conversation_id": f"conv_{account_id}_{int(datetime.now().timestamp())}",
                "account_id": account_id,
                "original_question": request.get("question"),
                "previous_summary": previous_summary,
                "messages": [
                    {"role": "assistant", "content": "Please answer this question in detail, and I will continue with in-depth questions based on your answer."}
                ],
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
            return conversation
        else:
            # Original logic
            conversation = await conversation_manager.start_conversation(
                db, account_id, request.get("question"), request.get("context")
            )
            
            if "error" in conversation:
                raise HTTPException(status_code=500, detail=conversation["error"])
            
            return conversation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/accounts/{account_id}/conversations/continue")
async def continue_conversation(
    account_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """Continue conversation"""
    try:
        conversation = request.get("conversation")
        user_message = request.get("user_message")
        
        if not conversation or not user_message:
            raise HTTPException(status_code=400, detail="Missing conversation or user message")
        
        # Continue conversation
        updated_conversation = await conversation_manager.continue_conversation(
            conversation, user_message
        )
        
        if "error" in updated_conversation:
            raise HTTPException(status_code=500, detail=updated_conversation["error"])
        
        return updated_conversation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/accounts/{account_id}/conversations/end")
async def end_conversation(
    account_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """End Conversation"""
    try:
        conversation = request.get("conversation")
        
        if not conversation:
            raise HTTPException(status_code=400, detail="Missing conversation data")
        
        # End Conversation
        result = await conversation_manager.end_conversation(db, conversation)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/accounts/{account_id}/conversations")
async def get_conversations(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Get conversation history"""
    try:
        conversations = await conversation_manager.get_conversation_history(db, account_id)
        return {"conversations": conversations}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Question progress APIs
@app.get("/accounts/{account_id}/progress")
async def get_question_progress(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Get question progress"""
    try:
        progress = await question_manager.get_question_progress(db, account_id)
        return progress
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optimized historical data APIs (directly query from database, no AI calls)
@app.get("/accounts/{account_id}/history/simple")
async def get_simple_history(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Get simplified historical data (directly query from database, no AI calls)"""
    try:
        # Directly query historical answers from database
        interactions = db.query(Interaction).filter(
            Interaction.account_id == account_id,
            Interaction.interaction_type.in_(["question", "conversation"]),
            Interaction.question.isnot(None),
            Interaction.answer.isnot(None)
        ).order_by(Interaction.created_at.desc()).all()
        
        # Organize data by question
        prefill_data = {}
        for interaction in interactions:
            if interaction.question not in prefill_data:  # Only take the latest answer
                prefill_data[interaction.question] = {
                    "answer": interaction.answer,
                    "structured_data": interaction.structured_data or {},
                    "last_updated": interaction.created_at.isoformat()
                }
        
        return {
            "prefill_data": prefill_data,
            "total_questions": len(prefill_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update historical summary APIs
@app.put("/accounts/{account_id}/history/summary")
async def update_history_summary(
    account_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """Update historical summary"""
    try:
        question = request.get("question")
        new_summary = request.get("summary")
        
        if not question or not new_summary:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        # Find historical record for this question
        interaction = db.query(Interaction).filter(
            Interaction.account_id == account_id,
            Interaction.question == question,
            Interaction.interaction_type == "conversation"
        ).order_by(Interaction.created_at.desc()).first()
        
        if not interaction:
            raise HTTPException(status_code=404, detail="Historical record not found")
        
        # UpdateSummary
        if interaction.structured_data:
            interaction.structured_data["summary"] = new_summary
        else:
            interaction.structured_data = {"summary": new_summary}
        
        db.commit()
        
        # ClearCache
        return {"message": "Historical summary updated", "summary": new_summary}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update historical answer APIs
@app.put("/accounts/{account_id}/interactions/update")
async def update_interaction_answer(
    account_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """Update historical answer"""
    try:
        question = request.get("question")
        new_answer = request.get("answer")
        structured_data = request.get("structured_data", {})
        
        if not question or not new_answer:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        # Find historical record for this question
        interaction = db.query(Interaction).filter(
            Interaction.account_id == account_id,
            Interaction.question == question,
            Interaction.interaction_type.in_(["question", "conversation"])
        ).order_by(Interaction.created_at.desc()).first()
        
        if not interaction:
            raise HTTPException(status_code=404, detail="Historical record not found")
        
        # Update answer and structured data
        interaction.answer = new_answer
        interaction.structured_data = structured_data
        
        db.commit()
        
        return {"message": "Historical answer updated", "answer": new_answer}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Start server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",  # Use 127.0.0.1 instead of 0.0.0.0
        port=settings.port,
        reload=settings.debug
    )
