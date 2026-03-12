"""
调用 Kimi：优先鲸云代理，无鲸云 key 时回退到 Moonshot 官方 API。
- 鲸云：WHALELLM_API_KEY + lab.iwhalecloud.com/gpt-proxy/moonshot
- 官方：MOONSHOT_API_KEY + api.moonshot.cn
"""
import json
import os
from pathlib import Path
from typing import Any

# 鲸云 Kimi 与 Claude 共用同一代理（openclaw 配置：whalellm baseUrl = gpt-proxy/anthropic）
WHALECLOUD_BASE = "https://lab.iwhalecloud.com/gpt-proxy/anthropic"
MOONSHOT_BASE = "https://api.moonshot.cn/v1"
MODEL = "moonshot/kimi-k2.5"
PROXY_VARS = [
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
    "http_proxy", "https_proxy", "all_proxy",
]


def _get_whalecloud_key() -> str | None:
    """从 WHALELLM_API_KEY 或 auth-profiles 的 whalellm:default 读取，未找到返回 None。"""
    key = os.environ.get("WHALELLM_API_KEY")
    if key and key.strip():
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
    return None


def _get_moonshot_key() -> str | None:
    """从 MOONSHOT_API_KEY 或 auth-profiles 的 moonshot:default 读取，未找到返回 None。"""
    key = os.environ.get("MOONSHOT_API_KEY")
    if key and key.strip():
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
                profile = profiles.get("moonshot:default", {})
                if profile.get("key"):
                    return profile["key"].strip()
            except (json.JSONDecodeError, OSError):
                continue
    return None


def run_completion(
    model: str | None = None,
    messages: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> str:
    """
    调用 Kimi：优先鲸云，无鲸云 key 时用 Moonshot 官方。
    返回 assistant 的 content 文本。
    """
    model = model or MODEL
    messages = messages or []
    saved = {k: os.environ.pop(k, None) for k in PROXY_VARS}
    try:
        import litellm
        model_id = model.replace("moonshot/", "").strip()
        whale_key = _get_whalecloud_key()
        whale_base = os.environ.get("WHALEKIMI_BASE_URL", WHALECLOUD_BASE)
        if whale_key:
            try:
                # 鲸云 anthropic 代理同时支持 Claude 和 Kimi，使用 anthropic-messages 格式
                response = litellm.completion(
                    model="anthropic/" + model_id,
                    messages=messages,
                    api_base=whale_base,
                    api_key=whale_key,
                    extra_headers={"x-api-key": whale_key},
                    **kwargs,
                )
            except Exception as e:
                if "404" in str(e) or "NotFound" in str(e).lower():
                    moon_key = _get_moonshot_key()
                    if moon_key:
                        base = os.environ.get("MOONSHOT_API_BASE", MOONSHOT_BASE)
                        os.environ["MOONSHOT_API_KEY"] = moon_key
                        response = litellm.completion(
                            model="moonshot/" + model_id,
                            messages=messages,
                            api_base=base,
                            api_key=moon_key,
                            **kwargs,
                        )
                    else:
                        raise
                else:
                    raise
        else:
            moon_key = _get_moonshot_key()
            if not moon_key:
                raise ValueError("未找到 WHALELLM_API_KEY 或 MOONSHOT_API_KEY，请配置其一")
            base = os.environ.get("MOONSHOT_API_BASE", MOONSHOT_BASE)
            os.environ["MOONSHOT_API_KEY"] = moon_key
            response = litellm.completion(
                model="moonshot/" + model_id,
                messages=messages,
                api_base=base,
                api_key=moon_key,
                **kwargs,
            )
        return (response.choices[0].message.content or "").strip()
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
