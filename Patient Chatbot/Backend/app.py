import openai
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import ast
import re
from dotenv import load_dotenv  # Load environment variables

print("Flask app is starting...")
load_dotenv()  #Load variables from .env

app = Flask(__name__)
CORS(app)

#Azure OpenAI setup from .env file
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_API_BASE")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

@app.route("/new-patient", methods=["GET"])
def get_new_patient():
    try:
        df = pd.read_csv('reduced_data.csv')
        patient = df.sample(1).iloc[0]
        procedures = ast.literal_eval(patient['Procedure'])

        prompt = f"""You are a {patient['Age']} years old {patient['Gender']} patient currently at the hospital undergoing {procedures[0]} for your condition, {patient['Condition']}.
The nurse (the student) is here to take care of you, follow protocol, and reassure you.

... [truncated for brevity]
"""
        return jsonify({
            "prompt": prompt,
            "patient": patient.to_dict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages")

    print("\n📥 Received messages:")
    for msg in messages:
        print(f"{msg['role']}: {msg['content']}")

    try:
        response = openai.ChatCompletion.create(
            engine=deployment_name,  # ✅ Uses .env variable
            messages=messages,
            temperature=0.9,
            max_tokens=400
        )
        reply = response.choices[0].message.content
        print(f"\n🧠 Azure replied:\n{reply}\n")

        reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL)
        reply = re.sub(r"\[.*?thinking.*?\]", "", reply, flags=re.IGNORECASE).strip()
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"\n❌ Azure API error:\n{e}\n")
        return jsonify({"error": f"Azure OpenAI error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
