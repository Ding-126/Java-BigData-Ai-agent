"""
LCEL 示例：Prompt + ChatModel + 输出解析器（需要 OPENAI_API_KEY）。

运行：
  python langchain/examples/02_lcel_chain.py
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def main() -> None:
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "未检测到 OPENAI_API_KEY。请先设置环境变量或在 .env 中配置。"
        )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是资深后端工程师，回答要点化、可执行。"),
            ("human", "给我一份 {topic} 的快速上手清单（不超过 {n} 条）。"),
        ]
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    parser = StrOutputParser()

    chain = prompt | llm | parser

    out = chain.invoke({"topic": "LangChain", "n": 8})
    print(out)


if __name__ == "__main__":
    main()

