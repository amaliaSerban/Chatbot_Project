import openai
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import ast
import re
from dotenv import load_dotenv
from jinja2 import Template

print("Flask app is starting...")
load_dotenv()  # Load variables from .env

app = Flask(__name__)
CORS(app)

# Azure OpenAI setup from .env file
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_API_BASE")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")


@app.route("/new-patient", methods=["GET"])
def get_new_patient():
    try:
        df = pd.read_csv('new_processed_data.csv')
        patient = df.sample(1).iloc[0].to_dict()

        with open("Level1Prompt.txt", "r", encoding="utf-8") as f:
            template = Template(f.read())
            prompt = template.render(**patient)

        return jsonify({
            "prompt": prompt,
            "patient": patient
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500




@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])

    print("\n Received messages:")
    for msg in messages:
        print(msg)
        if 'role' in msg and 'content' in msg:
            print(f"{msg['role']}: {msg['content']}")
        else:
            print(" Skipping malformed message:", msg)

    try:
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=messages,
            temperature=0.9,
            max_tokens=400
        )
        reply = response.choices[0].message.content
        print(f"\n Azure replied:\n{reply}\n")

        reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL)
        reply = re.sub(r"\[.*?thinking.*?\]", "", reply, flags=re.IGNORECASE).strip()
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"\n Azure API error:\n{e}\n")
        return jsonify({"error": f"Azure OpenAI error: {str(e)}"}), 500


@app.route("/feedback", methods=["POST"])
def get_feedback():
    try:
        data = request.json
        messages = data.get("messages", [])

        # Convert messages to a clean text transcript
        full_chat = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])

        # Load feedback prompt template from file
        with open("Feedback_short.txt", "r", encoding="utf-8") as file:
            rubric = file.read()

        # Combine conversation and rubric into the final prompt
        feedback_prompt = f"""
You are an expert evaluator assessing a simulated patient conversation between a nurse (student) and a patient.

--- Conversation Transcript ---
{full_chat}
------------------------------

--- Evaluation Rubric ---
{rubric}
------------------------------

Please:
1. Score each main category based on the rubric (e.g., 12/20, 7/10, etc.)
2. Write a short paragraph of **positive feedback**
3. Write a short paragraph with **constructive improvement tips**
4. End with an **overall score out of 100**
"""

        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[
                {"role": "system", "content": "You are a strict but fair communication coach evaluating a student nurse."},
                {"role": "user", "content": feedback_prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )

        return jsonify({"feedback": response.choices[0].message.content})

    except Exception as e:
        print(f"\n Feedback error:\n{e}\n")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)