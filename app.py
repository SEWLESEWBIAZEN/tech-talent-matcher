import streamlit as st
import streamlit_authenticator as stauth
from constants import list_tech_sectors
from database import load_scenarios, save_scenarios
from ai_services import generate_ai_scenarios, generate_final_profile, generate_learning_roadmap
from components import admin_dashboard
import yaml
from yaml.loader import SafeLoader

# --- AUTHENTICATION SETUP ---
# In a real SaaS, you would store these securely in a database. 
# For Phase 1, we use a local config file to get the app running.
config = {
    'credentials':
    {
        'usernames':
        {
            'admin': {'name': 'Admin User', 'password': ''} # Password will be hashed below
        }
    },
    'cookie': {'name': 'tech_talent', 'key': 'super_secret_key', 'expiry_days': 30}
}

# Load existing credentials if they exist
try:
    with open('config.yaml', 'r') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    # SAFETY CHECK: If old config exists without 'email', force overwrite
    if 'admin' in config.get('credentials', {}).get('usernames', {}):
        if 'email' not in config['credentials']['usernames']['admin']:
            raise FileNotFoundError("Old config format, regenerating.")

except (FileNotFoundError, Exception):
    # Create a fresh, valid config with email
    hashed_password = stauth.Hasher.hash('password')
    
    config = {
        'credentials': {
            'usernames': {
                'admin': {
                    'name': 'Admin', 
                    'password': hashed_password,
                    'email': 'admin@techtalent.com'
                }
            }
        },
        'cookie': {'name': 'tech_talent_v2', 'key': 'super_secret_key', 'expiry_days': 30}
    }
    
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file)

# Initialize authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- PAGE CONFIG ---
st.set_page_config(page_title="Tech Talent Matcher", page_icon="🧠", layout="wide")

# --- LOGIN GATEKEEPER ---
st.session_state['authentication_status'] = st.session_state.get('authentication_status', None)

# 1. Check if the user is logged out. If so, add CSS to center the block.
if not st.session_state.get('authentication_status'):
    st.markdown("""
        <style>
            /* Remove the default Streamlit padding and center the block */
            .block-container {
                padding-top: 5rem !important;
                max-width: 50rem !important; /* Constrain the width to make it centered */
            }
        </style>
    """, unsafe_allow_html=True)

# 2. The Login Box
authenticator.login(location='main')

if st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
    st.subheader("New user? Register here:")
    try:
        if authenticator.register_user(location='main', domains=None):
            st.success('User registered successfully! Please login using the form above.')
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file)
    except Exception as e:
        st.error(f"Error during registration: {e}")

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
    st.subheader("New user? Register here:")
    try:
        if authenticator.register_user(location='main', domains=None):
            st.success('User registered successfully! Please login using the form above.')
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file)
    except Exception as e:
        st.error(f"Error during registration: {e}")

