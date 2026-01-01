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
        html_body = markdown.markdown(text_content, extensions=['tables'])
        return f"<html><body>{html_body}</body></html>" # Simplified for brevity

    def create_word_doc(text_content):
        doc = Document()
        doc.add_heading('Rewritten Resume (Draft)', 0)
        for line in text_content.split('\n'):
            doc.add_paragraph(line)
        doc_filename = "Rewritten_Resume.docx"
        doc.save(doc_filename)
        return doc_filename

    # --- MAIN UI STARTS HERE ---
    
    # 1. SIDEBAR PROFILE SYSTEM (The "Digital Open Door")
    with st.sidebar:
        st.image("logo_v2.png", width=200) # Assuming you have the logo
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
        if user_data['tier'] == "premium":
            st.success("💎 Unlimited Tokens")
        else:
            st.warning(f"🪙 Tokens: {user_data['tokens']}")
            
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

    # 2. MAIN HEADER & DYNAMIC BANNER
    col1, col2 = st.columns([2, 5]) 
    with col2:
        st.title("Career Pivot AI")
    
    # --- DYNAMIC BANNER LOGIC ---
    # Only show "Premium Unlocked" if they are actually Premium
    if user_data['tier'] == 'premium':
        st.markdown("### ✨ Premium Access Unlocked")
    elif user_data['tier'] == 'basic':
        st.markdown("### ✅ Basic Access Active (Upgrade for Resume Rewrite)")
    else:
        st.markdown("### 🆓 Free Trial Mode (3 Tokens)")

    uploaded_file = st.file_uploader("Upload Client Resume (PDF)", type=["pdf"])

    if uploaded_file is not None:
        tab1, tab2, tab3 = st.tabs(["📊 1. Strategy Report", "📝 2. Resume Rewrite", "🚀 3. Job Hunter"])
        
        client = genai.Client(api_key=api_key)

        # --- TAB 1: STRATEGY (Uses Tokens) ---
        with tab1:
            st.header("Step 1: The Strategy")
            st.write(f"Cost: 1 Token (Your Balance: {user_data['tokens']})")
            
            if st.button("Generate Strategy Report", key="btn_strategy"):
                # SECURITY CHECK: Do they have tokens?
                if sec.deduct_token(current_email):
                    with st.spinner("Auditing Resume..."):
                        try:
                            # ... (Your existing AI Code for Strategy) ...
                            temp_filename = "temp_resume.pdf"
                            with open(temp_filename, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            file_ref = client.files.upload(file=temp_filename)
                            
                            prompt_strategy = "Create a Career Pivot Strategy Report." # Shortened for brevity
                            response = client.models.generate_content(model="gemini-2.0-flash", contents=[file_ref, prompt_strategy])
                            
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
            
            # LOGIC: Check Tier
            is_premium_user = sec.is_premium(current_email)
            
            if is_premium_user:
                # --- PREMIUM VIEW ---
                st.success("🔓 Premium Feature Unlocked")
                if st.button("Draft New Resume (.docx)", key="btn_rewrite"):
                    with st.spinner("Rewriting Resume..."):
                        # ... (Your existing AI Code for Resume) ...
                        # (I've kept this brief, paste your original prompt/code here if needed)
                        st.write("Generating Premium Resume...") 
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
            # ... (Your existing Job Hunter code remains the same) ...
            st.write("Job search tools are free for all users.")
            target_role = st.text_input("Target Role", value="Data Center Technician")
            st.link_button("Search LinkedIn", f"https://www.linkedin.com/jobs/search/?keywords={target_role}")