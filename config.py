# config.py
import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> None:
    """加载配置，检查必要项是否存在。"""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / ".env"

    load_dotenv(dotenv_path=env_path)

    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError(
            "\n错误：缺少 OPENAI_API_KEY\n\n"
            "解决方法：\n"
            "  1. 复制 .env.example 为 .env\n"
            "  2. 填入你的 API Key\n"
            "  3. 重新运行\n"
        )


def get_model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def get_base_url() -> str | None:
    return os.environ.get("OPENAI_BASE_URL") or None