elif st.session_state.get('authentication_status'):
    # 3. If they ARE logged in, reset the CSS so the app can use the whole screen.
    st.markdown("""
        <style>
            .block-container {
                max-width: 80rem !important; /* Restore wide layout for the quiz */
                padding-top: 2rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- MAIN APP UI ---
    st.title("🧠 The Tech Talent Pipeline")
    st.write("Don't know what tech career is right for you? Let's give you a real-world scenario instead of a boring quiz.")

    # Sidebar
    with st.sidebar:
        st.subheader("🛠️ Admin Controls")
        if st.button("Manage Manual Scenarios"):
            admin_dashboard()
            
        st.divider()
        st.subheader("🤖 AI Scenario Generator")
        nvidia_api_key = st.text_input("Enter NVIDIA API Key", type="password")       

        selected_sector = st.selectbox("Which tech sector do you want to test for?", list_tech_sectors())
        num_scenarios = st.number_input("How many scenarios?", min_value=1, max_value=10, value=3)
        
        if st.button("Generate AI Scenarios"):
            if nvidia_api_key:
                with st.spinner(f"AI is generating {num_scenarios} scenarios for {selected_sector}..."):
                    new_scenarios, error = generate_ai_scenarios(nvidia_api_key, int(num_scenarios), selected_sector)
                    if error:
                        st.error(f"Error: {error}")
                    else:
                        save_scenarios(new_scenarios)
                        st.success(f"Generated {num_scenarios} scenarios for {selected_sector}!")
                        st.session_state.clear()
                        st.rerun()
            else:
                st.warning("Please enter your API key first.")
                
        st.divider()
        if st.button("🔄 Reset Quiz"):
            st.session_state.clear()
            st.rerun()
            
        st.divider()
        openai_api_key_final = st.text_input("NVIDIA API Key for Final Profile", type="password")

    # --- RUN THE QUIZ DYNAMICALLY ---
    scenarios = load_scenarios()

    for i in range(len(scenarios)):
        if f"scenario_{i+1}_answer" not in st.session_state:
            st.session_state[f"scenario_{i+1}_answer"] = None

    for i, scen in enumerate(scenarios):
        if i > 0 and st.session_state.get(f"scenario_{i}_answer") is None:
            st.info(f"👆 Answer Scenario {i} to unlock Scenario {i+1}.")
            break
            
        st.header(f"Scenario {i+1}: {scen['title']}")
        st.write(scen['setup'])
        
        if scen['output']:
            st.code(scen['output'], language="text")
            
        st.write(scen['prompt'])
        
        col1, col2, col3 = st.columns(3)
        
        if col1.button(f"A. {scen['options']['A']['text']}", key=f"btn_{i+1}_A"):
            st.session_state[f"scenario_{i+1}_answer"] = "A"
        elif col2.button(f"B. {scen['options']['B']['text']}", key=f"btn_{i+1}_B"):
            st.session_state[f"scenario_{i+1}_answer"] = "B"
        elif col3.button(f"C. {scen['options']['C']['text']}", key=f"btn_{i+1}_C"):
            st.session_state[f"scenario_{i+1}_answer"] = "C"

        answer = st.session_state.get(f"scenario_{i+1}_answer")
        if answer:
            st.success(f"✅ {scen['options'][answer]['result']}")
        
        st.divider()

    # --- FINAL RESULTS PAGE ---
    all_answered = all(st.session_state.get(f"scenario_{i+1}_answer") is not None for i in range(len(scenarios)))

    if all_answered and len(scenarios) > 0:
        st.header("📊 Your Tech Talent Profile")

        user_choices = []
        for i, scen in enumerate(scenarios):
            ans = st.session_state.get(f"scenario_{i+1}_answer")
            if ans and ans in scen['options']:
                user_choices.append(f"Scenario {i+1}: {scen['title']} -> User chose: {scen['options'][ans]['result']}")

        # 1. First, generate the Archetype Profile
        if openai_api_key_final:
            with st.spinner("AI is analyzing your tech archetype..."):
                ai_summary, error = generate_final_profile(openai_api_key_final, user_choices)
                if error:
                    st.error(f"Error generating AI summary: {error}")
                else:
                    st.success("🎯 Your AI-Generated Tech Archetype:")
                    st.markdown(ai_summary)
                    st.divider()
                    
                    # 2. Now, add the Roadmap Generator Button
                    if "roadmap_generated" not in st.session_state:
                        if st.button("🗺️ Generate a 3-Month Learning Roadmap"):
                            st.session_state.roadmap_generated = True
                    
                    # 3. Display the Roadmap if the button was clicked
                    if st.session_state.get("roadmap_generated"):
                        with st.spinner("AI is building your personalized learning roadmap..."):
                            roadmap, road_error = generate_learning_roadmap(openai_api_key_final, user_choices)
                            if road_error:
                                st.error(f"Error generating roadmap: {road_error}")
                            else:
                                st.subheader("🚀 Your Personalized Advancement Roadmap")
                                st.markdown(roadmap)
        else:
            st.warning("👆 Please enter your API key in the sidebar to generate your personalized AI career profile.")
    st.write(f'Welcome *{st.session_state["name"]}*')
    authenticator.logout('Logout', 'main')