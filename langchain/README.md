# LangChain 使用整理

面向“把大模型能力接入到业务代码里”的工程化框架。本文档以 **LangChain Python** 为主，覆盖常用能力：模型调用、Prompt、LCEL（链式表达式）、结构化输出、工具调用，以及如何写可测试的示例代码。

## 目录

- [1. 安装与环境变量](#1-安装与环境变量)
- [2. LangChain 现在的推荐用法（LCEL）](#2-langchain-现在的推荐用法lcel)
- [3. 核心概念速览](#3-核心概念速览)
- [4. 示例代码](#4-示例代码)
- [5. 常见坑与最佳实践](#5-常见坑与最佳实践)
- [6. 参考链接](#6-参考链接)
- [附：更多用法与模式](#附更多用法与模式)

---

## 1. 安装与环境变量

### 1.1 Python 版本

建议 Python 3.10+。

### 1.2 安装依赖

下面是最小可用组合（按需安装即可）：

```bash
pip install -U langchain-core langchain-openai langchain-community python-dotenv
```

或使用本目录提供的 `requirements.txt`：

```bash
pip install -r langchain/requirements.txt
```

- **langchain-core**：核心抽象（Runnable、Message、Prompt、Parser 等）
- **langchain-openai**：OpenAI / 兼容 OpenAI API 的模型适配
- **langchain-community**：社区集成（部分 loader、vectorstore、工具等）
- **python-dotenv**：本地 `.env` 读取（可选但强烈建议）

### 1.3 环境变量（以 OpenAI 为例）

把密钥放在环境变量里，**不要写进代码、不要提交到 git**：

```bash
export OPENAI_API_KEY="xxx"
```

或在项目根目录（或 `langchain/` 目录）放一个 `.env`（自行确保不提交）：

```env
OPENAI_API_KEY=xxx
```

---

## 2. LangChain 现在的推荐用法（LCEL）

LangChain 近年的主流用法是 **LCEL（LangChain Expression Language）**：用“管道”方式组合 Prompt、模型、解析器、工具等。

典型形态：

```text
prompt | llm | output_parser
```

优点：

- **组合清晰**：像搭积木一样拼 pipeline
- **可测试**：可替换成 Fake LLM / Fake Embeddings
- **可观测**：更容易接入 tracing / callbacks（如 LangSmith）

---

## 3. 核心概念速览

### 3.1 Model / LLM / ChatModel

- **ChatModel**：面向“消息（system/user/assistant）”的对话模型，工程里最常用
- 在 LangChain 中通常通过 provider 包提供实现，例如 `langchain_openai.ChatOpenAI`

### 3.2 PromptTemplate / ChatPromptTemplate

- 把“输入变量 + 模板”变成可复用组件
- Chat 场景通常用 `ChatPromptTemplate` 来同时构造 system + user prompt

### 3.3 Runnable（可运行组件）

LCEL 中的所有组件都倾向于实现 Runnable 接口，从而支持：

- `.invoke()`：单次调用
- `.batch()`：批量调用
- `.stream()`：流式输出（取决于模型/组件支持）

### 3.4 OutputParser（输出解析）

把模型输出从“字符串/消息”变成结构化对象：

- **最常见**：`StrOutputParser()`（取文本）
- 结构化输出建议优先使用“模型的结构化/JSON 输出能力 + 校验”，并配合解析器/校验器

### 3.5 Tools（工具）

把“可执行函数”包装成工具，支持模型产生 tool call，再由程序执行工具并把结果喂回模型形成闭环（agent/工具链）。

---

## 4. 示例代码

示例代码都在 `langchain/examples/`，建议从最小例子开始。

### 4.1 运行方式

```bash
python langchain/examples/01_chat_openai.py
python langchain/examples/02_lcel_chain.py
python langchain/examples/03_offline_fake_chain.py
```

### 4.2 示例说明

- **01_chat_openai.py**：最小的 ChatModel 调用（需要 `OPENAI_API_KEY`）
- **02_lcel_chain.py**：Prompt + 模型 + 输出解析（LCEL 推荐写法，需要 `OPENAI_API_KEY`）
- **03_offline_fake_chain.py**：离线可跑：用 Fake LLM 做“可测试的链”示例（不需要任何 API Key）

---

## 5. 常见坑与最佳实践

### 5.1 把“业务逻辑”和“提示词/链”解耦

- Prompt/链负责：组织输入、约束输出、调用模型/工具
- 业务代码负责：参数校验、权限、数据获取、结果落库/展示

### 5.2 先做可测试的最小闭环

- 优先让链在本地用 Fake LLM 跑通（示例 03）
- 再替换成真实模型（示例 01/02）

### 5.3 关注输入输出的稳定性

- 用 Prompt 明确输出格式
- 用解析器/校验逻辑兜底，避免“模型输出一变就崩”

### 5.4 安全与合规

- 密钥只放环境变量/密钥管理系统
- 处理敏感数据前确认脱敏策略与日志策略（不要把敏感信息写入 tracing/log）

---

## 6. 参考链接

- [LangChain 官方文档](https://python.langchain.com/)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)
- [LangSmith（Tracing/Observability）](https://docs.smith.langchain.com/)

---

## 附：更多用法与模式

进阶但仍然常用的实践（结构化输出、可测试链路等）见：

- `langchain/01-常用用法与模式.md`

