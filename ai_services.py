import json
from openai import OpenAI

def generate_ai_scenarios(api_key, num_scenarios, tech_sector):
    try:
        client = OpenAI(
          base_url = "https://integrate.api.nvidia.com/v1",
          api_key = api_key
        )
        
        sector_instruction = ""
        if tech_sector != "General Tech (All Sectors)":
            sector_instruction = f"ALL scenarios must be strictly focused on the domain of {tech_sector}. The challenges, tools, and career archetypes tested must only be relevant to {tech_sector}."
        
        prompt = f"""
        You are an expert tech career assessor. Generate exactly {num_scenarios} short, interactive scenarios to help someone figure out their ideal tech career.
        
        {sector_instruction}
        
        **CRITICAL RULE:** As the number of scenarios increases, they must form an escalating, interconnected narrative. Scenario 2 should build on the consequences of Scenario 1, etc. They should feel like one continuous day at a tech company.
        
        Each scenario must test 3 different approaches (Options A, B, and C) representing different sub-career paths.
        
        You MUST return your response as a valid JSON array of objects. Do not include any markdown formatting or extra text, ONLY the JSON array.
        
        Each object in the array must have this exact structure:
        {{
          "title": "Short Title",
          "setup": "Brief setup of the situation",
          "output": "A snippet of code, terminal output, or data. Leave as empty string '' if not applicable.",
          "prompt": "The question asking what their first instinct is.",
          "options": {{
            "A": {{"text": "Option A text", "result": "What choosing this reveals about their archetype."}},
            "B": {{"text": "Option B text", "result": "What choosing this reveals about their archetype."}},
            "C": {{"text": "Option C text", "result": "What choosing this reveals about their archetype."}}
          }}
        }}
        """
        
        completion = client.chat.completions.create(
          model="thinkingmachines/inkling",
          messages=[{"role":"user","content":prompt}],
          temperature=1,
          top_p=0.95,
          max_tokens=8192,
          stream=False
        )
        
        ai_response = completion.choices[0].message.content
        
        if not ai_response:
            return None, "The AI returned an empty response."
            
        if "```json" in ai_response:
            ai_response = ai_response.replace("```json", "").replace("```", "").strip()
            
        new_scenarios = json.loads(ai_response)
        return new_scenarios, None
        
    except Exception as e:
        return None, str(e)

def generate_final_profile(api_key, user_choices):
    try:
        client = OpenAI(
          base_url = "https://integrate.api.nvidia.com/v1",
          api_key = api_key
        )
        
        prompt = f"""
        A user just took a tech career assessment quiz. 
        Here are the results of their choices: {user_choices}.
        
        Based on these choices, write a highly personalized, encouraging summary of what specific tech career path they are best suited for. 
        Mention their specific strengths and give them an archetype title. 
        Keep it under 150 words.
        """
        
        completion = client.chat.completions.create(
          model="thinkingmachines/inkling",
          messages=[{"role":"user","content":prompt}],
          temperature=1,
          top_p=0.95,
          max_tokens=8192,
          stream=False
        )
        
        return completion.choices[0].message.content, None
        
    except Exception as e:
        return None, str(e)

def generate_learning_roadmap(api_key, user_choices, tech_sector="General Tech"):
    try:
        client = OpenAI(
          base_url = "https://integrate.api.nvidia.com/v1",
          api_key = api_key
        )
        
        prompt = f"""
        A user just completed a tech career assessment quiz for the {tech_sector} sector.
        Here are their choices and their inferred talents: {user_choices}.
        
        Based on their specific profile, create a personalized 3-month learning and advancing roadmap to help them get started or level up in this career path.
        
        Format the roadmap using Markdown with clear headings:
        - **Month 1: Foundations** (What core concepts/tools to learn)
        - **Month 2: Hands-On Projects** (Specific project ideas they should build based on their instinct profile)
        - **Month 3: Portfolio & Advancement** (How to showcase their skills and what communities/certifications to pursue)
        
        Keep it actionable, realistic, and highly tailored to their specific archetype results.
        """
        
        completion = client.chat.completions.create(
          model="thinkingmachines/inkling",
          messages=[{"role":"user","content":prompt}],
          temperature=1,
          top_p=0.95,
          max_tokens=8192,
          stream=False
        )
        
        return completion.choices[0].message.content, None
        
    except Exception as e:
        return None, str(e)    