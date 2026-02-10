"""
离线可运行示例：用 Fake LLM 演示“可测试的链”（不需要任何 API Key）。

这个示例的目标是展示：
  - PromptTemplate/ChatPromptTemplate
  - LCEL 管道：prompt | llm | parser
  - 如何用 Fake LLM 做单元测试/离线验证

运行：
  python langchain/examples/03_offline_fake_chain.py
"""

from __future__ import annotations

from langchain_core.language_models.fake import FakeListLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def main() -> None:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一个遵循格式的助手。"),
            (
                "human",
                "请把下面的需求改写成验收标准（Gherkin 风格），最多 3 条：\n{req}",
            ),
        ]
    )

    # FakeListLLM 会按顺序吐出 responses，用于离线测试链路是否通畅
    llm = FakeListLLM(
        responses=[
            "\n".join(
                [
                    "Scenario: 需求验收",
                    "  Given 用户已登录",
                    "  When 用户提交需求",
                    "  Then 系统生成不超过 3 条的验收标准",
                ]
            )
        ]
    )

    chain = prompt | llm | StrOutputParser()

    out = chain.invoke({"req": "在项目下新增 langchain 目录，并提供使用文档与示例代码"})
    print(out)


if __name__ == "__main__":
    main()

