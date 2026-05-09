"""Bedrock tool-use agent loop for the Rental Truth-Teller."""

import json
import os
import sys
from pathlib import Path

import boto3
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agent.aws_bedrock_env import apply_bedrock_client_env, bedrock_bearer_token
from agent.tool_definitions import TOOLS
from agent.tools import TOOL_DISPATCH

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

SYSTEM_PROMPT = (ROOT / "agent" / "system_prompt.md").read_text(encoding="utf-8")
AWS_REGION = (os.getenv("AWS_REGION") or "us-east-1").strip()
MODEL_ID = (os.getenv("BEDROCK_MODEL_ID") or "us.anthropic.claude-sonnet-4-20250514-v1:0").strip()


def _trim_env(name: str) -> str:
    v = os.getenv(name)
    return v.strip() if v else ""


def _bedrock_client():
    """
    1) Bedrock API key: AWS_BEARER_TOKEN_BEDROCK (or pasted into SECRET by mistake).
    2) IAM: AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY (+ optional SESSION_TOKEN).
    3) Else boto3 default chain (~/.aws/credentials, SSO/AWS_PROFILE).
    """
    bearer = bedrock_bearer_token()
    if bearer:
        apply_bedrock_client_env(bearer)
        return boto3.Session().client("bedrock-runtime", region_name=AWS_REGION)

    key_id = _trim_env("AWS_ACCESS_KEY_ID")
    secret = _trim_env("AWS_SECRET_ACCESS_KEY")
    token = _trim_env("AWS_SESSION_TOKEN")

    session_kw = {}
    if key_id and secret:
        session_kw["aws_access_key_id"] = key_id
        session_kw["aws_secret_access_key"] = secret
        if token:
            session_kw["aws_session_token"] = token

    return boto3.Session(**session_kw).client("bedrock-runtime", region_name=AWS_REGION)


bedrock = _bedrock_client()

_MAX_AGENT_LOOPS = 24


def run_agent(user_message: str, conversation_history: list | None = None) -> str:
    """
    Run the full agent loop:
    1. Send user message + tool definitions to Bedrock
    2. If Bedrock returns tool_use, execute the tool and send results back
    3. Repeat until Bedrock returns a final text response
    """
    messages = conversation_history.copy() if conversation_history else []
    messages.append({"role": "user", "content": [{"text": user_message}]})

    for _ in range(_MAX_AGENT_LOOPS):
        response = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=messages,
            toolConfig={"tools": TOOLS},
        )

        output = response["output"]["message"]
        messages.append(output)

        stop_reason = response["stopReason"]

        if stop_reason == "tool_use":
            tool_results = []
            for block in output["content"]:
                if "toolUse" in block:
                    tool_name = block["toolUse"]["name"]
                    tool_input = block["toolUse"]["input"]
                    tool_id = block["toolUse"]["toolUseId"]

                    print(f"  Calling tool: {tool_name}({json.dumps(tool_input)})")

                    try:
                        result = TOOL_DISPATCH[tool_name](tool_input)
                        tool_results.append(
                            {
                                "toolResult": {
                                    "toolUseId": tool_id,
                                    "content": [{"json": result}],
                                }
                            }
                        )
                    except Exception as e:
                        tool_results.append(
                            {
                                "toolResult": {
                                    "toolUseId": tool_id,
                                    "content": [{"text": f"Error: {str(e)}"}],
                                    "status": "error",
                                }
                            }
                        )

            messages.append({"role": "user", "content": tool_results})

        elif stop_reason == "end_turn":
            for block in output["content"]:
                if "text" in block:
                    return block["text"]
            return "I couldn't generate a response. Please try rephrasing."

        else:
            return "Unexpected response from the model. Please try again."

    return "Stopped after too many tool rounds — please narrow your question or try again."
