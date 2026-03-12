"""
调用鲸云 API。baseUrl: https://lab.iwhalecloud.com/gpt-proxy/anthropic
x-api-key 认证，模型 claude-4.5-haiku。
API Key 从环境变量 WHALELLM_API_KEY 或 auth-profiles 的 whalellm:default 读取。
调用前临时移除代理环境变量，避免 socks:// 报错。
"""
import json
import os
from pathlib import Path
from typing import Any

BASE_URL = "https://lab.iwhalecloud.com/gpt-proxy/anthropic"
MODEL = "claude-4.5-sonnet"
PROXY_VARS = [
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
    "http_proxy", "https_proxy", "all_proxy",
]


def _get_api_key() -> str:
    """从 WHALELLM_API_KEY 或 auth-profiles 的 whalellm:default 读取。"""
    key = os.environ.get("WHALELLM_API_KEY")
    if key:
        return key.strip()
    for candidate in [
        Path.home() / ".openclaw" / "agents" / "main" / "agent" / "auth-profiles.json",
        Path.home() / ".openclaw" / "agents" / "java-dev" / "agent" / "auth-profiles.json",
    ]:
        if candidate.exists():
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    data = json.load(f)
                profiles = data.get("profiles", {}) if isinstance(data, dict) else {}
                profile = profiles.get("whalellm:default", {})
                if profile.get("key"):
                    return profile["key"].strip()
            except (json.JSONDecodeError, OSError):
                continue
    raise ValueError("未找到 WHALELLM_API_KEY 或 whalellm:default 的 API Key")


def run_completion(
    model: str | None = None,
    messages: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> str:
    """
    调用鲸云 API，临时移除代理环境变量。
    返回 assistant 的 content 文本。
    """
    model = model or MODEL
    messages = messages or []
    saved = {k: os.environ.pop(k, None) for k in PROXY_VARS}
    try:
        import litellm
        api_key = _get_api_key()
        model_id = model.replace("anthropic/", "").strip()
        response = litellm.completion(
            model="anthropic/" + model_id,
            messages=messages,
            api_base=BASE_URL,
            api_key=api_key,
            extra_headers={"x-api-key": api_key},
            **kwargs,
        )
        return (response.choices[0].message.content or "").strip()
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
