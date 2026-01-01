import streamlit as st
from datetime import datetime

# <--- PASTE THE DICTIONARY RIGHT HERE --- >
DEFAULT_USER_PROFILE = {
    "full_name": "",
    "email": "",
    "phone": "",
    "linkedin_url": "",
    "current_role": "",         
    "target_role": "",          
    "years_experience": 0,      
    "target_industry": "",      
    "pivot_motivation": "",     
    "hard_skills": [],          
    "soft_skills": [],          
    "certifications": [],       
    "desired_salary": "",       
    "location_preference": "",  
    "onboarding_complete": False 
}
# <--- END PASTE --- >

# --- MOCK DATABASE (In a real app, this connects to SQL/Firebase) ---
# We use Streamlit's session state to persist data while the app is running.
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {
        "demo@bizy.com": {
            "tier": "basic", 
            "tokens": 5, 
            "joined": "2025-01-01"
        },
        "vip@bizy.com": {
            "tier": "premium", 
            "tokens": 9999, 
            "joined": "2025-01-01"
        }
    }

def get_user(email):
    """Retrieves user profile or creates a new one with 3 FREE tokens."""
    db = st.session_state["user_db"]
    
    if email not in db:
        # NEW USER: Grant Free Trial
        db[email] = {"tier": "free", "tokens": 3, "joined": str(datetime.now())}
    
    return db[email]

def upgrade_user(email, new_tier):
    """Simulates a payment upgrade."""
    db = st.session_state["user_db"]
    if email in db:
        db[email]["tier"] = new_tier
        if new_tier == "premium":
            db[email]["tokens"] = 9999 # Unlimited
        elif new_tier == "basic":
            db[email]["tokens"] += 10 # Add 10 tokens
    return db[email]

def deduct_token(email):
    """Attempts to spend 1 token. Returns True if successful."""
    user = get_user(email)
    
    # Premium users never run out
    if user["tier"] == "premium":
        return True
    
    # Check balance for Free/Basic
    if user["tokens"] > 0:
        st.session_state["user_db"][email]["tokens"] -= 1
        return True
    
    return False

def is_premium(email):
    """Simple check for UI locking."""
    user = get_user(email)
    return user["tier"] == "premium"