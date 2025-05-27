from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import ast
import re
from openai import AzureOpenAI

print("Flask app is starting...")
app = Flask(__name__)
CORS(app)

# Azure OpenAI client setup
client = AzureOpenAI(
    api_key="9Wd2OvAD0yNGtkfySEjbehqzE35wbgK6Uoo0JbQIcz5W7MPVpEteJQQJ99BEACfhMk5XJ3w3AAAAACOGDLCG",  
    api_version="2024-04-01-preview",
    azure_endpoint="https://fabia-max2y4dm-swedencentral.cognitiveservices.azure.com/"
)

# Returns a random patient and system prompt
@app.route("/new-patient", methods=["GET"])
def get_new_patient():
    try:
        df = pd.read_csv('reduced_data.csv')  # Always reload to get fresh sample
        patient = df.sample(1).iloc[0]
        procedures = ast.literal_eval(patient['Procedure'])

        prompt = f"""You are a {patient['Age']} years old {patient['Gender']} patient currently at the hospital undergoing {procedures[0]} for your condition, {patient['Condition']}.
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

        return jsonify({
            "prompt": prompt,
            "patient": patient.to_dict()
        })
    except Exception as e:
        return jsonify({"error": f"Error generating patient: {str(e)}"}), 500


#  POST /chat - Sends conversation to Azure and returns patient response
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages")

    print("\n Received messages:")
    for msg in messages:
        print(f"{msg['role']}: {msg['content']}")

    if not messages:
        return jsonify({"error": "No messages provided."}), 400

    try:
        response = client.chat.completions.create(
            model="gptpatient",  # Your deployment name
            messages=messages,
            temperature=0.9,
            max_tokens=400
        )

        reply = response.choices[0].message.content
        print(f"\nAzure replied:\n{reply}\n")

        # Clean hallucinations
        reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL)
        reply = re.sub(r"\[.*?thinking.*?\]", "", reply, flags=re.IGNORECASE).strip()

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"\n Azure API error:\n{str(e)}\n")
        return jsonify({"error": f"Azure OpenAI error: {str(e)}"}), 500


#Start server
if __name__ == "__main__":
    app.run(debug=True)
