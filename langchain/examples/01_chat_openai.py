"""
最小 LangChain ChatModel 调用示例（需要 OPENAI_API_KEY）。

运行：
  python langchain/examples/01_chat_openai.py
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


def main() -> None:
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "未检测到 OPENAI_API_KEY。请先设置环境变量或在 .env 中配置。"
        )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )

    messages = [
        SystemMessage(content="你是一个严谨的技术助手，回答尽量简洁。"),
        HumanMessage(content="用 3 句话解释什么是 LangChain。"),
    ]

    resp = llm.invoke(messages)
    print(resp.content)


if __name__ == "__main__":
    main()

