import streamlit as st
import pandas as pd
from openai import AzureOpenAI
import ast
import re

# Load patient dataset
@st.cache_data
def load_data():
    return pd.read_csv('reduced_data.csv')

df = load_data()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Ensure patient + prompt are available
if 'prompt' not in st.session_state:
    st.session_state.patient = df.sample(1).iloc[0]
    patient = st.session_state.patient
    procedures = ast.literal_eval(patient['Procedure'])

    st.session_state.prompt = f"""
You are a {patient['Age']} years old {patient['Gender']} patient currently at the hospital undergoing {procedures[0]} for your condition, {patient['Condition']}.
The nurse (the student) is here to take care of you, follow protocol, and reassure you.

You should express emotions based on your risk score ({patient['Length_of_Stay']} days in hospital):
- If it's high, show fear, anxiety, or uncertainty.
- If it's low, be calm, cooperative, and trusting.

If you have been readmitted ({patient['Readmission']}), express familiarity with the procedure. Otherwise, ask more questions.

Your past experience with medical care has been rated as {patient['Satisfaction']} out of 5.

BEHAVIOR RULES:
- Speak like a real patient: short, emotional, human-like sentences.
- DO NOT give any feedback or summary unless explicitly asked.
- NEVER simulate the nurse or continue the conversation yourself.
- Do NOT include any internal thoughts like <think> or [thinking].
- Only respond to the most recent nurse message — one reply per turn.
- If the nurse is rude or dismissive, react emotionally and appropriately.
- When asked for feedback, evaluate:
  - reassurance
  - clarity
  - empathy
"""
else:
    patient = st.session_state.patient

# App UI
st.title("EmpathAI")
st.caption("Powered by Azure OpenAI (GPT-4)")

with st.expander("Show Patient Details", expanded=False):
    st.write("**Patient Data:**")
    st.dataframe(patient.to_frame().T)

# Reset patient
if st.button("🔄 Load New Patient"):
    st.session_state.messages = []
    del st.session_state.prompt
    del st.session_state.patient
    st.rerun()

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Input from user (nurse)
user_input = st.chat_input("Ask the patient something...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    client = AzureOpenAI(
        api_key="9Wd2OvAD0yNGtkfySEjbehqzE35wbgK6Uoo0JbQIcz5W7MPVpEteJQQJ99BEACfhMk5XJ3w3AAAAACOGDLCG",  # Replace with your actual key
        api_version="2024-04-01-preview",
        azure_endpoint="https://fabia-max2y4dm-swedencentral.cognitiveservices.azure.com/"
    )

    try:
        response = client.chat.completions.create(
            model="gptpatient",  
            messages=[
                {"role": "system", "content": st.session_state.prompt},
                *[
                    {"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]}
                    for msg in st.session_state.messages[-4:]
                ]
            ],
            temperature=0.9,
            max_tokens=400
        )

        reply = response.choices[0].message.content

        # Make sure no reasoning or internal thoughts are included
        reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL)
        reply = re.sub(r"\[.*?thinking.*?\]", "", reply, flags=re.IGNORECASE).strip()

        st.chat_message("assistant").markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        st.error(f"Azure OpenAI error: {e}")

# End conversation button (not working yet)
if st.button("💬 End Conversation and Request Feedback"):
    st.session_state.messages.append({
        "role": "user",
        "content": "Can you give me feedback about how I did as a nurse today?"
    })
    st.rerun()
