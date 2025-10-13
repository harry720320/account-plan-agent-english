"""
Unified application entry point
Handles switching between login and main application
"""
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Strategic Account Plan AI Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main function"""
    # Check if main application should be displayed
    if st.session_state.get("show_main_app", False):
        # Import and run main application
        import streamlit_app
        streamlit_app.main()
    else:
        # Show login page
        import login_page
        login_page.show_login_page()

if __name__ == "__main__":
    main()
