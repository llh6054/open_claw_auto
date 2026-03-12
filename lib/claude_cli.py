"""
通过 Claude CLI (claude -p) 调用，用于代码生成。
支持两种认证方式：
1. WhaleCloud 第三方 key：设置 WHALELLM_API_KEY 或配置 auth-profiles 的 whalellm:default
2. Claude 官方：运行 claude /login 登录
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path

WHALECLOUD_BASE_URL = "https://lab.iwhalecloud.com/gpt-proxy/anthropic"
PROXY_VARS = [
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
    "http_proxy", "https_proxy", "all_proxy",
]


def _get_whalecloud_key() -> str | None:
    """从 WHALELLM_API_KEY 或 auth-profiles 读取鲸云 key，未找到返回 None。"""
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


def run_completion(prompt: str, timeout: int = 300) -> str:
    """
    使用 claude -p 执行补全，返回纯文本输出。
    若存在 WhaleCloud key，自动设置 ANTHROPIC_BASE_URL 和 ANTHROPIC_API_KEY。
    """
    env = os.environ.copy()
    whale_key = _get_whalecloud_key()
    if whale_key:
        env["ANTHROPIC_BASE_URL"] = WHALECLOUD_BASE_URL
        env["ANTHROPIC_API_KEY"] = whale_key
        for k in PROXY_VARS:
            env.pop(k, None)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(prompt)
        tmp_path = f.name
    try:
        with open(tmp_path, "r", encoding="utf-8") as f:
            result = subprocess.run(
                ["claude", "-p", "--tools", "", "--output-format", "text"],
                stdin=f,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
        if result.returncode != 0:
            raise RuntimeError(f"claude CLI failed: {result.stderr or result.stdout}")
        return (result.stdout or "").strip()
    finally:
        Path(tmp_path).unlink(missing_ok=True)
