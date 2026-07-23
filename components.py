import streamlit as st
import json
from database import load_scenarios, save_scenarios

@st.dialog("Manage Scenarios")
def admin_dashboard():
    scenarios = load_scenarios()
    
    st.subheader("Current Scenarios")
    for i, scen in enumerate(scenarios):
        with st.expander(f"Scenario {i+1}: {scen['title']}"):
            new_title = st.text_input("Title", scen['title'], key=f"title_{i}")
            new_setup = st.text_area("Setup", scen['setup'], key=f"setup_{i}")
            new_output = st.text_area("Code Output", scen['output'], key=f"output_{i}")
            new_prompt = st.text_area("Prompt", scen['prompt'], key=f"prompt_{i}")
            
            st.markdown("**Options (Edit JSON below):**")
            options_str = st.text_area("Options JSON", json.dumps(scen['options'], indent=2), height=200, key=f"options_{i}")
            
            if st.button("Save Changes", key=f"save_{i}"):
                try:
                    new_options = json.loads(options_str)
                except json.JSONDecodeError:
                    st.error("Invalid JSON format for options.")
                    new_options = scen['options'] 
                
                scenarios[i]['title'] = new_title
                scenarios[i]['setup'] = new_setup
                scenarios[i]['output'] = new_output
                scenarios[i]['prompt'] = new_prompt
                scenarios[i]['options'] = new_options
                save_scenarios(scenarios)
                st.rerun()
            
            if st.button("Delete Scenario", key=f"del_{i}", type="secondary"):
                scenarios.pop(i)
                save_scenarios(scenarios)
                st.rerun()

    st.divider()
    st.subheader("Manually Add New Scenario")
    new_s_title = st.text_input("New Title", key="new_title")
    new_s_setup = st.text_area("New Setup", key="new_setup")
    new_s_output = st.text_area("New Code Output", key="new_output")
    new_s_prompt = st.text_area("New Prompt", key="new_prompt")
    
    if st.button("Add Scenario", type="primary"):
        new_scen = {
            "title": new_s_title,
            "setup": new_s_setup,
            "output": new_s_output,
            "prompt": new_s_prompt,
            "options": {
                "A": {"text": "Option A", "result": "Result A"},
                "B": {"text": "Option B", "result": "Result B"},
                "C": {"text": "Option C", "result": "Result C"}
            }
        }
        scenarios.append(new_scen)
        save_scenarios(scenarios)
        st.rerun()

import yaml

@st.dialog("🔑 Save Your NVIDIA API Key")
def api_key_manager(authenticator, config):
    st.write("Paste your NVIDIA API Key here. It will be securely saved to your profile so you don't have to enter it every time.")
    new_key = st.text_input("NVIDIA API Key", type="password")
    
    if st.button("Save Key"):
        if new_key:
            # Find the current logged-in user and save the key to their profile
            username = st.session_state.get("username")
            if username:
                # Update the config dictionary in memory
                config['credentials']['usernames'][username]['api_key'] = new_key
                
                # Save the updated config back to the YAML file
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file)
                    
                st.success("API Key saved successfully! Please refresh the app to apply it.")
                st.rerun()
        else:
            st.error("Please enter a valid key.")