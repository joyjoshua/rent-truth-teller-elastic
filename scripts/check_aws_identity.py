"""Verify AWS / Bedrock auth configured in ROOT/.env.

- IAM credentials → STS GetCallerIdentity
- Bedrock API key (AWS_BEARER_TOKEN_BEDROCK) → minimal Bedrock Converse ping

Run from repo root:
  python scripts/check_aws_identity.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import boto3
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT))
from agent.aws_bedrock_env import apply_bedrock_client_env, bedrock_bearer_token


def main() -> int:
    load_dotenv(ROOT / ".env")

    region = (os.getenv("AWS_REGION") or "us-east-1").strip()
    model_id = (
        os.getenv("BEDROCK_MODEL_ID") or "us.anthropic.claude-sonnet-4-20250514-v1:0"
    ).strip()

    bearer = bedrock_bearer_token()
    if bearer:
        apply_bedrock_client_env(bearer)
        client = boto3.Session().client("bedrock-runtime", region_name=region)
        try:
            response = client.converse(
                modelId=model_id,
                messages=[
                    {"role": "user", "content": [{"text": "Reply with exactly: ok"}]}
                ],
                inferenceConfig={"maxTokens": 16},
            )
        except Exception as e:
            print("Bedrock Converse failed:", e, file=sys.stderr)
            print(
                "\nHints:\n"
                "  - Confirm AWS_REGION matches where the API key / model is valid.\n"
                "  - Upgrade boto3/botocore: pip install -U boto3 botocore\n"
                "  - Rotate AWS_BEARER_TOKEN_BEDROCK if expired.\n",
                file=sys.stderr,
            )
            return 1
        parts = response.get("output", {}).get("message", {}).get("content") or []
        text = ""
        for p in parts:
            if isinstance(p, dict) and "text" in p:
                text += p["text"]
        print("[OK] Bedrock API key works (minimal Converse):")
        print(f"  ModelId: {model_id}")
        print(f"  Snippet: {text.strip()[:80]!r}")
        return 0

    key_id = (os.getenv("AWS_ACCESS_KEY_ID") or "").strip()
    secret = (os.getenv("AWS_SECRET_ACCESS_KEY") or "").strip()
    token = (os.getenv("AWS_SESSION_TOKEN") or "").strip()

    session_kw: dict = {}
    if key_id and secret:
        session_kw["aws_access_key_id"] = key_id
        session_kw["aws_secret_access_key"] = secret
        if token:
            session_kw["aws_session_token"] = token

    session = boto3.Session(**session_kw)

    try:
        ident = session.client("sts", region_name=region).get_caller_identity()
    except Exception as e:
        print("STS failed:", e, file=sys.stderr)
        print(
            "\nHints:\n"
            "  - For Bedrock console API keys, set AWS_BEARER_TOKEN_BEDROCK=ABSK... "
            "(not IAM access keys).\n"
            "  - For IAM, use AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY (+ SESSION_TOKEN).\n",
            file=sys.stderr,
        )
        return 1

    print("[OK] IAM credentials resolve for STS:")
    print(f"  Arn: {ident.get('Arn')}")
    print(f"  Account: {ident.get('Account')}")
    print(f"  UserId: {ident.get('UserId')}")
    print(f"  Region used: {region}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
