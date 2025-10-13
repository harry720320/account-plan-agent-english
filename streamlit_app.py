"""
Streamlit User Interface
Provides a friendly web interface for using the Strategic Account Plan AI Agent
"""
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Any
# import pandas as pd  # Temporarily remove pandas dependency

# API base URL
API_BASE_URL = "http://localhost:8000"

# Check login status
if "access_token" not in st.session_state or "user_info" not in st.session_state:
    st.error("Please login first")
    if st.button("🔐 Go to Login Page"):
        st.session_state.show_main_app = False
        st.rerun()
    st.stop()

# Initialize session state function
def init_session_state():
    """Initialize session state"""
    if "current_account_id" not in st.session_state:
        st.session_state.current_account_id = None
    if "current_plan_id" not in st.session_state:
        st.session_state.current_plan_id = None
    if "interactions" not in st.session_state:
        st.session_state.interactions = []
    if "prefill_data_cache" not in st.session_state:
        st.session_state.prefill_data_cache = {}

def get_cached_prefill_data(account_id: int) -> Dict:
    """Get cached historical data to avoid repeated API calls"""
    cache_key = f"prefill_{account_id}"
    if cache_key not in st.session_state.prefill_data_cache:
        with st.spinner("Loading historical data..."):
            history_result = make_api_request("GET", f"/accounts/{account_id}/history/simple")
            st.session_state.prefill_data_cache[cache_key] = history_result.get("prefill_data", {})
    return st.session_state.prefill_data_cache[cache_key]

