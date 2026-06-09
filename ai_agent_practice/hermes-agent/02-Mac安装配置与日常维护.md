# 02 · Mac 安装、配置与日常维护

面向 **Mac 初学者**：下面命令可直接复制到「终端」（Terminal）执行。若提示 `command not found: hermes`，请先完成安装并执行 `source ~/.zshrc`。

---

## 一、安装前准备

### 1. 确认已安装 Git

1. 打开 **终端**（应用程序 → 实用工具 → 终端，或 Spotlight 搜索 Terminal）。
2. 输入下面命令并回车：

```bash
git --version
```

3. 若显示类似 `git version 2.x`，说明已安装。
4. 若未安装，安装 Xcode 命令行工具（会附带 Git）：

```bash
xcode-select --install
```

弹出窗口后点「安装」，等待完成即可。

### 2. 确认网络与 Shell

- 需要能访问 GitHub 与 Nous 的安装脚本。
- macOS 默认 Shell 为 **zsh**，本指南按 zsh 编写（配置文件为 `~/.zshrc`）。

---

## 二、安装 Hermes Agent

### 方式 A：一行脚本安装（推荐）

在终端执行：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

脚本通常会：下载 CLI、写入 `~/.local/bin/hermes`，并提示你把该目录加入 PATH。

### 方式 B：桌面应用（可选）

1. 打开 GitHub Releases：  
   https://github.com/NousResearch/hermes-agent/releases  
2. 下载适用于 **macOS** 的安装包（`.dmg` 或说明中的 Desktop 版本）。
3. 打开 `.dmg`，将应用拖入「应用程序」文件夹。
4. 首次打开若被 Gatekeeper 拦截：系统设置 → 隐私与安全性 → 仍要打开。

桌面版与 CLI 可并存；日常维护命令仍以 CLI 为准。

### 3. 让终端识别 `hermes` 命令

安装完成后执行：

```bash
source ~/.zshrc
hermes --version
```

若仍找不到命令，手动把下面一行加入 `~/.zshrc`（可用 `nano ~/.zshrc` 编辑）：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

保存后再次：

```bash
source ~/.zshrc
hermes --version
```

---

## 三、安装后的目录结构（心里有数）

| 路径 | 含义 |
|------|------|
| `~/.hermes/` | 主配置、记忆、日志、Gateway 状态等 |
| `~/.local/bin/hermes` | CLI 可执行文件（常见位置） |
| `~/.hermes/logs/gateway.log` | Gateway 运行日志（排错常用） |

---

## 四、首次配置

按顺序执行（交互式向导会提问 API Key、模型等）：

### 1. 总向导

```bash
hermes setup
```

### 2. 模型与工具

```bash
hermes model
hermes tools
```

### 3. 修改单项配置

```bash
hermes config set <键> <值>
```

（具体键名以 `hermes config` 帮助或官方文档为准。）

### 4. 门户 / 浏览器登录类配置（若文档支持）

```bash
hermes setup --portal
```

---

## 五、Gateway（Telegram / Discord / Slack）

Gateway 让 Hermes 在 IM 里 24/7 响应（需本机或服务器常开，或使用 launchd 后台服务）。

### 1. 初始化与安装

```bash
hermes gateway setup
hermes gateway install
```

### 2. 启停与状态

```bash
hermes gateway start
hermes gateway status
hermes gateway stop
hermes gateway restart
```

### 3. macOS 开机自启（launchd）

`hermes gateway install` 通常会注册 **launchd** 用户服务。查看日志：

```bash
tail -f ~/.hermes/logs/gateway.log
```

按 `Ctrl + C` 退出日志跟踪（不会停止 Gateway）。

---

## 六、升级

```bash
hermes update --check
hermes update
```

升级后建议：

```bash
hermes doctor
hermes config check
```

若有配置迁移提示：

```bash
hermes config migrate
```

---

## 七、诊断命令速查

| 命令 | 用途 |
|------|------|
| `hermes doctor` | 环境与依赖健康检查 |
| `hermes config check` | 校验配置文件 |
| `hermes config migrate` | 升级后迁移旧配置 |
| `hermes gateway status` | Gateway 是否在跑 |
| `tail -f ~/.hermes/logs/gateway.log` | 实时看 Gateway 日志 |

---

## 八、常见问题（排错表）

| 现象 | 可能原因 | 处理建议 |
|------|----------|----------|
| `hermes: command not found` | PATH 未包含 `~/.local/bin` | `source ~/.zshrc` 或手动 export PATH |
| API / 模型报错 | Key 未配置或过期 | 重新 `hermes setup` 或 `hermes model` |
| Gateway 无响应 | 服务未启动或 Token 错误 | `hermes gateway status` → `restart`；查 `gateway.log` |
| IM 收不到消息 | 机器人未邀请进频道 / Webhook 错误 | 按 `hermes gateway setup` 文档核对平台侧配置 |
| 升级后配置异常 | 配置版本变更 | `hermes config migrate` + `hermes doctor` |
| 权限被拒绝 | macOS 安全限制 | 系统设置中允许终端/应用访问所需权限 |

---

## 九、卸载（大致步骤）

> 卸载前请自行备份 `~/.hermes/` 中需要保留的记忆或配置。

1. 停止并移除 Gateway 服务：

```bash
hermes gateway stop
hermes gateway uninstall
```

（若子命令名与本地版本不一致，以 `hermes gateway --help` 为准。）

2. 删除 CLI（若通过脚本安装）：

```bash
rm -f ~/.local/bin/hermes
```

3. 删除数据目录（**不可恢复**）：

```bash
rm -rf ~/.hermes
```

4. 从 `~/.zshrc` 中删除与 Hermes 相关的 `export PATH` 或 alias 行，然后：

```bash
source ~/.zshrc
```

5. 若安装了桌面应用：从「应用程序」中拖到废纸篓。

---

## 十、日常维护建议

- 每月执行一次：`hermes update --check` → `hermes update` → `hermes doctor`
- Gateway 长期运行时，偶尔查看 `gateway.log` 是否有重复报错
- 重要 API Key 不要提交到 Git；仅保存在本地配置中

更多细节请以官方文档为准：https://hermes-agent.nousresearch.com/docs
