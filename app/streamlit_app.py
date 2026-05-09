import os
import sys

import streamlit as st
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

load_dotenv(os.path.join(ROOT, ".env"))

from agent.agent import bedrock, run_agent

BEDROCK_MODEL = (os.getenv("BEDROCK_MODEL_ID") or "us.anthropic.claude-sonnet-4-20250514-v1:0").strip()

st.set_page_config(page_title="Rental Truth-Teller", page_icon="🏠", layout="centered")
st.title("🏠 Bengaluru Rental Truth-Teller")
st.caption("The second opinion your broker doesn't want you to have.")

with st.sidebar:
    st.header("Try these queries")
    examples = [
        "Is ₹35,000 fair for a 2BHK in Koramangala?",
        "Broker wants 8 months deposit for a 1BHK in HSR at ₹22,000",
        "Should I rent in Whitefield or Sarjapur for ₹25,000?",
        "What can I get in BTM Layout for under ₹20,000?",
        "Is the deposit norm really 10 months in Indiranagar?",
    ]
    for ex in examples:
        if st.button(ex, key=ex, use_container_width=True):
            st.session_state["prefill"] = ex

    st.divider()
    st.markdown("**Data source:** Kaggle Bengaluru rental listings")
    st.markdown("**Powered by:** Elasticsearch + AWS Bedrock (Claude)")
    st.markdown("---")
    st.caption("⚠️ Data is from public datasets. Not financial or legal advice.")


def bedrock_verdict(agent_response: str, user_query: str) -> str | None:
    """Post-processing: call Bedrock for a renter's verdict summary."""
    try:
        prompt = f"""Based on this rental market analysis, give a 2-sentence
"Renter's Verdict" — a clear, actionable takeaway for the renter.

User's question: {user_query}
Agent's analysis: {agent_response}

Respond with ONLY the verdict, starting with "🏷️ Renter's Verdict:"."""

        response = bedrock.converse(
            modelId=BEDROCK_MODEL,
            system=[{"text": "You are a concise rental market advisor."}],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
        )
        return response["output"]["message"]["content"][0]["text"]
    except Exception:
        return None


if "messages" not in st.session_state:
    st.session_state.messages = []

if "prefill" in st.session_state:
    prefill = st.session_state.pop("prefill")
    st.session_state.messages.append({"role": "user", "content": prefill})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about Bengaluru rentals..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_msg = st.session_state.messages[-1]["content"]

    if len(st.session_state.messages) < 2 or st.session_state.messages[-2]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Searching rental data..."):
                try:
                    answer = run_agent(user_msg)

                    st.markdown(answer)

                    verdict = bedrock_verdict(answer, user_msg)
                    if verdict:
                        st.info(verdict)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer + (f"\n\n{verdict}" if verdict else ""),
                        }
                    )

                except Exception as e:
                    error_msg = f"⚠️ Something went wrong. Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