def make_api_request(method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
    """Send API request"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        # Add authentication header
        headers = {}
        if "access_token" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}
        
        # CheckAuthenticationFailure
        if response.status_code == 401:
            st.error("Login expired, please login again")
            if st.button("🔐 Login Again"):
                st.switch_page("login_page.py")
            st.stop()
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API request failed: {response.status_code} - {response.text}"}
    
    except Exception as e:
        return {"error": f"Request error: {str(e)}"}

def show_chat_window(question_index: int, question: Dict[str, Any], account_id: int):
    """Display optimized chat window"""
    
    conversation_key = f"conversation_{question_index}"
    chat_window_key = f"show_chat_{question_index}"
    
    # If conversation does not exist, initialize
    if conversation_key not in st.session_state:
        st.session_state[conversation_key] = None
    
    # Start conversation button
    if st.session_state[conversation_key] is None:
        if st.button(f"🚀 Start Conversation", key=f"start_chat_{question_index}"):
            with st.spinner("Initializing conversation..."):
                conversation_data = {
                    "question": question["question_text"],
                    "context": {"category": question["category"]},
                    "simplified": True  # Use simplified mode, reduce AI calls
                }
                
                result = make_api_request(
                    "POST",
                    f"/accounts/{account_id}/conversations/start",
                    conversation_data
                )
                
                if "error" not in result:
                    st.session_state[conversation_key] = result
                    st.session_state[chat_window_key] = True
                    st.rerun()
                else:
                    st.error(f"Start ConversationFailure: {result['error']}")
    
    # Display conversation interface
    if st.session_state[conversation_key]:
        conversation = st.session_state[conversation_key]
        
        # Display historical summary (if available)
        if conversation.get("previous_summary"):
            st.markdown("#### 📋 Historical Summary")
            
            # Check if in edit mode
            edit_key = f"edit_summary_{question_index}"
            if edit_key not in st.session_state:
                st.session_state[edit_key] = False
            
            if st.session_state[edit_key]:
                # Edit mode
                edited_summary = st.text_area(
                    "Edit Historical Summary:",
                    value=conversation['previous_summary'],
                    height=150,
                    key=f"summary_edit_{question_index}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 SaveModify", key=f"save_summary_{question_index}"):
                        # SaveModify
                        update_data = {
                            "question": conversation['original_question'],
                            "summary": edited_summary
                        }
                        
                        result = make_api_request(
                            "PUT",
                            f"/accounts/{account_id}/history/summary",
                            update_data
                        )
                        
                        if "error" not in result:
                            st.success("✅ Historical summary updated!")
                            # Update historical summary in conversation
                            conversation['previous_summary'] = edited_summary
                            st.session_state[edit_key] = False
                            # ClearCache
                            cache_key = f"prefill_{account_id}"
                            if cache_key in st.session_state.prefill_data_cache:
                                del st.session_state.prefill_data_cache[cache_key]
                            st.rerun()
                        else:
                            st.error(f"SaveFailure: {result['error']}")
                
                with col2:
                    if st.button("❌ Cancel", key=f"cancel_summary_{question_index}"):
                        st.session_state[edit_key] = False
                        st.rerun()
            else:
                # Display mode
                st.info(conversation['previous_summary'])
                if st.button("✏️ EditSummary", key=f"edit_summary_btn_{question_index}"):
                    st.session_state[edit_key] = True
                    st.rerun()
        
        # Chat message display area
        st.markdown("#### 💭 Conversation Records")
        
        # Display conversation history
        messages = conversation.get("messages", [])
        for j, msg in enumerate(messages):
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="background-color: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right;">
                    <strong>👤 You:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #f5f5f5; padding: 10px; border-radius: 10px; margin: 5px 0;">
                    <strong>🤖 AI:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
        
        # User input area
        st.markdown("#### ✍️ Your Answer")
        
        # Use form to avoid page refresh
        with st.form(f"chat_form_{question_index}", clear_on_submit=True):
            user_input = st.text_area(
                "Please enter your answer...",
                height=100,
                key=f"chat_input_{question_index}",
                placeholder="Please answer the AI's question in detail..."
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                send_button = st.form_submit_button("💬 Send", type="primary")
            
            with col2:
                save_button = st.form_submit_button("💾 Save Conversation")
            
            with col3:
                close_button = st.form_submit_button("❌ Close Window")
            
            # HandleSendMessage
            if send_button and user_input:
                with st.spinner("AI is thinking..."):
                    continue_data = {
                        "conversation": conversation,
                        "user_message": user_input
                    }
                    
                    result = make_api_request(
                        "POST",
                        f"/accounts/{account_id}/conversations/continue",
                        continue_data
                    )
                    
                    if "error" not in result:
                        st.session_state[conversation_key] = result
                        # Only refresh current question, not affecting other questions
                        st.rerun()
                    else:
                        st.error(f"SendFailure: {result['error']}")
            
            # Handle save conversation
            if save_button:
                with st.spinner("Generating summary and saving..."):
                    save_data = {"conversation": conversation}
                    
                    result = make_api_request(
                        "POST",
                        f"/accounts/{account_id}/conversations/end",
                        save_data
                    )
                    
                    if "error" not in result:
                        st.success("✅ Conversation saved!")
                        st.markdown(f"**AI Generated Summary:** {result.get('summary', '')}")
                        
                        # Clear cache to ensure latest data is displayed on next load
                        cache_key = f"prefill_{account_id}"
                        if cache_key in st.session_state.prefill_data_cache:
                            del st.session_state.prefill_data_cache[cache_key]
                        
                        # Only clear current question's conversation state
                        st.session_state[conversation_key] = None
                        st.session_state[chat_window_key] = False
                        # Only refresh current question area
                        st.rerun()
                    else:
                        st.error(f"SaveFailure: {result['error']}")
            
            # Handle close window
            if close_button:
                st.session_state[chat_window_key] = False
                st.rerun()

def show_chat_status(question_index: int, question: Dict[str, Any]):
    """Display chat state (optimized version - reduce page refresh)"""
    conversation_key = f"conversation_{question_index}"
    
    if conversation_key in st.session_state and st.session_state[conversation_key]:
        conversation = st.session_state[conversation_key]
        message_count = len(conversation.get("messages", []))
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.success(f"✅ Conversation In Progress (exchanged {message_count} messages)")
        
        with col2:
            if st.button(f"💬 Open Chat", key=f"open_chat_{question_index}"):
                st.session_state[f"show_chat_{question_index}"] = True
                # Use local refresh instead of global refresh
                st.rerun()
        
        with col3:
            if st.button(f"💾 Save", key=f"quick_save_{question_index}", type="primary"):
                # Quick save conversation
                save_data = {"conversation": conversation}
                
                with st.spinner("Saving..."):
                    result = make_api_request(
                        "POST",
                        f"/accounts/{st.session_state.current_account_id}/conversations/end",
                        save_data
                    )
                    
                    if "error" not in result:
                        st.success("Conversation saved!")
                        # Only clear current question's state, not affecting other questions
                        st.session_state[conversation_key] = None
                        st.rerun()
                    else:
                        st.error(f"SaveFailure: {result['error']}")
    else:
        if st.button(f"🚀 Start Conversation", key=f"start_{question_index}"):
            # Start Conversation
            conversation_data = {
                "question": question["question_text"],
                "context": {"category": question["category"]},
                "simplified": True  # Use simplified mode
            }
            
            result = make_api_request(
                "POST",
                f"/accounts/{st.session_state.current_account_id}/conversations/start",
                conversation_data
            )
            
            if "error" not in result:
                st.session_state[conversation_key] = result
                st.session_state[f"show_chat_{question_index}"] = True
                # Collapse all other questions when starting conversation
                for j in range(len(st.session_state.get("core_questions", []))):
                    if j != question_index and f"question_{j}" in st.session_state:
                        st.session_state[f"question_{j}"]["expanded"] = False
                st.rerun()
            else:
                st.error(f"Start ConversationFailure: {result['error']}")

def main():
    """Main function"""
    # InitializeSessionState
    init_session_state()
    
    st.title("🎯 Strategic Account Plan AI Agent")
    st.markdown("Intelligent system for automatically generating strategic customer plans through AI")
    
    # Sidebar
    with st.sidebar:
        # User information
        st.header("👤 User Information")
        user_info = st.session_state.user_info
        st.write(f"**Username:** {user_info['username']}")
        st.write(f"**Role:** {'Administrator' if user_info.get('is_admin') else 'Regular User'}")
        
        if st.button("🔐 Logout"):
            # ClearLoginState
            for key in ["access_token", "user_info", "current_account_id", "current_plan_id", "interactions", "prefill_data_cache"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.show_main_app = False
            st.rerun()
        
        st.markdown("---")
        
        st.header("📋 Navigate")
        page = st.selectbox(
            "Select Page",
            ["Account Management", "Information Collection", "Plan Generation", "History View", "System Settings"]
        )
    
    # Display content based on selected page
    if page == "Account Management":
        show_account_management()
    elif page == "Information Collection":
        show_information_collection()
    elif page == "Plan Generation":
        show_plan_generation()
    elif page == "History View":
        show_history_view()
    elif page == "System Settings":
        show_system_settings()

def show_account_management():
    """Account management page"""
    st.header("🏢 Account Management")
    
    # Clear edit state (preserve current page edit state)
    # Comment out automatic clear, let users manually complete edit or cancel
    
    # CountryFilter
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get all countries
        countries_result = make_api_request("GET", "/countries/")
        if "error" not in countries_result:
            countries = ["All Countries"] + countries_result.get("countries", [])
            selected_country = st.selectbox("🌍 SelectCountry", countries, key="country_filter")
        else:
            selected_country = "All Countries"
    
    with col2:
        if st.button("🔄 RefreshList"):
            st.rerun()
    
    # Create new account
    with st.expander("Create New Account", expanded=True):
        with st.form("create_account_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input("Company Name *", placeholder="Please enterCompany Name")
                industry = st.text_input("Industry", placeholder="e.g.: Technology, Finance, Manufacturing, etc.")
            
            with col2:
                company_size = st.selectbox("Company Size", ["Unknown", "Small (1-50 people)", "Medium (51-200 people)", "Large (201-1000 people)", "Extra Large (1000+ people)"])
                website = st.text_input("Official Website", placeholder="https://www.example.com")
            
            col3, col4 = st.columns(2)
            with col3:
                # Use unified country list function
                available_countries = get_countries_list()
                country = st.selectbox("Country *", available_countries)
            with col4:
                description = st.text_area("Company Description", placeholder="Please enterCompany Description...")
            
            submitted = st.form_submit_button("Create Account", type="primary")
            
            if submitted:
                if not company_name:
                    st.error("Please enterCompany Name")
                elif not country:
                    st.error("Please select a country")
                else:
                    data = {
                        "company_name": company_name,
                        "industry": industry if industry else None,
                        "company_size": company_size if company_size != "Unknown" else None,
                        "website": website if website else None,
                        "country": country,
                        "description": description if description else None
                    }
                    
                    result = make_api_request("POST", "/accounts/", data)
                    
                    if "error" in result:
                        st.error(f"Create account failed: {result['error']}")
                    else:
                        st.success(f"Account created successfully! Account ID: {result['id']}")
                        st.session_state.current_account_id = result['id']
    
    # Account list
    st.subheader(f"📋 Account List ({selected_country})")
    
    # Get account list based on selected country
    params = {}
    if selected_country != "All Countries":
        params["country"] = selected_country
    
    
    result = make_api_request("GET", "/accounts/", data=None, params=params)
    
    if "error" in result:
        st.error(f"Get account list failed: {result['error']}")
    else:
        accounts = result.get("accounts", [])
        
        if accounts:
            # Table header
            if st.session_state.get("user_info", {}).get("is_admin", False):
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
                with col7:
                    st.write("**Edit**")
                with col8:
                    st.write("**Delete**")
            else:
                col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.write("**Company Name**")
            with col2:
                st.write("**Industry**")
            with col3:
                st.write("**Scale**")
            with col4:
                st.write("**Country**")
            with col5:
                st.write("**Created Time**")
            with col6:
                st.write("**Actions**")
            st.divider()
            
            # Use simple table display
            for account in accounts:
                if st.session_state.get("user_info", {}).get("is_admin", False):
                    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
                else:
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                with col1:
                    st.write(f"**{account['company_name']}**")
                with col2:
                    st.write(account.get('industry', 'Unknown'))
                with col3:
                    st.write(account.get('company_size', 'Unknown'))
                with col4:
                    st.write(f"🌍 {account.get('country', 'Unknown')}")
                with col5:
                    st.write(account['created_at'][:10])
                with col6:
                    if st.button(f"Select", key=f"select_{account['id']}"):
                        # Clear state when switching accounts
                        if st.session_state.get("current_account_id") != account['id']:
                            clear_account_state()
                        st.session_state.current_account_id = account['id']
                        st.rerun()
                
                # Administrator action buttons
                is_admin = st.session_state.get("user_info", {}).get("is_admin", False)
                if is_admin:
                    # Edit button
                    with col7:
                        if st.button("✏️", key=f"edit_{account['id']}", help="Edit account info"):
                            st.session_state[f"editing_account_{account['id']}"] = True
                            st.rerun()
                    
                    # Delete button
                    with col8:
                        # Check if delete is confirmed
                        if st.session_state.get(f"confirm_delete_{account['id']}", False):
                            # Display warning information
                            st.warning("⚠️ Confirm delete? This will delete all related data!")
                            # Display confirm button
                            if st.button("✅ ConfirmDelete", key=f"confirm_{account['id']}", type="primary"):
                                # ExecuteDelete
                                result = make_api_request("DELETE", f"/accounts/{account['id']}")
                                if "error" in result:
                                    st.error(f"DeleteFailure: {result['error']}")
                                else:
                                    st.success(f"Account '{account['company_name']}' deleted")
                                    # CleanConfirmState
                                    del st.session_state[f"confirm_delete_{account['id']}"]
                                    st.rerun()
                            
                            # Cancel button
                            if st.button("❌ Cancel", key=f"cancel_{account['id']}"):
                                del st.session_state[f"confirm_delete_{account['id']}"]
                                st.rerun()
                        else:
                            # Initial delete button
                            if st.button("🗑️", key=f"delete_{account['id']}", help="Delete account (requires double confirmation)"):
                                st.session_state[f"confirm_delete_{account['id']}"] = True
                                st.rerun()
                
                # Edit account form (if currently editing)
                if is_admin and st.session_state.get(f"editing_account_{account['id']}", False):
                    st.markdown("---")
                    st.markdown(f"### ✏️ Edit Account: {account['company_name']}")
                    
                    with st.form(f"edit_account_form_{account['id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_company_name = st.text_input(
                                "Company Name *", 
                                value=account['company_name'],
                                key=f"edit_company_name_{account['id']}"
                            )
                            new_industry = st.text_input(
                                "Industry", 
                                value=account.get('industry', ''),
                                key=f"edit_industry_{account['id']}"
                            )
                        
                        with col2:
                            new_company_size = st.selectbox(
                                "Company Size", 
                                ["Unknown", "Small (1-50 people)", "Medium (51-200 people)", "Large (201-1000 people)", "Extra Large (1000+ people)"],
                                index=["Unknown", "Small (1-50 people)", "Medium (51-200 people)", "Large (201-1000 people)", "Extra Large (1000+ people)"].index(account.get('company_size', 'Unknown')),
                                key=f"edit_company_size_{account['id']}"
                            )
                            new_website = st.text_input(
                                "Official Website", 
                                value=account.get('website', ''),
                                key=f"edit_website_{account['id']}"
                            )
                        
                        col3, col4 = st.columns(2)
                        with col3:
                            # Use unified country list function
                            available_countries = get_countries_list()
                            
                            # Calculate current country index
                            current_country = account.get('country', 'China')
                            try:
                                country_index = available_countries.index(current_country)
                            except ValueError:
                                country_index = 0
                            
                            new_country = st.selectbox(
                                "Country *", 
                                available_countries,
                                index=country_index,
                                key=f"edit_country_{account['id']}"
                            )
                        with col4:
                            new_description = st.text_area(
                                "Company Description", 
                                value=account.get('description', ''),
                                key=f"edit_description_{account['id']}"
                            )
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("💾 SaveModify", type="primary"):
                                if not new_company_name:
                                    st.error("Please enterCompany Name")
                                elif not new_country:
                                    st.error("Please select a country")
                                else:
                                    # Prepare update data
                                    update_data = {
                                        "company_name": new_company_name,
                                        "industry": new_industry if new_industry else None,
                                        "company_size": new_company_size if new_company_size != "Unknown" else None,
                                        "website": new_website if new_website else None,
                                        "country": new_country,
                                        "description": new_description if new_description else None
                                    }
                                    
                                    # Call update API
                                    result = make_api_request("PUT", f"/accounts/{account['id']}", update_data)
                                    
                                    if "error" not in result:
                                        st.success("✅ Account information updated successfully!")
                                        # CleanEditState
                                        del st.session_state[f"editing_account_{account['id']}"]
                                        st.rerun()
                                    else:
                                        st.error(f"❌ UpdateFailure: {result['error']}")
                        
                        with col_cancel:
                            if st.form_submit_button("❌ Cancel"):
                                del st.session_state[f"editing_account_{account['id']}"]
                                st.rerun()
                    
                    st.markdown("---")
                
                st.divider()
            
            # Select account dropdown
            account_options = [f"{acc['id']} - {acc['company_name']}" for acc in accounts]
            current_selection = None
            if st.session_state.current_account_id:
                current_selection = f"{st.session_state.current_account_id} - {next((acc['company_name'] for acc in accounts if acc['id'] == st.session_state.current_account_id), 'Unknown')}"
            
            selected_account = st.selectbox(
                "Select account to operate",
                options=account_options,
                index=account_options.index(current_selection) if current_selection in account_options else 0,
                key="account_selector"
            )
            
            if selected_account:
                account_id = int(selected_account.split(" - ")[0])
                if st.session_state.current_account_id != account_id:
                    # Clear state related to old account
                    clear_account_state()
                    st.session_state.current_account_id = account_id
                    st.rerun()
                
                # Display current selected account information
                selected_account_info = next((acc for acc in accounts if acc['id'] == account_id), None)
                if selected_account_info:
                    st.success(f"✅ Currently selected account: {selected_account_info['company_name']}")
                    with st.expander("📋 Account Detailed Information", expanded=False):
                        st.write(f"**Company Name：** {selected_account_info.get('company_name', 'Unknown')}")
                        st.write(f"**Industry：** {selected_account_info.get('industry', 'Unknown')}")
                        st.write(f"**Company Size：** {selected_account_info.get('company_size', 'Unknown')}")
                        st.write(f"**Official Website：** {selected_account_info.get('website', 'Unknown')}")
                        st.write(f"**Company Description:** {selected_account_info.get('description', 'No description available')}")
                        st.write(f"**Created Time:** {selected_account_info.get('created_at', 'Unknown')}")
        else:
            st.info("No account data available")

def clear_account_state():
    """Clear account related state"""
    if "current_plan_id" in st.session_state:
        del st.session_state.current_plan_id
    if "customer_profile" in st.session_state:
        del st.session_state.customer_profile
    if "editing_plan_content" in st.session_state:
        st.session_state["editing_plan_content"] = False
    if "edited_plan_content" in st.session_state:
        del st.session_state["edited_plan_content"]
    if "editing_profile" in st.session_state:
        st.session_state["editing_profile"] = False
    if "editing" in st.session_state:
        del st.session_state["editing"]
    # Clear cached historical data
    if "prefill_data_cache" in st.session_state:
        st.session_state.prefill_data_cache = {}

def get_countries_list():
    """Unified function to get country list"""
    try:
        countries_result = make_api_request("GET", "/countries/")
        if "error" not in countries_result:
            countries = countries_result.get("countries", [])
            # Add default country (if not exists)
            default_countries = ["China", "United States", "Japan", "South Korea", "Germany", "France", "United Kingdom", "Italy", "Spain", "Canada", "Australia", "India", "Brazil", "Other"]
            for default_country in default_countries:
                if default_country not in countries:
                    countries.append(default_country)
            countries.sort()
            return countries
        else:
            # If API fails, use default list
            return ["China", "United States", "Japan", "South Korea", "Germany", "France", "United Kingdom", "Italy", "Spain", "Canada", "Australia", "India", "Brazil", "Other"]
    except:
        return ["China", "United States", "Japan", "South Korea", "Germany", "France", "United Kingdom", "Italy", "Spain", "Canada", "Australia", "India", "Brazil", "Other"]

def check_duplicate_profiles():
    """Check if there are duplicate Customer Profile data"""
    try:
        # Check if there are duplicate data (through API check)
        result = make_api_request("GET", "/health")  # Simple health check
        if "error" not in result:
            # Here you can add more detailed duplicate check logic
            # Currently backend API ensures only one Customer Profile is returned
            return False
        return False
    except:
        return False

def load_saved_profile():
    """Automatically load saved Customer Profile"""
    try:
        account_id = st.session_state.current_account_id
        if not account_id:
            return
        
        # Get saved Customer Profile
        result = make_api_request("GET", f"/accounts/{account_id}/customer-profile")
        
        if "error" not in result and result.get("exists"):
            profile_content = result.get("profile", "")
            created_at = result.get("created_at", "")
            st.session_state["customer_profile"] = profile_content
            
            # Display load information, including update time
            created_at = result.get("created_at", "")
            updated_at = result.get("updated_at", "")
            
            if updated_at and updated_at != created_at:
                st.success(f"📖 Automatically loaded saved Customer Profile (Updated: {updated_at[:10]})")
            elif created_at:
                st.success(f"📖 Automatically loaded saved Customer Profile (Saved: {created_at[:10]})")
            else:
                st.success("📖 Automatically loaded saved Customer Profile!")
        else:
            # No saved Customer Profile, session is empty
            if "customer_profile" not in st.session_state:
                st.session_state["customer_profile"] = ""
                
    except Exception as e:
        if "customer_profile" not in st.session_state:
            st.session_state["customer_profile"] = ""

def show_information_collection():
    """Information Collection page"""
    st.header("📊 Information Collection")
    
    if not st.session_state.current_account_id:
        st.warning("Please select an account first")
        return
    
    # Display current selected account information
    result = make_api_request("GET", "/accounts/")
    if "error" not in result:
        accounts = result.get("accounts", [])
        current_account = next((acc for acc in accounts if acc['id'] == st.session_state.current_account_id), None)
        if current_account:
            st.info(f"🎯 Current operating account: **{current_account['company_name']}** | Industry: {current_account.get('industry', 'Unknown')} | Scale: {current_account.get('company_size', 'Unknown')}")
        else:
            st.error("Unable to find current account information")
            return
    else:
        st.error("Unable to get account information")
        return
    
    # ExternalInformation Collection
    st.subheader("🌐 ExternalInformation Collection")
    
    # Add view external information button
    if st.button("📋 View Collected External Information", type="secondary"):
        result = make_api_request("GET", f"/accounts/{st.session_state.current_account_id}/external-info")
        
        if "error" in result:
            st.error(f"GetExternal InformationFailure: {result['error']}")
        else:
            st.success("External InformationGetSuccess！")
            
            external_info = result.get("external_info", {})
            
            # Display company information (supports editing)
            if "company_profile" in external_info:
                with st.expander("🏢 Company Basic Information", expanded=True):
                    profile = external_info["company_profile"].get("content", {}) if isinstance(external_info["company_profile"], dict) else external_info["company_profile"]
                    st.write("**View / Edit Company Information**")
                    edited_company = st.text_input("Company Name", value=profile.get("company_name", ""))
                    edited_industry = st.text_input("Industry", value=profile.get("industry", ""))
                    edited_size = st.text_input("Company Size", value=profile.get("company_size", ""))
                    edited_site = st.text_input("Official Website", value=profile.get("website", ""))
                    edited_desc = st.text_area("Company Description", value=profile.get("description", ""), height=120)
                    if st.button("💾 Save Company Info", key="save_company_profile"):
                        payload = {
                            "info_type": "company_profile",
                            "content": {
                                "company_name": edited_company,
                                "industry": edited_industry,
                                "company_size": edited_size,
                                "website": edited_site,
                                "description": edited_desc
                            }
                        }
                        save_res = make_api_request("PUT", f"/accounts/{st.session_state.current_account_id}/external-info", payload)
                        if "error" in save_res:
                            st.error(f"SaveFailure: {save_res['error']}")
                        else:
                            st.success("✅ Company information saved")
                            st.rerun()
            
            # Display news information (supports editing summary and entries)
            if "news" in external_info:
                with st.expander("📰 News Information", expanded=False):
                    news = external_info["news"].get("content", {}) if isinstance(external_info["news"], dict) else external_info["news"]
                    st.write(f"**News Count:** {news.get('news_count', 0)}")
                    st.write(f"**Time Range:** {news.get('time_range', 'Unknown')}")
                    edited_summary = st.text_area("News Summary (Editable)", value=news.get('summary', ''), height=150)
                    # Optional: Edit partial news entries
                    items = news.get("news_data", [])
                    if items:
                        st.markdown("**News Entries (First 5 Editable)**")
                        max_edit = min(5, len(items))
                        for idx in range(max_edit):
                            with st.expander(f"Edit News {idx+1}"):
                                title = st.text_input(f"Title {idx+1}", value=items[idx].get("title", ""), key=f"news_title_{idx}")
                                summary = st.text_area(f"Abstract {idx+1}", value=items[idx].get("summary", ""), key=f"news_sum_{idx}")
                                date = st.text_input(f"Date {idx+1}", value=items[idx].get("date", ""), key=f"news_date_{idx}")
                                source = st.text_input(f"Source {idx+1}", value=items[idx].get("source", ""), key=f"news_src_{idx}")
                                items[idx] = {"title": title, "summary": summary, "date": date, "source": source}
                    if st.button("💾 Save News Info", key="save_news_info"):
                        payload = {
                            "info_type": "news",
                            "content": {**news, "summary": edited_summary, "news_data": items}
                        }
                        save_res = make_api_request("PUT", f"/accounts/{st.session_state.current_account_id}/external-info", payload)
                        if "error" in save_res:
                            st.error(f"SaveFailure: {save_res['error']}")
                        else:
                            st.success("✅ News information saved")
                            st.rerun()
            
            # Display market information (supports editing)
            if "market_info" in external_info:
                with st.expander("📊 Market Information", expanded=False):
                    market = external_info["market_info"].get("content", {}) if isinstance(external_info["market_info"], dict) else external_info["market_info"]
                    edited_industry = st.text_input("Industry", value=market.get('industry', ''))
                    edited_trends = st.text_area("Trends", value=market.get('trends', ''), height=120)
                    
                    # Handle competitors (could be list of strings or list of dicts)
                    competitors_list = market.get('competitors', []) or []
                    competitors_str_list = []
                    for item in competitors_list:
                        if isinstance(item, dict):
                            # If dict, try to extract name or convert to string
                            competitors_str_list.append(item.get('name', str(item)))
                        else:
                            competitors_str_list.append(str(item))
                    edited_competitors = st.text_area("Competitors (separated by commas)", value=", ".join(competitors_str_list))
                    
                    # Handle opportunities (could be list of strings or list of dicts)
                    opportunities_list = market.get('opportunities', []) or []
                    opportunities_str_list = []
                    for item in opportunities_list:
                        if isinstance(item, dict):
                            opportunities_str_list.append(item.get('description', str(item)))
                        else:
                            opportunities_str_list.append(str(item))
                    edited_opportunities = st.text_area("Market Opportunities (separated by commas)", value=", ".join(opportunities_str_list))
                    
                    # Handle risks (could be list of strings or list of dicts)
                    risks_list = market.get('risks', []) or []
                    risks_str_list = []
                    for item in risks_list:
                        if isinstance(item, dict):
                            risks_str_list.append(item.get('description', str(item)))
                        else:
                            risks_str_list.append(str(item))
                    edited_risks = st.text_area("Potential Risks (separated by commas)", value=", ".join(risks_str_list))
                    if st.button("💾 Save Market Info", key="save_market_info"):
                        payload = {
                            "info_type": "market_info",
                            "content": {
                                "industry": edited_industry,
                                "trends": edited_trends,
                                "competitors": [s.strip() for s in edited_competitors.split(',') if s.strip()],
                                "opportunities": [s.strip() for s in edited_opportunities.split(',') if s.strip()],
                                "risks": [s.strip() for s in edited_risks.split(',') if s.strip()]
                            }
                        }
                        save_res = make_api_request("PUT", f"/accounts/{st.session_state.current_account_id}/external-info", payload)
                        if "error" in save_res:
                            st.error(f"SaveFailure: {save_res['error']}")
                        else:
                            st.success("✅ Market information saved")
                            st.rerun()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Collect Company Information", type="primary"):
            with st.spinner("Collecting company information..."):
                result = make_api_request(
                    "POST", 
                    f"/accounts/{st.session_state.current_account_id}/external-info",
                    {"info_type": "company_profile"}
                )
                
                if "error" in result:
                    st.error(f"Collection failed: {result['error']}")
                else:
                    st.success("Company information collection completed!")
                    # Display preview of collected information
                    if "results" in result and "company_profile" in result["results"]:
                        profile = result["results"]["company_profile"]
                        st.info(f"Collected company information: {profile.get('company_name', 'Unknown')} - {profile.get('industry', 'UnknownIndustry')}")
    
    with col2:
        if st.button("Collect News Information"):
            with st.spinner("Collecting news information..."):
                result = make_api_request(
                    "POST", 
                    f"/accounts/{st.session_state.current_account_id}/external-info",
                    {"info_type": "news"}
                )
                
                if "error" in result:
                    st.error(f"Collection failed: {result['error']}")
                else:
                    st.success("News information collection completed!")
                    # Display preview of collected information
                    if "results" in result and "news_snapshot" in result["results"]:
                        news = result["results"]["news_snapshot"]
                        st.info(f"Collected {news.get('news_count', 0)} news items")
    
    with col3:
        if st.button("Collect Market Information"):
            with st.spinner("Collecting market information..."):
                result = make_api_request(
                    "POST", 
                    f"/accounts/{st.session_state.current_account_id}/external-info",
                    {"info_type": "market_info"}
                )
                
                if "error" in result:
                    st.error(f"Collection failed: {result['error']}")
                else:
                    st.success("Market information collection completed!")
                    # Display preview of collected information
                    if "results" in result and "market_info" in result["results"]:
                        market = result["results"]["market_info"]
                        st.info(f"Collected market information: {market.get('industry', 'UnknownIndustry')}")
    
    # Internal Information Collection (Q&A)
    st.subheader("💬 InternalInformation Collection")
    
    # Get core questions
    if st.button("GetIssueList"):
        # First initialize question templates
        init_result = make_api_request("POST", "/questions/initialize")
        if "error" not in init_result:
            st.success("Question TemplatesInitializeSuccess")
        
        # Then get question list
        result = make_api_request("GET", "/questions/core")
        
        if "error" in result:
            st.error(f"GetIssueFailure: {result['error']}")
        else:
            st.session_state.core_questions = result.get("questions", [])
            st.success(f"Retrieved {len(st.session_state.core_questions)} core questions")
    
    # Automatically initialize question templates (if no questions yet)
    if "core_questions" not in st.session_state or len(st.session_state.core_questions) == 0:
        st.info("Automatically initializing question templates...")
        init_result = make_api_request("POST", "/questions/initialize")
        if "error" not in init_result:
            # GetIssueList
            result = make_api_request("GET", "/questions/core")
            if "error" not in result:
                st.session_state.core_questions = result.get("questions", [])
                st.success(f"Automatic initialization completed, retrieved {len(st.session_state.core_questions)} core questions")
            else:
                st.error("GetIssueListFailure")
        else:
            st.error("Question TemplatesInitializeFailure")
    
    if "core_questions" in st.session_state and len(st.session_state.core_questions) > 0:
        questions = st.session_state.core_questions
        
        # Display question progress
        progress_result = make_api_request("GET", f"/accounts/{st.session_state.current_account_id}/progress")
        if "error" not in progress_result:
            progress = progress_result
            st.progress(progress.get("completion_rate", 0) / 100)
            st.caption(f"Completion progress: {progress.get('answered_questions', 0)}/{progress.get('total_questions', 0)} questions")
        
        # Optimized multi-turn conversation interface - load on demand
        for i, question in enumerate(questions):
            # InitializeIssueState
            question_key = f"question_{i}"
            if question_key not in st.session_state:
                st.session_state[question_key] = {
                    "loaded": False,
                    "expanded": False
                }
            
            # GetIssueState
            question_state = st.session_state[question_key]
            
            # Handle question title click events
            if not question_state["loaded"]:
                # Only display question title, do not load detailed content
                question_title = f"Issue {i+1}: {question['question_text']}"
                if st.button(question_title, key=f"question_title_{i}", help=f"Click to load question details (Category: {question['category']})"):
                    question_state["loaded"] = True
                    question_state["expanded"] = True
                    # Automatically collapse other expanded questions
                    for j in range(len(questions)):
                        if j != i:
                            other_key = f"question_{j}"
                            if other_key in st.session_state:
                                st.session_state[other_key]["expanded"] = False
                    st.rerun()
            else:
                # Loaded questions, use expander management
                current_expanded = question_state.get("expanded", False)
                question_title = f"Issue {i+1}: {question['question_text']}"
                
                with st.expander(question_title, expanded=current_expanded):
                    if current_expanded:
                        # Display detailed question information
                        st.write(f"**Category:** {question['category']}")
                        
                        # Use cached historical data to avoid duplicate API calls
                        prefill_data = get_cached_prefill_data(st.session_state.current_account_id)
                        
                        # Display pre-filled answers (supports editing)
                        if question['question_text'] in prefill_data:
                            st.markdown("#### 📝 Historical Answer")
                            
                            # Check if in edit mode
                            edit_answer_key = f"edit_answer_{i}"
                            if edit_answer_key not in st.session_state:
                                st.session_state[edit_answer_key] = False
                            
                            if st.session_state[edit_answer_key]:
                                # Edit mode
                                edited_answer = st.text_area(
                                    "Edit Historical Answer:",
                                    value=prefill_data[question['question_text']]['answer'],
                                    height=150,
                                    key=f"answer_edit_{i}"
                                )
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("💾 Save Answer", key=f"save_answer_{i}"):
                                        # SaveModify
                                        update_data = {
                                            "question": question['question_text'],
                                            "answer": edited_answer,
                                            "structured_data": prefill_data[question['question_text']].get('structured_data', {})
                                        }
                                        
                                        result = make_api_request(
                                            "PUT",
                                            f"/accounts/{st.session_state.current_account_id}/interactions/update",
                                            update_data
                                        )
                                        
                                        if "error" not in result:
                                            st.success("✅ Historical answer updated!")
                                            # UpdateCache
                                            prefill_data[question['question_text']]['answer'] = edited_answer
                                            st.session_state[edit_answer_key] = False
                                            st.rerun()
                                        else:
                                            st.error(f"SaveFailure: {result['error']}")
                                
                                with col2:
                                    if st.button("❌ Cancel", key=f"cancel_answer_{i}"):
                                        st.session_state[edit_answer_key] = False
                                        st.rerun()
                            else:
                                # Display mode
                                st.info(prefill_data[question['question_text']]['answer'])
                                if st.button("✏️ Edit Answer", key=f"edit_answer_btn_{i}"):
                                    st.session_state[edit_answer_key] = True
                                    st.rerun()
                        
                        # Check if to display chat window
                        if st.session_state.get(f"show_chat_{i}", False):
                            show_chat_window(i, question, st.session_state.current_account_id)
                        else:
                            show_chat_status(i, question)
                
                # Handle question expand/collapse buttons
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"🔄 {'Reload' if current_expanded else 'Expand Details'}", key=f"toggle_{i}"):
                        question_state["expanded"] = not question_state["expanded"]
                        # If expanding current question, collapse other questions
                        if question_state["expanded"]:
                            for j in range(len(questions)):
                                if j != i and f"question_{j}" in st.session_state:
                                    st.session_state[f"question_{j}"]["expanded"] = False
                        st.rerun()
                
                with col2:
                    # Display question state
                    if question_state.get("expanded", False):
                        st.success("✓ Loaded")
                    else:
                        st.info("📋 Ready")
    else:
        st.warning("No question templates available, please initialize question templates first")

def show_plan_generation():
    """Plan Generation page - Customer Profile and plan management"""
    st.header("📋 Plan GenerationManage")
    
    if not st.session_state.current_account_id:
        st.warning("Please select an account first")
        return
    
    # Display current selected account information
    result = make_api_request("GET", "/accounts/")
    if "error" not in result:
        accounts = result.get("accounts", [])
        current_account = next((acc for acc in accounts if acc['id'] == st.session_state.current_account_id), None)
        if current_account:
            st.info(f"🎯 Current operating account: **{current_account['company_name']}** | Industry: {current_account.get('industry', 'Unknown')} | Scale: {current_account.get('company_size', 'Unknown')}")
        else:
            st.error("Unable to find current account information")
            return
    else:
        st.error("Unable to get account information")
        return
    
    # Customer ProfilePartial
    st.subheader("👥 Customer Profile")
    
    # Display Customer Profile button
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🤖 Generate Customer Profile", type="primary", help="Generate Customer Profile based on collected information"):
            # BeginGenerateCustomer Profile
            generate_customer_profile()
    
    with col2:
        if st.button("🔄 Refresh Data", help="Refresh collected information and load saved profile"):
            # Clear current profile state, trigger reload
            if "customer_profile" in st.session_state:
                del st.session_state["customer_profile"]
            st.rerun()
    
    with col3:
        if st.button("💾 Save Profile", help="Save Customer Profile"):
            success, message = save_customer_profile()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    # Display Customer Profile content
    show_customer_profile_content()
    
    # Plan management section
    st.subheader("📋 Plan Management")
    show_plan_management()

def generate_customer_profile():
    """GenerateCustomer Profile"""
    try:
        with st.spinner("🤖 AI analyzing collected information and generating Customer Profile..."):
            # Get collected information
            account_id = st.session_state.current_account_id
            
            if not account_id:
                st.error("❌ No account selected, please select an account first")
                return
            
            # Check if Customer Profile already exists
            if "customer_profile" in st.session_state and st.session_state["customer_profile"]:
                st.warning("⚠️ Detected existing Customer Profile, regeneration will overwrite existing content")
                # Clear any old Customer Profile state, prepare for rebuild
                del st.session_state["customer_profile"]
            
            # First get basic historical data (including External and Internal Information)
            history_result = {}
            try:
                history_result = make_api_request("GET", f"/accounts/{account_id}/history")
                if "error" in history_result:
                    st.warning(f"⚠️ History API returned incorrect: {history_result['error']}")
            except Exception as e:
                st.warning(f"⚠️ Issue getting historical data: {str(e)}")
                st.warning("💡 Suggest refreshing page to retry")
            
            # 1. Get External Information - get real External Information from database
            external_data = {}
            try:
                if "error" not in history_result:
                    # external_info structure: {info_type: {content: {...}, source_url: "", created_at: ""}}
                    external_info_raw = history_result.get("external_info", {})
                    
                    if external_info_raw:
                        # Reorganize External Information
                        for info_type, info_content in external_info_raw.items():
                            if isinstance(info_content, dict) and "content" in info_content:
                                external_data[info_type] = info_content["content"]
                            elif info_content:  # Non-empty content
                                external_data[info_type] = info_content
                                
                # Additional retrieval method: if not available from history, try other APIs
                if not external_data:
                    try:
                        external_info_result = make_api_request("GET", f"/accounts/{account_id}/external-info")
                        if "error" not in external_info_result and external_info_result:
                            external_data = external_info_result
                    except Exception as e2:
                        st.info(f"🔄 Issue encountered when trying other methods to get External Information: {str(e2)}")
                        
            except Exception as e:
                st.warning(f"⚠️ Issue getting External Information: {str(e)}")
                external_data = {}
            
            # Debug output - see what was actually retrieved
            st.info(f"🔍 Debug: External Information retrieval result type={type(external_data)}, content count={len(external_data) if isinstance(external_data, dict) else 'N/A'}")
            if external_data:
                st.info(f"🔍 Debug: External Information keys={list(external_data.keys()) if isinstance(external_data, dict) else 'N/A'}")
            
            # 2. Get Internal Information - get Q&A data from interaction records
            internal_data = {}
            try:
                if "error" not in history_result:
                    interactions = history_result.get("interactions", [])
                    
                    # Build Q&A data
                    if interactions:
                        for interaction in interactions:
                            question = interaction.get("question", "")
                            answer = interaction.get("answer", "")
                            if question and answer:
                                internal_data[question] = answer
                    
                    # Try to get more detailed user Q&A content  
                    try:
                        history_prefill = make_api_request("GET", f"/accounts/{account_id}/history/prefill")
                        if "error" not in history_prefill:
                            prefill_data = history_prefill.get("prefill_data", {})
                            # Merge all internal source data
                            for key, value in prefill_data.items():
                                if isinstance(value, dict) and value:
                                    internal_data[f"VerboseRecord_{key}"] = str(value)
                                elif isinstance(value, str) and value:
                                    internal_data[f"Content_{key}"] = value
                    except Exception as e3:
                        st.info(f"🔄 Issue encountered when trying to get pre-processed information: {str(e3)}")
                        
            except Exception as e:
                st.warning(f"⚠️ Issue getting Internal Information: {str(e)}")
                internal_data = {}
            
            # Debug output - see what was actually retrieved
            st.info(f"🔍 Debug: Internal Information retrieval result type={type(internal_data)}, content count={len(internal_data) if isinstance(internal_data, dict) else 'N/A'}")
            if internal_data:
                st.info(f"🔍 Debug: Internal Information keys={list(internal_data.keys()) if isinstance(internal_data, dict) else 'N/A'}")
            
            # 3. Visualize collected information summary
            st.markdown("### 💡 Data Collection Summary")
            
            with st.expander("📊 External Information Collection Status", expanded=False):
                if external_data:
                    for info_type, content in external_data.items():
                        st.write(f"**{info_type}**: {str(content)[:200]}...")
                else:
                    st.write("⚠️ Not foundExternal Information")
            
            with st.expander("💬 Internal Information Collection Status", expanded=False):
                if internal_data:
                    for key, value in internal_data.items():
                        st.write(f"**{key}**: {str(value)[:100]}...")
                else:
                    st.write("⚠️ Not foundInternal Information")
            
            # 4. Send completed collected data to API
            customer_profile_data = {
                "external_info": external_data,
                "internal_info": internal_data
            }
            
            result = make_api_request(
                "POST",
                f"/accounts/{account_id}/generate-customer-profile",
                customer_profile_data
            )
            
            if "error" not in result:
                profile = result.get("profile", "")
                st.session_state["customer_profile"] = profile
                st.success("✅ Customer ProfileGenerateSuccess！")
                st.info("💡 Suggest clicking '💾 Save Profile' button to save to database, this will overwrite previous Customer Profile.")
            else:
                st.error(f"❌ GenerateCustomer ProfileFailure: {result['error']}")
                    
    except Exception as e:
        st.error(f"❌ GenerateCustomer ProfileAbnormal: {str(e)}")

def save_customer_profile(profile_content=None):
    """SaveCustomer Profile"""
    try:
        # Use passed content or get from session state
        if profile_content is None:
            if "customer_profile" not in st.session_state:
                st.warning("⚠️ Please generate Customer Profile first")
                return
            profile_content = st.session_state["customer_profile"]
        
        profile_data = {
            "customer_profile": profile_content,
            "account_id": st.session_state.current_account_id
        }
        
        with st.spinner("🗄️ Saving Customer Profile..."):
            result = make_api_request(
                "POST",
                f"/accounts/{st.session_state.current_account_id}/save-customer-profile",
                profile_data
            )
            
            if "error" not in result:
                return True, "✅ Customer Profile saved successfully! Cross-session access supported, will automatically load on next reopen."
            else:
                return False, f"❌ SaveCustomer ProfileFailure: {result['error']}"
                
    except Exception as e:
        return False, f"❌ SaveCustomer ProfileAbnormal: {str(e)}"

def show_customer_profile_content():
    """Display Customer Profile content"""
    
    # Automatically check if there's a saved Customer Profile
    if "customer_profile" not in st.session_state or not st.session_state["customer_profile"]:
        load_saved_profile()
    
    if "customer_profile" in st.session_state and st.session_state["customer_profile"]:
        
        # Edit mode toggle
        if "editing_profile" not in st.session_state:
            st.session_state["editing_profile"] = False
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 📝 Customer ProfileContent")
        with col2:
            if st.button("✏️ Edit", key="edit_profile_btn"):
                st.session_state["editing_profile"] = not st.session_state["editing_profile"]
                st.rerun()
        
        # Edit or display mode
        if st.session_state["editing_profile"]:
            # Edit mode
            edited_profile = st.text_area(
                "Customer Profile Content (Editable):",
                value=st.session_state["customer_profile"],
                height=400,
                help="You can edit the generated Customer Profile content here"
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("💾 SaveModify", type="primary"):
                    # Updatesession state
                    st.session_state["customer_profile"] = edited_profile
                    
                    # Also save to database
                    success, message = save_customer_profile(edited_profile)
                    if success:
                        st.success("✅ Customer Profile modified and saved to database!")
                    else:
                        st.warning(f"⚠️ Error saving to database: {message[:50]}, modification saved locally")
                    
                    st.session_state["editing_profile"] = False
                    st.rerun()
            
            with col2:
                if st.button("↩️ CancelModify"):
                    st.session_state["editing_profile"] = False
                    st.rerun()
            
            with col3:
                # Check if regeneration is confirmed
                if st.session_state.get("confirm_regenerate_profile", False):
                    # Display warning information
                    st.warning("⚠️ Regeneration will overwrite existing Customer Profile!")
                    # Display confirm button
                    if st.button("✅ Confirm Overwrite", type="primary"):
                        st.session_state["customer_profile"] = ""
                        st.session_state["editing_profile"] = False
                        st.session_state["confirm_regenerate_profile"] = False
                        st.rerun()
                    
                    # Cancel button
                    if st.button("❌ Cancel"):
                        st.session_state["confirm_regenerate_profile"] = False
                        st.rerun()
                else:
                    # Initial regenerate button
                    if st.button("🔄 Regenerate"):
                        st.session_state["confirm_regenerate_profile"] = True
                        st.rerun()
        else:
            # Display mode
            st.markdown(st.session_state["customer_profile"])
    
    else:
        st.info("💡 Click 'Generate Customer Profile' button to begin creating Customer Profile")

def show_plan_management():
    """Plan management section"""
    
    # Generate new plan
    with st.form("generate_plan_form"):
        plan_title = st.text_input("📝 New Plan Title", placeholder="Please enter plan title...", help="Specify title for the upcoming strategic plan")
        
        plan_description = st.text_area(
            "📄 Plan Description (Optional)", 
            placeholder="Please enter special requirements or description for this plan, AI will generate customized content based on this...", 
            help="Describe special requirements or background information for the plan, AI will adjust generated content based on this information",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            generate_button = st.form_submit_button("🚀 Generate Plan", type="primary")
        with col2:
            if st.form_submit_button("👁️ Preview Plan"):
                st.info("Preview feature under development...")
        
        if generate_button:
            with st.spinner("🤖 Generating strategic plan..."):
                data = {
                    "title": plan_title if plan_title else f"Strategic_Plan_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    "description": plan_description if plan_description else None
                }
                result = make_api_request(
                    "POST",
                    f"/accounts/{st.session_state.current_account_id}/plans",
                    data
                )
                
                if "error" in result:
                    st.error(f"❌ GenerateFailure: {result['error']}")
                else:
                    st.success("✅ Plan GenerationSuccess！")
                    st.session_state.current_plan_id = result.get("id")
    
    # Plan list display
    st.markdown("---")
    show_plans_list()
    
    # Current plan details (if there is a selected plan)
    show_current_plan()

def show_plans_list():
    """Display plan list"""
    st.subheader("📋 Plan List")
    
    if st.button("🔄 Refresh Plan List", help="Reload plan data"):
        st.rerun()
    
    try:
        result = make_api_request("GET", f"/accounts/{st.session_state.current_account_id}/plans")
        
        if "error" not in result:
            plans = result.get("plans", [])
            
            if plans:
                for plan in plans:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            st.write(f"**📋 {plan['title']}**")
                            st.caption(f"State: {plan['status']} | Create: {plan.get('created_at', '').split('T')[0]}")
                        
                        with col2:
                            if st.button(f"👁️ View", key=f"view_plan_{plan['id']}"):
                                st.session_state.current_plan_id = plan['id']
                                st.rerun()
                        
                        with col3:
                            if st.button(f"✏️ Edit", key=f"edit_plan_{plan['id']}"):
                                st.session_state.current_plan_id = plan['id']
                                st.session_state["editing"] = True
                                st.rerun()
                        
                        with col4:
                            if st.button(f"🗑️ Delete", key=f"delete_plan_{plan['id']}"):
                                # AddDeleteConfirm
                                if plan['id'] == st.session_state.current_plan_id:
                                    st.session_state.current_plan_id = None
                                
                                delete_result = make_api_request("DELETE", f"/plans/{plan['id']}")
                                if "error" not in delete_result:
                                    st.success("✅ Plan deleted!")
                                    st.rerun()
                                else:
                                    st.error(f"DeleteFailure: {delete_result['error']}")
                        
                        st.divider()
            else:
                st.info("📝 No plan data available, click 'Generate Plan' above to begin creating strategic plan")
    except Exception as e:
        st.error(f"❌ Failed to get plan list: {str(e)}")

def show_current_plan():
    """Display current selected plan details"""
    if st.session_state.current_plan_id:
        st.markdown("---")
        st.subheader("📄 Current Plan Details")
        
        try:
            result = make_api_request("GET", f"/plans/{st.session_state.current_plan_id}")
            
            if "error" not in result:
                plan = result
                
                # Basic plan information
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.write(f"**Title:** {plan.get('title', 'Not specified')}")
                    st.write(f"**State:** {plan.get('status', 'Unknown')}")
                with col_info2:
                    if plan.get('created_at'):
                        st.write(f"**Created Time:** {plan['created_at']}")
                    if plan.get('updated_at'):
                        st.write(f"**Updated Time:** {plan['updated_at']}")
                
                # Display content or editor based on edit state
                if st.session_state.get("editing_plan_content", False):
                    show_plan_editor(plan)
                else:
                    show_plan_content(plan)
                    
            else:
                st.error(f"Unable to get plan details: {result.get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Failed to get plan details: {str(e)}")

def show_plan_content(plan):
    """Display plan content in read-only mode"""
    st.markdown("---")
    content = plan.get('content', '')
    if content:
        st.markdown("### 📋 Plan Content")
        st.markdown(content)
    else:
        st.info("📝 This plan has no content yet, you can click Edit to add")
    
    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("✏️ Edit Plan Content", key="edit_plan_content"):
            st.session_state["editing_plan_content"] = True
            st.rerun()
    
def show_plan_editor(plan):
    """Display plan content editor"""
    st.markdown("---")
    st.markdown("### ✏️ Edit Plan Content")
    
    # Get current content as editor initial value
    if "edited_plan_content" not in st.session_state:
        st.session_state["edited_plan_content"] = plan.get('content', '')
    
    # Large text editor
    edited_content = st.text_area(
        "Plan Content (Markdown format supported)",
        value=st.session_state.get("edited_plan_content", ""),
        height=500,
        key="plan_content_editor",
        help="Use Markdown syntax to format content"
    )
    
    # Updatesession state
    st.session_state["edited_plan_content"] = edited_content
    
    # Save and Cancel buttons
    col_save, col_cancel, col_preview = st.columns(3)
    
    with col_save:
        if st.button("💾 SaveModify", type="primary"):
            # Call save API
            success = save_plan_content(st.session_state.current_plan_id, edited_content)
            if success:
                st.success("✅ Plan content saved!")
                # Cleansession state
                del st.session_state["editing_plan_content"]
                del st.session_state["edited_plan_content"]
                st.rerun()
            else:
                st.error("❌ Save failed, please retry")
    
    with col_cancel:
        if st.button("❌ CancelEdit"):
            # Cleansession state
            if "editing_plan_content" in st.session_state:
                del st.session_state["editing_plan_content"]
            if "edited_plan_content" in st.session_state:
                del st.session_state["edited_plan_content"]
            st.rerun()
    
    with col_preview:
        if st.button("👁️ Preview"):
            st.markdown("### 📄 Preview")
            st.markdown(edited_content)

def save_plan_content(plan_id, content):
    """Save plan content modifications"""
    try:
        update_data = {"content": content}
        result = make_api_request(
            "PUT", 
            f"/plans/{plan_id}", 
            update_data
        )
        return "error" not in result
    except Exception as e:
        st.error(f"Error saving plan: {str(e)}")
        return False

def show_history_view():
    """History view page"""
    st.header("📚 History View")
    
    if not st.session_state.current_account_id:
        st.warning("Please select an account first")
        return
    
    # Account historical information
    st.subheader("📊 Account Historical Information")
    
    if st.button("Load Historical Information"):
        result = make_api_request("GET", f"/accounts/{st.session_state.current_account_id}/history")
        
        if "error" in result:
            st.error(f"Failed to get historical information: {result['error']}")
        else:
            history = result
            
            # Display account information
            st.write("**Account Information:**")
            account_info = history.get("account", {})
            st.json(account_info)
            
            # Display interaction history
            st.write("**Interaction History:**")
            interactions = history.get("interactions", [])
            
            if interactions:
                for i, interaction in enumerate(interactions):
                    with st.expander(f"Interaction {i+1}: {interaction['question'][:50]}...", expanded=False):
                        st.write(f"**Issue:** {interaction['question']}")
                        st.write(f"**Answer:** {interaction['answer']}")
                        st.write(f"**Time:** {interaction['created_at']}")
                        if interaction.get('structured_data'):
                            st.write("**Structured Data:**")
                            st.json(interaction['structured_data'])
            else:
                st.info("No interaction history available")
            
            # Display External Information
            st.write("**External Information:**")
            external_info = history.get("external_info", {})
            if external_info:
                for info_type, info_data in external_info.items():
                    with st.expander(f"External Information: {info_type}", expanded=False):
                        st.json(info_data)
            else:
                st.info("No External Information available")
            
            # Display plan history
            st.write("**Plan History:**")
            plans = history.get("plans", [])
            if plans:
                for plan in plans:
                    with st.expander(f"Plan: {plan['title']}", expanded=False):
                        st.write(f"**State:** {plan['status']}")
                        st.write(f"**Created Time:** {plan['created_at']}")
                        st.write(f"**Updated Time:** {plan['updated_at']}")
                        if plan.get('change_log'):
                            st.write("**Change Log:**")
                            st.json(plan['change_log'])
            else:
                st.info("No plan history available")

def show_system_settings():
    """System settings page"""
    st.header("⚙️ System Settings")
    
    # APIStateCheck
    st.subheader("🔍 System Status")
    
    if st.button("CheckAPIState"):
        result = make_api_request("GET", "/health")
        
        if "error" in result:
            st.error(f"APIJoinFailure: {result['error']}")
        else:
            st.success("APIJoinNormal")
            st.json(result)
    
    # Question TemplatesManage
    st.subheader("📝 Question TemplatesManage")
    
    # Get current Question Templates
    if st.button("🔄 RefreshQuestion Templates"):
        st.rerun()
    
    # Automatically get Question Templates
    questions_result = make_api_request("GET", "/questions/core")
    
    if "error" in questions_result:
        st.warning("Unable to get Question Templates, please initialize first")
        if st.button("InitializeQuestion Templates"):
            with st.spinner("Initializing Question Templates..."):
                init_result = make_api_request("POST", "/questions/initialize")
                
                if "error" in init_result:
                    st.error(f"InitializeFailure: {init_result['error']}")
                else:
                    st.success("Question TemplatesInitializeComplete")
                    st.rerun()
    else:
        questions = questions_result.get("questions", [])
        
        if not questions:
            st.info("No Question Templates available")
            if st.button("InitializeQuestion Templates"):
                with st.spinner("Initializing Question Templates..."):
                    init_result = make_api_request("POST", "/questions/initialize")
                    
                    if "error" in init_result:
                        st.error(f"InitializeFailure: {init_result['error']}")
                    else:
                        st.success("Question TemplatesInitializeComplete")
                        st.rerun()
        else:
            st.success(f"Currently have {len(questions)} Question Templates")
            
            # Display Question Templates list
            st.markdown("#### 📋 Question TemplatesList")
            
            for i, question in enumerate(questions):
                with st.expander(f"Issue {i+1}: {question['question_text']}", expanded=False):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**Category:** {question['category']}")
                        st.write(f"**Issue:** {question['question_text']}")
                        if question.get('description'):
                            st.write(f"**Description:** {question['description']}")
                    
                    with col2:
                        if st.button(f"✏️ Edit", key=f"edit_{question['id']}"):
                            st.session_state[f"editing_question_{question['id']}"] = True
                            st.rerun()
                    
                    with col3:
                        if st.button(f"🗑️ Delete", key=f"delete_{question['id']}"):
                            st.session_state[f"confirm_delete_{question['id']}"] = True
                            st.rerun()
                    
                    # Edit question form
                    if st.session_state.get(f"editing_question_{question['id']}", False):
                        st.markdown("---")
                        st.markdown("#### ✏️ EditIssue")
                        
                        with st.form(f"edit_form_{question['id']}"):
                            new_question_text = st.text_area(
                                "IssueContent",
                                value=question['question_text'],
                                height=100,
                                key=f"edit_text_{question['id']}"
                            )
                            
                            new_category = st.selectbox(
                                "Question Category",
                                options=["Cooperation History", "Products & Services", "Challenges & Issues", "Key Contacts", "Future Plans", "Resource Needs"],
                                index=["Cooperation History", "Products & Services", "Challenges & Issues", "Key Contacts", "Future Plans", "Resource Needs"].index(question['category']) if question['category'] in ["Cooperation History", "Products & Services", "Challenges & Issues", "Key Contacts", "Future Plans", "Resource Needs"] else 0,
                                key=f"edit_category_{question['id']}"
                            )
                            
                            new_description = st.text_area(
                                "Question Description (Optional)",
                                value=question.get('description', ''),
                                height=60,
                                key=f"edit_desc_{question['id']}"
                            )
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.form_submit_button("💾 SaveModify", type="primary"):
                                    if new_question_text:
                                        # UpdateIssue
                                        update_data = {
                                            "question_text": new_question_text,
                                            "category": new_category,
                                            "description": new_description if new_description else None
                                        }
                                        
                                        result = make_api_request(
                                            "PUT",
                                            f"/questions/{question['id']}",
                                            update_data
                                        )
                                        
                                        if "error" not in result:
                                            st.success("IssueUpdateSuccess！")
                                            st.session_state[f"editing_question_{question['id']}"] = False
                                            st.rerun()
                                        else:
                                            st.error(f"UpdateFailure: {result['error']}")
                                    else:
                                        st.warning("Please enterIssueContent")
                            
                            with col2:
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state[f"editing_question_{question['id']}"] = False
                                    st.rerun()
                    
                    # DeleteConfirm
                    if st.session_state.get(f"confirm_delete_{question['id']}", False):
                        st.markdown("---")
                        st.warning(f"⚠️ Are you sure you want to delete question: '{question['question_text']}'?")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button(f"✅ ConfirmDelete", key=f"confirm_del_{question['id']}"):
                                # DeleteIssue
                                result = make_api_request(
                                    "DELETE",
                                    f"/questions/{question['id']}"
                                )
                                
                                if "error" not in result:
                                    st.success("IssueDeleteSuccess！")
                                    st.session_state[f"confirm_delete_{question['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error(f"DeleteFailure: {result['error']}")
                        
                        with col2:
                            if st.button(f"❌ CancelDelete", key=f"cancel_del_{question['id']}"):
                                st.session_state[f"confirm_delete_{question['id']}"] = False
                                st.rerun()
            
            # AddNewIssue
            st.markdown("---")
            st.markdown("#### ➕ AddNewIssue")
            
            with st.form("add_question_form"):
                new_question_text = st.text_area(
                    "IssueContent *",
                    placeholder="Please enter new question...",
                    height=100
                )
                
                new_category = st.selectbox(
                    "Question Category *",
                    options=["Cooperation History", "Products & Services", "Challenges & Issues", "Key Contacts", "Future Plans", "Resource Needs"],
                    index=0
                )
                
                new_description = st.text_area(
                    "Question Description (Optional)",
                    placeholder="Please enter question description...",
                    height=60
                )
                
                if st.form_submit_button("➕ AddIssue", type="primary"):
                    if new_question_text:
                        # AddNewIssue
                        add_data = {
                            "question_text": new_question_text,
                            "category": new_category,
                            "description": new_description if new_description else None
                        }
                        
                        result = make_api_request(
                            "POST",
                            "/questions/",
                            add_data
                        )
                        
                        if "error" not in result:
                            st.success("IssueAddSuccess！")
                            st.rerun()
                        else:
                            st.error(f"AddFailure: {result['error']}")
                    else:
                        st.warning("Please enterIssueContent")
    
    # Country Management (only visible to administrators)
    if st.session_state.get("user_info", {}).get("is_admin", False):
        st.subheader("🌍 CountryManage")
        
        # Get current country list
        if st.button("🔄 RefreshCountryList"):
            st.rerun()
        
        # Use unified country list function
        countries = get_countries_list()
            
        if countries:
            st.success(f"Currently have {len(countries)} countries")
            
            # Display country list
            st.markdown("#### 📋 CountryList")
            
            for i, country in enumerate(countries):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"🌍 {country}")
                
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_country_{i}"):
                        st.session_state[f"confirm_delete_country_{i}"] = True
                        st.rerun()
                
                # DeleteConfirm
                if st.session_state.get(f"confirm_delete_country_{i}", False):
                    st.warning(f"⚠️ ConfirmDeleteCountry '{country}'？")
                    
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("✅ ConfirmDelete", key=f"confirm_delete_country_btn_{i}", type="primary"):
                            result = make_api_request("DELETE", f"/countries/?country_name={country}")
                            if "error" not in result:
                                st.success(f"Country '{country}' deleted")
                                del st.session_state[f"confirm_delete_country_{i}"]
                                st.rerun()
                            else:
                                st.error(f"DeleteFailure: {result['error']}")
                    
                    with col_cancel:
                        if st.button("❌ Cancel", key=f"cancel_delete_country_{i}"):
                            del st.session_state[f"confirm_delete_country_{i}"]
                            st.rerun()
                
                st.divider()
            
        else:
            st.info("No country data available")
        
        # Add new country (unified placement outside)
        st.markdown("#### ➕ AddNewCountry")
        
        with st.form("add_country_form"):
            new_country = st.text_input(
                "Country Name",
                placeholder="Please enter country name...",
                help="Add new country to the optional list"
            )
            
            if st.form_submit_button("➕ AddCountry", type="primary"):
                if new_country.strip():
                    add_data = {"country_name": new_country.strip()}
                    
                    result = make_api_request("POST", "/countries/", add_data)
                    
                    if "error" not in result:
                        st.success(f"Country '{new_country}' AddSuccess！")
                        st.rerun()
                    else:
                        st.error(f"AddFailure: {result['error']}")
                else:
                    st.warning("Please enter country name")
    else:
        st.info("🔒 Country management feature is only visible to administrators")
    
    # System information
    st.subheader("ℹ️ System Information")
    
    st.write("**Version:** 1.0.0")
    st.write("**API Address:** http://localhost:8000")
    st.write("**DataLibrary:** SQLite")
    st.write("**AIModel:** gpt-5-mini")

if __name__ == "__main__":
    main()
