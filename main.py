import os
import json

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "x-ai/grok-4.1-fast"


def call_openrouter(messages):
	if not OPENROUTER_API_KEY:
		raise RuntimeError("OPENROUTER_API_KEY is not set. Add it to your .env file.")

	payload = {
		"model": MODEL_NAME,
		"messages": messages,
		"max_tokens": 10000,
		"temperature": 0.3,
		"top_p": 0.9,
		"frequency_penalty": 0,
		"presence_penalty": 0,
	}

	headers = {
		"Authorization": f"Bearer {OPENROUTER_API_KEY}",
		"Content-Type": "application/json",
	}

	response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload), timeout=60)
	response.raise_for_status()
	data = response.json()
	return data["choices"][0]["message"]["content"]


st.set_page_config(page_title="Wellbee", page_icon="🐝")
st.title("Wellbee")
st.caption("Supportive, practical guidance for workplace wellbeing.")

with st.sidebar:
	st.header("Assistant Settings")
	st.write(f"Model: {MODEL_NAME}")
	st.markdown("""
Use this assistant for:
- Stress management tips
- Burnout prevention strategies
- Communication and boundary setting
- Work-life balance ideas
	""")

if "messages" not in st.session_state:
	st.session_state.messages = [
		{
			"role": "system",
			"content": (
				"You are Wellbee, a Workforce Wellbeing Assistant. Provide supportive, actionable, and "
				"evidence-based guidance for workplace wellbeing, stress management, communication, "
				"and work-life balance. Be empathetic, concise, and practical."
				"Talk less, dont make long lists talk like a human."
				"PLEASE TALK NORMALLY, DONT MAKE LONG LISTS, DONT TALK LIKE A ROBOT, TALK LIKE A HUMAN."
				"RESPOND IN MAX 2-3 LINES."
			),
		}
	]

for msg in st.session_state.messages:
	if msg["role"] == "system":
		continue
	with st.chat_message(msg["role"]):
		st.markdown(msg["content"])

user_prompt = st.chat_input("Ask about workplace wellbeing...")
print(user_prompt)
if user_prompt:
	st.session_state.messages.append({"role": "user", "content": user_prompt})
	with st.chat_message("user"):
		st.markdown(user_prompt)

	with st.chat_message("assistant"):
		with st.spinner("Thinking..."):
			try:
				reply = call_openrouter(st.session_state.messages)
				st.markdown(reply)
				st.session_state.messages.append({"role": "assistant", "content": reply})
			except Exception as exc:
				st.error(f"Request failed: {exc}")
