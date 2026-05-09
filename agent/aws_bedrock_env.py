"""Resolve Bedrock API-key bearer token from environment (vs IAM SigV4)."""

from __future__ import annotations

import os


def _trim(name: str) -> str:
    v = os.getenv(name)
    return v.strip() if v else ""


def bedrock_bearer_token() -> str:
    """
    Bedrock console API keys use AWS_BEARER_TOKEN_BEDROCK (see AWS docs).

    Also accepts the common mistake of pasting
    `set AWS_BEARER_TOKEN_BEDROCK=ABSK...` into AWS_SECRET_ACCESS_KEY.
    """
    direct = _trim("AWS_BEARER_TOKEN_BEDROCK")
    if direct:
        return direct

    secret = _trim("AWS_SECRET_ACCESS_KEY")
    if not secret:
        return ""

    lower = secret.lower()
    if lower.startswith("set "):
        secret = secret[4:].strip()

    marker = "AWS_BEARER_TOKEN_BEDROCK="
    idx = secret.find(marker)
    if idx != -1:
        secret = secret[idx + len(marker) :].strip()

    if secret.startswith("ABSK"):
        return secret.split()[0]

    return ""


def apply_bedrock_client_env(bearer: str) -> None:
    """Ensure boto3 uses bearer auth for Bedrock: drop stray IAM vars that break SigV4."""
    os.environ["AWS_BEARER_TOKEN_BEDROCK"] = bearer
    for var in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
        os.environ.pop(var, None)
