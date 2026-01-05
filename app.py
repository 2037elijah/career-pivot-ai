import streamlit as st
import os
import markdown
from dotenv import load_dotenv
from google import genai
from docx import Document
import bizy_security as sec  # IMPORTING YOUR NEW SECURITY FILE

# 1. Load Keys
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# --- BRANDING CONFIGURATION ---
st.set_page_config(
    page_title="Career Pivot AI",
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CLEANUP CSS ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* Custom Style for Locked Buttons */
            .locked-button { opacity: 0.6; cursor: not-allowed; background-color: #eee; }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- PASSWORD PROTECTION (The Front Door) ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == "PIVOT2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔑 Enter Access Code (From your Gumroad Receipt):", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔑 Enter Access Code:", type="password", on_change=password_entered, key="password")
        st.error("😕 Access code incorrect")
        return False
    else:
        return True

if check_password():
    # --- HELPER FUNCTIONS ---
    def clean_text(text):
        text = text.replace("```markdown", "").replace("```", "")
        return text.strip()

    def create_html_report(text_content):
        html_content = f"<html><body>{text_content}</body></html>"
        html_filename = "career_pivot_report.html"
        with open(html_filename, "w") as f:
            f.write(html_content)
        return html_filename

    def create_word_doc(text_content):
        doc = Document()
        doc.add_paragraph(text_content)
        doc_filename = "career_pivot_resume.docx"
        doc.save(doc_filename)
        return doc_filename

    def render_onboarding():
        """Renders a form to collect user data before they access the tools."""
        st.markdown("## 🚀 Let's Build Your Career Profile")
        st.info("Complete your profile to unlock your 3 Free Tokens and custom AI strategies.")
        
        with st.form("onboarding_form"):
            c1, c2 = st.columns(2)
            with c1:
                full_name = st.text_input("Full Name", placeholder="Elijah Michael")
                current_role = st.text_input("Current Job Title", placeholder="e.g., Retail Associate")
                years_exp = st.number_input("Years of Work Experience", min_value=0, max_value=50, value=2)
            
            with c2:
                target_role = st.text_input("Target Job Title", placeholder="e.g., Cyber Analyst")
                target_industry = st.selectbox("Target Industry", ["Tech/IT", "Healthcare", "Finance", "Construction", "Other"])
                motivation = st.selectbox("Why are you pivoting?", ["Seeking Higher Pay", "Want Remote Work", "Better Culture", "Career Growth"])

            st.markdown("### 🛠️ Skills & Logistics")
            skills = st.multiselect("Select your Top Skills (Transferable & Technical)", 
                                   ["Customer Service", "Management", "Python", "SQL", "Project Management", 
                                    "Troubleshooting", "Sales", "Public Speaking", "Microsoft Office"])
            
            relocation = st.radio("Work Preference", ["Remote", "Hybrid", "On-site"], horizontal=True)
            
            submitted = st.form_submit_button("💾 Save Profile & Unlock Tools")
            
            if submitted:
                # SAVE DATA TO SESSION STATE
                st.session_state["user_profile"] = {
                    "full_name": full_name,
                    "current_role": current_role,
                    "target_role": target_role,
                    "pivot_motivation": motivation,
                    "skills": skills,
                    "preference": relocation,
                    "onboarding_complete": True
                }
                st.success("Profile Saved! Reloading...")
                st.rerun()

    # --- MAIN UI STARTS HERE ---
    
    # 1. GATEKEEPER CHECK: Has the user completed onboarding?
    if "user_profile" not in st.session_state:
        render_onboarding() # Show form
        st.stop() # Stop here. Do not load the dashboard yet.

    # 2. SIDEBAR PROFILE SYSTEM (The "Digital Open Door")
    with st.sidebar:
        # st.image("logo_v2.png", width=200) # Uncomment if you have the logo
        st.divider()
        st.markdown("### 👤 User Profile")
        
        # User "Login" to track tokens
        if "user_email" not in st.session_state:
            st.session_state["user_email"] = "guest"
            
        user_email = st.text_input("Enter Email to Load Profile:", value=st.session_state.get("user_email_input", ""))
        
        if st.button("Load / Create Profile"):
            st.session_state["user_email"] = user_email
            st.rerun()
            
        # Get Current User Data
        current_email = st.session_state["user_email"]
        user_data = sec.get_user(current_email)
        
        # Display Wallet
        st.info(f"**Plan:** {user_data['tier'].upper()}")
        
        # 1. CREATE A PLACEHOLDER (An empty box we can update later)
        token_display = st.empty() 
        
        if user_data['tier'] == "premium":
            token_display.success("💎 Unlimited Tokens")
        else:
            # Draw the initial value
            token_display.warning(f"🪙 Tokens: {user_data['tokens']}")
            
        # UPGRADE SIMULATOR (For Testing)
        st.divider()
        st.markdown("### 🛠️ Admin / Upgrade Test")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Buy Basic ($29)"):
                sec.upgrade_user(current_email, "basic")
                st.rerun()
        with c2:
            if st.button("Buy Premium ($49)"):
                sec.upgrade_user(current_email, "premium")
                st.rerun()

    # 3. MAIN HEADER & DYNAMIC BANNER
    col1, col2 = st.columns([2, 5]) 
    with col2:
        st.title("Career Pivot AI")
        st.caption("🤖 **The Logic:** If an AI can't read your resume, a human recruiter never will. We fix that.")
    
    # --- DYNAMIC BANNER LOGIC ---
    if user_data['tier'] == 'premium':
        st.markdown("### ✨ Premium Access Unlocked")
    elif user_data['tier'] == 'basic':
        st.markdown("### ✅ Basic Access Active (Upgrade for Resume Rewrite)")
    else:
        st.markdown("### 🆓 Free Trial Mode (3 Tokens)")

    st.markdown("---")
    st.markdown("### 1️⃣ Start Here")
    st.write("Upload your current resume to unlock the Strategy and Rewrite tools.")
    uploaded_file = st.file_uploader("Upload Client Resume (PDF)", type=["pdf"], label_visibility="collapsed")

    if uploaded_file is not None:
        tab1, tab2, tab3 = st.tabs(["📊 1. Strategy Report", "📝 2. Resume Rewrite", "🚀 3. Job Hunter"])
        
        client = genai.Client(api_key=api_key)

        # --- TAB 1: STRATEGY (Uses Tokens) ---
        with tab1:
            st.header("Step 1: The Strategy")
            st.info("💡 **Instructions:** Click the button below to audit your resume against ATS bots and generate a pivot roadmap.")
            
            st.write(f"Cost: 1 Token (Your Balance: {user_data['tokens']})")
            
            if st.button("Generate Strategy Report", key="btn_strategy"):
                # SECURITY CHECK: Do they have tokens?
                if sec.deduct_token(current_email):

                    user_data = sec.get_user(current_email) # Get new balance (2)
                    token_display.warning(f"🪙 Tokens: {user_data['tokens']}")

                    with st.spinner("Auditing Resume..."):
                        try:
                            temp_filename = "temp_resume.pdf"
                            with open(temp_filename, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            file_ref = client.files.upload(file=temp_filename)
                            
                            # USES THE NEW PROFILE DATA IN THE PROMPT!
                            profile = st.session_state["user_profile"]
                            prompt_strategy = f"""
                            Role: Senior Tech Recruiter.
                            Candidate: {profile['full_name']} moving from {profile['current_role']} to {profile['target_role']}.
                            Motivation: {profile['pivot_motivation']}.
                            Task: Create a Career Pivot Strategy Report.
                            """
                            response = client.models.generate_content(model="gemini-flash-latest", contents=[file_ref, prompt_strategy])
                            
                            st.success("Strategy Ready! (1 Token deducted)")
                            st.markdown(clean_text(response.text))
                            os.remove(temp_filename)
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.error("❌ Not enough tokens! Please upgrade your plan in the sidebar.")

        # --- TAB 2: REWRITE (HARD LOCKED for Basic/Free) ---
        with tab2:
            st.header("Step 2: The Rewrite")
            st.info("📝 **Instructions:** We will rewrite your resume using keywords from your target industry to maximize your approval odds.")
            
            # LOGIC: Check Tier
            is_premium_user = sec.is_premium(current_email)
            
            if is_premium_user:
                # --- PREMIUM VIEW ---
                st.success("🔓 Premium Feature Unlocked")
                if st.button("Draft New Resume (.docx)", key="btn_rewrite"):

                    user_data = sec.get_user(current_email) # Get new balance (2)
                    token_display.warning(f"🪙 Tokens: {user_data['tokens']}")

                    with st.spinner("Rewriting Resume..."):
                         try:
                            temp_filename = "temp_resume.pdf"
                            with open(temp_filename, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            file_ref = client.files.upload(file=temp_filename)
                            
                            # USES THE NEW PROFILE DATA
                            profile = st.session_state["user_profile"]
                            prompt_rewrite = f"""
                            Role: Professional Resume Writer.
                            Task: Rewrite resume for {profile['target_role']} in {profile['target_industry']}.
                            Highlight Skills: {', '.join(profile['skills'])}.
                            """
                            response = client.models.generate_content(model="gemini-flash-latest", contents=[file_ref, prompt_rewrite])
                            
                            st.success("Resume Drafted!")
                            clean_response = clean_text(response.text)
                            docx_file = create_word_doc(clean_response)
                            with open(docx_file, "rb") as f:
                                st.download_button("📥 Download Word Doc", f, "Rewritten_Resume.docx")
                            os.remove(temp_filename)
                         except Exception as e:
                            st.error(f"Error: {e}")
            else:
                # --- LOCKED VIEW ---
                st.warning("🔒 This feature is locked.")
                st.markdown("### Upgrade to Premium ($49) to unlock:")
                st.markdown("- ✍️ Full AI Resume Rewrite\n- 🔄 Unlimited Revisions\n- 📥 Word Doc Download")
                
                # Mock "Greyed Out" Button
                st.button("Draft New Resume (.docx)", key="btn_rewrite_locked", disabled=True)
                st.info("👈 Use the 'Admin / Upgrade Test' in the sidebar to simulate upgrading to Premium.")

        # --- TAB 3: JOB HUNTER ---
        with tab3:
            st.header("Step 3: Launch Your Search")
            st.info("🔎 **Instructions:** These buttons open pre-filtered search feeds for your target role. No typing required.")
            
            st.write("Job search tools are free for all users.")
            
            # Pre-fill these inputs with the Profile Data!
            profile = st.session_state["user_profile"]
            target_role = st.text_input("Target Role", value=profile['target_role'])
            
            st.link_button("Search LinkedIn", f"https://www.linkedin.com/jobs/search/?keywords={target_role}")