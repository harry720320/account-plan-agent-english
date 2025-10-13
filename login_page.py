"""
Login page
Provides user login interface
"""
import streamlit as st
import requests
import json
from typing import Dict, Any

# API base URL
API_BASE_URL = "http://localhost:8000"

def make_api_request(method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
    """Send API request"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API request failed: {response.status_code} - {response.text}"}
    
    except Exception as e:
        return {"error": f"Request error: {str(e)}"}

def show_login_page():
    """Display login page"""
    st.title("🔐 User Login")
    st.markdown("---")
    
    # Check if already logged in
    if "access_token" in st.session_state and "user_info" in st.session_state:
        st.success(f"Welcome back, {st.session_state.user_info['username']}!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🏠 Enter System", type="primary"):
                st.session_state.show_main_app = True
                st.rerun()
        
        with col2:
            if st.button("🔑 Change Password"):
                st.session_state.show_change_password = True
        
        with col3:
            if st.button("👥 User Management", disabled=not st.session_state.user_info.get('is_admin', False)):
                st.session_state.show_user_management = True
        
        # Show change password interface
        if st.session_state.get("show_change_password", False):
            show_change_password_form()
        
        # Display user management interface
        if st.session_state.get("show_user_management", False):
            show_user_management()
        
        if st.button("🚪 Logout"):
            # ClearLoginState
            for key in ["access_token", "user_info", "show_change_password", "show_user_management"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        return
    
    # Login form
    with st.form("login_form"):
        st.subheader("Please Enter Login Info")
        
        username = st.text_input("Username", placeholder="Please Enter Username")
        password = st.text_input("Password", type="password", placeholder="Please Enter Password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            login_button = st.form_submit_button("🔑 Login", type="primary")
        
        with col2:
            register_button = st.form_submit_button("📝 Register", disabled=True)  # Temporarily disabled registration
        
        if login_button:
            if not username or not password:
                st.error("Please enter username and password")
            else:
                with st.spinner("Logging in..."):
                    login_data = {
                        "username": username,
                        "password": password
                    }
                    
                    result = make_api_request("POST", "/auth/login", login_data)
                    
                    if "error" not in result:
                        # Login successful, save user information
                        st.session_state.access_token = result["access_token"]
                        st.session_state.user_info = result["user"]
                        
                        st.success(f"Login successful! Welcome, {result['user']['username']}")
                        st.rerun()
                    else:
                        st.error(f"LoginFailure: {result['error']}")
        
        if register_button:
            st.info("Registration feature is not yet available, please contact administrator")

def show_change_password_form():
    """Display change password form"""
    st.markdown("---")
    st.subheader("🔑 ModifyPassword")
    
    with st.form("change_password_form"):
        old_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("NewPassword", type="password")
        confirm_password = st.text_input("ConfirmNewPassword", type="password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            save_button = st.form_submit_button("💾 Save", type="primary")
        
        with col2:
            cancel_button = st.form_submit_button("❌ Cancel")
        
        if save_button:
            if not old_password or not new_password or not confirm_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("New password and confirm password do not match")
            elif len(new_password) < 6:
                st.error("New password must be at least 6 characters long")
            else:
                with st.spinner("Changing password..."):
                    headers = {
                        "Authorization": f"Bearer {st.session_state.access_token}"
                    }
                    
                    change_data = {
                        "old_password": old_password,
                        "new_password": new_password
                    }
                    
                    result = make_api_request("POST", "/auth/change-password", change_data, headers)
                    
                    if "error" not in result:
                        st.success("PasswordModifySuccess！")
                        st.session_state.show_change_password = False
                        st.rerun()
                    else:
                        st.error(f"PasswordModifyFailure: {result['error']}")
        
        if cancel_button:
            st.session_state.show_change_password = False
            st.rerun()

def show_user_management():
    """Display user management interface"""
    st.markdown("---")
    st.subheader("👥 User Management")
    
    # Get user list
    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }
    
    with st.spinner("Loading user list..."):
        result = make_api_request("GET", "/auth/users", headers=headers)
        
        if "error" not in result:
            users = result
            
            # Display user list
            for user in users:
                with st.expander(f"👤 {user['username']} {'(Administrator)' if user['is_admin'] else ''}"):
                    st.write(f"**User ID:** {user['id']}")
                    st.write(f"**Username:** {user['username']}")
                    st.write(f"**Administrator:** {'Yes' if user['is_admin'] else 'No'}")
                    st.write(f"**State:** {'Active' if user['is_active'] else 'Disabled'}")
                    st.write(f"**Created Time:** {user['created_at']}")
            
            # Create new user form
            st.markdown("### 📝 Create New User")
            
            with st.form("create_user_form"):
                new_username = st.text_input("NewUsername")
                new_password = st.text_input("NewPassword", type="password")
                is_admin = st.checkbox("Administrator Permission")
                
                create_button = st.form_submit_button("➕ Create User", type="primary")
                
                if create_button:
                    if not new_username or not new_password:
                        st.error("Please enter username and password")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        with st.spinner("Creating user..."):
                            create_data = {
                                "username": new_username,
                                "password": new_password,
                                "is_admin": is_admin
                            }
                            
                            result = make_api_request("POST", "/auth/create-user", create_data, headers)
                            
                            if "error" not in result:
                                st.success(f"User {new_username} created successfully!")
                                st.rerun()
                            else:
                                st.error(f"Create user failed: {result['error']}")
        else:
            st.error(f"Get user list failed: {result['error']}")

if __name__ == "__main__":
    show_login_page()
