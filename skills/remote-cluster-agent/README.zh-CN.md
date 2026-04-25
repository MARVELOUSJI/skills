# Remote Cluster Agent

![Version](https://img.shields.io/badge/version-0.5.0-blue)

[English](README.md) | 中文

> 让 Coding Agent 在无公网的 GPU 集群上自动迭代。本地读写，远程执行，~0.1s 延迟。本地用 Go daemon + `rca` CLI，集群端 Python agent.py。

## v0.5.0 新特性

**项目级 rule + 同步竞态修复**

- **新增：项目初始化流程** —— 当 agent 第一次在某个新项目里使用 skill 做开发时，会主动问 4 个值（节点、远程目录、conda 环境名、mutagen session 名），生成 `<project>/.claude/rules/remote-cluster-agent.md` 并在 `<project>/CLAUDE.md` 里 `@import` 引用。该项目此后所有会话自动加载这条 rule。
- **同步竞态文档化并修复** —— `MUTAGEN.md` 新增警告：mutagen 是*近实时*但*非同步*。增加 `mutagen sync flush <session>` 作为标准解法，避免本地编辑→远程执行 / 远程写→本地读两个方向的旧数据问题。项目 rule 文件强制每个会话遵守此规则。
- **每个项目记录 conda 环境** —— rule 文件固化项目所用 conda env，所有 `rca exec` 跑 Python / pytest 都会先 `conda activate`，避免回退到系统解释器找不到依赖。

无 breaking change，v0.4.x 项目继续可用；项目初始化流程仅在首次缺 rule 文件时触发。

## 安装

```bash
npx skills add jiahao-shao1/sjh-skills --skill remote-cluster-agent
```

然后编译并安装 `rca` CLI（需要 Go 1.21+）：

```bash
cd <skill_dir>
make install
```

重启 agent，说"连集群"开始使用。Agent 会在首次使用时引导你完成配置。

## v0.4.0 新特性

**架构重构：MCP server → Go daemon + `rca` CLI**

- **Breaking**: Python MCP server 被替换为本地 Go daemon + `rca` CLI。
  - 单一 `rca` 二进制：后台 daemon（首次调用自动启动）+ CLI 子命令（通过 Unix socket 无状态 HTTP 客户端）。
  - 迁移：`make install` 后 `rca config init` —— 自动检测 `~/.config/remote-cluster-agent/*.md` 旧配置并迁移到 `~/.config/rca/config.toml`。
  - 命令变更：`remote_bash(node, cmd)` → `rca exec -n <node> "<cmd>"`；`remote_bash_batch` → `rca batch`。

**新功能**

- `rca batch` —— 多节点并行执行命令。
- `rca cp` —— 通过 agent JSON-Lines 通道传文件（base64，单文件 50 MB 上限），不依赖 SCP，任何 SSH 隧道形态都能用。
- `rca nodes --check / --health` —— 深度延迟探测 + 历史延迟追踪（内置节点健康监控）。
- `rca agent check / deploy` —— 集群端 agent 生命周期管理。
- `rca daemon register` —— 可选 launchd 自动启动（macOS）。

**Agent 协议 v2.1**

- 按行流式输出。
- 请求取消。
- 单次往返批量执行。
- 文件读写通过 agent 通道（不再依赖 SCP）。

**修复**

- **Fixed**: 彻底消除 MCP stdio 断连 —— daemon 通过 CLI 调用和 AI agent 交互，MCP transport 上不再有 progress notification 竞态问题。
- **Fixed**: 多会话 SSH 连接爆炸 —— N 个 session × M 个节点 收敛到 1 个 daemon × M 个持久连接。

## 架构

```
本地机器                                  GPU 集群（不需要公网）
├── Claude Code / Codex (Read/Edit/Write)└── /path/to/project/
│   每次操作 ~0.5ms                          ├── 训练脚本
├── Mutagen 实时同步 ◄───SSH────────────► 代码 + 日志
├── rca CLI ──► rcad ◄──SSH────────────► bash 命令
│              (Unix socket,                └── agent.py（持久运行）
│               连接池)                         JSON-Lines v2.1
└── 本地读取结果（快 ~20x）
```

**核心特性**：

| 特性 | 值 |
|------|-----|
| 延迟 | ~0.1s/命令（持久 SSH + JSON-Lines） |
| 并发 | 单 daemon 服务所有 CC / Codex session |
| 安装 | `make install` → `~/go/bin/rca`（~8 MB，零运行时依赖） |

### 自动化循环

```
修改代码（本地） → Mutagen 同步（亚秒级） → mutagen sync flush → 跑实验（远程） → 日志同步回来 → flush → 读结果（本地） → 循环
```

- **代码编辑**：本地原生工具（~0.5ms）
- **代码同步**：[Mutagen](https://mutagen.io) 近实时 one-way-replica SSH 同步（见 [MUTAGEN.md](MUTAGEN.md)）
- **同步 flush**：`mutagen sync flush <session>` 在跨边界（远程执行 / 本地读）前关闭传播竞态（见 [MUTAGEN.md → Sync Timing](MUTAGEN.md#sync-timing--race-conditions)）
- **远程执行**：`rca exec` / `rca batch` —— 通过本地 daemon 路由
- **读取结果**：本地 `Read` 工具（比远程 exec 快 ~20x）

## 快速开始

### 1. 安装 skill

```bash
npx skills add jiahao-shao1/sjh-skills --skill remote-cluster-agent
```

### 2. 编译并安装 CLI

```bash
cd <skill_dir>
make install
```

`rca` 会安装到 `$(go env GOPATH)/bin`。确保该目录在 `PATH` 里。

### 3. 初始化配置

```bash
rca config init
```

- 全新安装 → 生成带注释的 `~/.config/rca/config.toml` 模板。
- 旧 markdown 配置（`~/.config/remote-cluster-agent/`）→ 自动迁移。

编辑配置，添加你的节点：

```toml
socket_path = "~/.config/rca/rca.sock"
default_dir = "/home/user/project"
agent_path  = "/shared/.agent/agent.py"

[nodes.train]
ssh = "ssh gpu-train"

[nodes.eval]
ssh = "ssh -p 2222 gpu-eval"
dir = "/home/user/eval-project"       # 可选，节点级覆盖
```

### 4. 启动 daemon

```bash
rca daemon start
rca daemon status
rca nodes
rca agent deploy           # 推送 agent.py 到各节点
```

可选：`rca daemon register` 注册 launchd 开机自启。

### 5. 配置 Mutagen 同步

```bash
bash <skill_dir>/mutagen-setup.sh gpu-train ~/repo/my_project /home/user/my_project
```

详见 [MUTAGEN.md](MUTAGEN.md)。完全走 SSH —— 集群不需要公网。

## 配置

单一配置文件：`~/.config/rca/config.toml`。

```toml
socket_path = "~/.config/rca/rca.sock"
default_dir = "/home/user/project"
agent_path  = "/shared/.agent/agent.py"

[monitor]
enabled           = true
interval          = "30s"
latency_threshold = "200ms"
latency_multiplier = 3.0
auto_reconnect    = false

[nodes.train]
ssh = "ssh gpu-train"

[nodes.eval]
ssh = "ssh -p 2222 gpu-eval"
```

用 `rca config edit` 编辑，`rca config show` 查看当前生效配置。

## 文件结构

```
remote-cluster-agent/
├── SKILL.md                          # Skill 指令
├── README.md                         # 英文说明
├── README.zh-CN.md                   # 本文件
├── MUTAGEN.md                        # Mutagen 同步指南
├── VERSION                           # 0.5.0
├── Makefile                          # 编译 / 安装 / 测试
├── go.mod / go.sum                   # Go 依赖
├── cmd/rca/                          # CLI 入口 + 子命令
├── internal/
│   ├── agent/                        # SSH agent 连接（JSON-Lines v2.1）
│   ├── client/                       # Unix socket HTTP 客户端
│   ├── config/                       # TOML 加载 + 旧配置迁移
│   ├── daemon/                       # HTTP server、连接池、监控
│   └── protocol/                     # 共享类型（daemon ↔ CLI）
├── launchd/
│   └── com.rca.daemon.plist          # launchd 自启模板
├── cluster-agent/
│   └── agent.py                      # 集群端 agent（零依赖，v2.1.0）
├── mutagen-setup.sh                  # Mutagen 同步配置
├── templates/
│   └── project-rule.md.tmpl          # 项目级 rule 模板（v0.5.0 新增）
├── reference/
│   ├── cluster-health.md             # 巡检流程
│   └── mutagen-troubleshooting.md    # Mutagen 排障手册
└── docs/
    ├── architecture.png              # 架构图
    └── architecture.html             # 交互版本
```

## 致谢

深受 [claude-code-local-for-vscode](https://github.com/justimyhxu/claude-code-local-for-vscode) 项目启发。

感谢 [@cherubicXN](https://github.com/cherubicXN) 实现的基于 Mutagen 的本地-集群实时同步方案。

## 许可证

MIT
