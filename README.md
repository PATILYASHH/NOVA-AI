<p align="center">
  <img src="https://img.shields.io/badge/NOVA-Autonomous%20AI%20Agent-blueviolet?style=for-the-badge&logo=robot&logoColor=white" alt="NOVA"/>
</p>

<h1 align="center">NOVA</h1>

<p align="center">
  <strong>An autonomous AI agent that lives on your PC.</strong>
</p>

<p align="center">
  <a href="#quick-start"><img src="https://img.shields.io/badge/Quick%20Start-blue?style=flat-square" alt="Quick Start"/></a>
  <a href="#features"><img src="https://img.shields.io/badge/Features-green?style=flat-square" alt="Features"/></a>
  <a href="#architecture"><img src="https://img.shields.io/badge/Architecture-orange?style=flat-square" alt="Architecture"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License"/></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Claude-Code%20CLI-6B4FBB?style=flat-square&logo=anthropic&logoColor=white"/>
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram&logoColor=white"/>
  <img src="https://img.shields.io/badge/ChromaDB-Vector%20Memory-FF6F61?style=flat-square"/>
  <img src="https://img.shields.io/badge/Skills-102+-brightgreen?style=flat-square"/>
</p>

---

<p align="center">
  <em>Controls your PC, builds full projects, fixes its own bugs, and evolves its personality — all through natural conversation via Telegram or Terminal.</em>
</p>

<p align="center">
  <em>No paid APIs. Runs locally using Claude Code CLI.</em>
</p>

> ⚠️ **Early Stage** — NOVA is under active development. Expect rough edges. Contributions welcome!

---

## What NOVA Does

Most AI assistants answer questions and forget you exist. NOVA is different — it's a persistent agent that **lives on your machine**, remembers your history, acts proactively, and improves itself over time.

- Controls your entire PC via natural language
- Builds full projects and pushes them to GitHub
- Fixes its own bugs daily with your approval
- Evolves its personality based on interactions
- Remembers past conversations semantically (ChromaDB)
- Sends you morning briefings and proactive alerts
- Reads PDFs, analyzes screenshots via OCR

---

## Demo

> 📹 *Demo GIF coming soon — star the repo to get notified!*

```
You: "build a todo app in flask and push to github"
NOVA: Creates project → writes all code → creates repo → pushes → sends link

You: "what's my cpu at?"
NOVA: "CPU at 23%, RAM at 67%. Everything's chill."

You: "this code is broken, help me fix it"
NOVA: Identifies bug → explains why → gives fix with code

You: (sends a PDF)
NOVA: Reads it, summarizes it, answers questions about it
```

---

## Features

<details>
<summary><strong>Natural Language Everything</strong> — Just talk, NOVA figures out the rest</summary>

No commands needed. NOVA classifies your message and decides what to do:
- **Chat** → Responds conversationally
- **PC Action** → Opens apps, screenshots, runs commands
- **Build Project** → Full project + GitHub repo
- **Code Task** → Claude Code implements features
</details>

<details>
<summary><strong>Self-Evolving Personality</strong> — Nothing is hardcoded</summary>

NOVA's personality, emotions, and knowledge are stored in editable files that evolve over time:

| File | What It Controls |
|---|---|
| `self/identity/personality.md` | How NOVA talks and behaves |
| `self/identity/emotions.json` | 11 emotions with triggers & expressions |
| `self/identity/traits.json` | Personality traits (0-1 scale) |
| `self/knowledge/learned.json` | Facts, opinions, lessons learned |

NOVA can update all of these based on interactions over time.

**Emotions modeled:** `happy` `proud` `frustrated` `angry` `worried` `sad` `excited` `annoyed` `caring` `playful` `curious`
</details>

<details>
<summary><strong>Self-Coding</strong> — NOVA proposes fixes for its own bugs</summary>

Every day at 6 PM:
1. Reviews all errors encountered during the day
2. Asks Claude to analyze root causes
3. Proposes specific code fixes
4. Sends proposals to you on Telegram
5. On your approval, **applies the fix into itself**

```
NOVA: "I encountered 3 errors today. Let me analyze..."

NOVA: "Self-Fix Proposal [High]
  Problem: Timeout in Claude CLI for long prompts
  File: core/personality.py
  Fix: Add retry with shorter prompt fallback
  Risk: Safe

  /fixapprove fix_20260411_180000 to approve"
```
</details>

<details>
<summary><strong>4-Layer Memory System</strong> — Remembers everything</summary>

| Layer | Type | Persistence | How It Works |
|:---|:---|:---|:---|
| **RM** (Register) | Current conversation | Session | Fast context for active chat |
| **RAM** | Daily session data | JSON files | Statistics, commands, files changed |
| **ROM** | Permanent knowledge | SQLite (9 tables) | Command history, projects, insights |
| **Vector** | Semantic search | ChromaDB | Finds past conversations by meaning |

**Example:**
```
You say: "flutter gradle error"
NOVA recalls: "Last week you had a Gradle build issue — we fixed it by updating the wrapper"
```
Even though the exact words differ, ChromaDB finds it by meaning.
</details>

<details>
<summary><strong>Proactive Intelligence</strong> — Acts without being asked</summary>

| Time | What NOVA Does |
|---|---|
| **9:00 AM** | Morning briefing: system health, disk warnings, greeting |
| **6:00 PM** | Evening summary + self-review + diary entry + fix proposals |
| **Anytime** | CPU/RAM/disk alerts when thresholds crossed |
| **Anytime** | Battery warnings when unplugged and low |

</details>

<details>
<summary><strong>Full PC Control</strong> — 110+ actions via natural language</summary>

| Category | Examples |
|---|---|
| **Apps** | Open/close any application |
| **System** | CPU, RAM, disk, battery, processes |
| **Files** | Read, write, find, delete files |
| **Code** | Run Python/JS/PowerShell, execute code |
| **Git** | Status, commit, push, pull, branch |
| **GitHub** | Create repos, push code, list repos |
| **Browser** | Open URLs, Google search |
| **Screenshots** | Capture and analyze screen |
| **Clipboard** | Read/write clipboard |
| **Network** | WiFi info, connectivity |
| **Power** | Shutdown, restart, sleep, lock |
| **Automation** | Macros, scheduled tasks, chains |

</details>

---

## Quick Start

### Prerequisites

| Tool | Required | Purpose |
|---|---|---|
| Python 3.10+ | Yes | Runtime |
| [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) | Yes | AI brain |
| [GitHub CLI](https://cli.github.com/) | Optional | Repo management |
| Telegram | Optional | Remote access from phone |

### Installation

```bash
# Clone the repo
git clone https://github.com/PATILYASHH/NOVA-AI.git
cd NOVA-AI

# Run the setup wizard (handles everything)
python nova_cli.py --setup
```

The wizard will:
1. Install all dependencies
2. Ask for your Telegram bot token & chat ID
3. Create your personality files
4. Set up all required directories

### Running NOVA

```bash
python nova_cli.py            # Interactive menu (recommended)
python nova_cli.py --chat     # Direct terminal chat
python nova_cli.py --bot      # Start Telegram bot
python main.py                # Telegram bot (direct)
```

### Terminal UI

```
╔══════════════════════════════════════════╗
║     ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ ║
║     ████╗  ██║██╔═══██╗██║   ██║██╔══██╗║
║     ██╔██╗ ██║██║   ██║██║   ██║███████║║
║     ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║║
║     ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║║
║     ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝║
║     Self-Evolving AI Agent               ║
╚══════════════════════════════════════════╝

  [1] Chat with NOVA (Terminal)
  [2] Start Telegram Bot
  [3] Setup / Reconfigure
  [4] System Status
  [5] Exit
```

### Telegram Setup

<details>
<summary>How to get Bot Token & Chat ID</summary>

**Bot Token:**
1. Open Telegram, search for `@BotFather`
2. Send `/newbot`, follow prompts
3. Copy the token

**Chat ID:**
1. Search for `@userinfobot` on Telegram
2. Send `/start`
3. Copy your chat ID

Enter both when the setup wizard asks.
</details>

---

## Architecture

```
NOVA/
├── nova_cli.py                 # Terminal UI & setup wizard
├── main.py                     # Telegram bot entry point
├── config.py                   # Configuration
│
├── core/                       # Brain
│   ├── personality.py          # Claude-powered dynamic chat
│   ├── dynamic_identity.py     # Loads personality from files
│   ├── vector_memory.py        # ChromaDB semantic memory
│   ├── agent_executor.py       # Autonomous multi-step tasks
│   ├── self_coder.py           # Self-coding (fixes own bugs)
│   ├── emotion_engine.py       # 11 emotions + mood tracking
│   ├── memory_system.py        # 3-tier memory (RM/RAM/ROM)
│   ├── nova_brain.py           # Intelligence orchestrator
│   ├── nlp_engine.py           # Natural language understanding
│   ├── reasoning_engine.py     # Logic & decision making
│   ├── context_engine.py       # Context awareness
│   ├── learning_loop.py        # Behavioral learning
│   ├── self_reflection.py      # Self-evaluation + diary
│   └── self_improve.py         # Self-improvement engine
│
├── actions/                    # System actions
│   ├── code_handler.py         # Code, Git, GitHub CLI, Graphify
│   ├── system_control.py       # Apps, commands, processes
│   ├── file_ops.py             # File operations
│   ├── utilities.py            # Screenshot, clipboard, browser
│   └── advanced_control.py     # Network, volume, battery
│
├── intelligence/               # Smart features
│   ├── powers.py               # OCR, web search, images, PDFs
│   ├── proactive_monitor.py    # Morning briefing, alerts
│   ├── smart_automation.py     # Macros, command chains
│   ├── habit_tracker.py        # Usage pattern learning
│   ├── scheduler.py            # Task scheduling
│   ├── work_setup.py           # Workspace auto-setup
│   └── style_learner.py        # Coding style learning
│
├── self/                       # NOVA's identity (evolves)
│   ├── identity/               # Personality, emotions, traits
│   ├── knowledge/              # Learned facts & opinions
│   └── diary/                  # Private diary entries
│
└── memory/                     # Persistent storage
    ├── RM/                     # Register (current session)
    ├── RAM/                    # Session (daily JSON)
    ├── ROM/                    # Permanent (SQLite)
    └── vector_db/              # Semantic (ChromaDB)
```

---

## Telegram Commands

> NOVA understands natural language, but these shortcuts also work:

<details>
<summary>View all commands</summary>

| Command | Description |
|:---|:---|
| `/build <desc>` | Build a full project from description |
| `/task <desc>` | Execute any task with Claude Code |
| `/autopush [path]` | Commit and push to GitHub |
| `/newrepo <name>` | Create GitHub repository |
| `/repos` | List your GitHub repos |
| `/graphify <path>` | Build knowledge graph |
| `/status` | System status (CPU, RAM, Disk) |
| `/screenshot` | Capture screen |
| `/cmd <command>` | Run shell command |
| `/open <app>` | Open application |
| `/close <app>` | Close application |
| `/git <path> <op>` | Git operations |
| `/run <lang>` | Execute code |
| `/fixes` | Today's errors + fix proposals |
| `/selfcode` | Trigger self-review now |
| `/fixapprove <id>` | Approve a self-fix |
| `/help` | Show all commands |

</details>

---

## Safety

| Action | NOVA's self dir | NOVA's code | Outside NOVA |
|:---|:---:|:---:|:---:|
| **Read** | Free | Free | Free |
| **Edit** | Free | Needs approval | Blocked |
| **Delete** | Needs approval | Needs approval | Blocked |

- All destructive actions (delete, kill, shutdown) require your confirmation
- NOVA can freely evolve its own personality and knowledge
- NOVA cannot touch files outside its directory without permission

---

## Known Limitations

- Windows-focused; macOS/Linux support is partial
- Requires Claude Code CLI to be authenticated and running
- Self-coding is experimental — always review proposals before approving
- Telegram bot requires manual setup (no OAuth flow yet)

---

## Roadmap

- [ ] Demo video / GIF in README
- [ ] macOS & Linux full support
- [ ] Web UI dashboard
- [ ] Plugin system for custom skills
- [ ] Voice input/output support
- [ ] CONTRIBUTING.md with detailed guide

---

## Tech Stack

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Claude_Code-6B4FBB?style=for-the-badge&logo=anthropic&logoColor=white"/>
  <img src="https://img.shields.io/badge/Telegram_Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white"/>
  <img src="https://img.shields.io/badge/ChromaDB-FF6F61?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/Graphify-00C853?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/GitHub_CLI-181717?style=for-the-badge&logo=github&logoColor=white"/>
</p>

---

## Contributing

Contributions are welcome!

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Have an idea or found a bug? [Open an issue](https://github.com/PATILYASHH/NOVA-AI/issues) — all feedback is appreciated.

---

## License

MIT License. See [`LICENSE`](LICENSE) for details.

---

<p align="center">
  Made by <a href="https://github.com/PATILYASHH"><strong>Yash Patil</strong></a>
</p>

<p align="center">
  <a href="https://github.com/PATILYASHH/NOVA-AI/stargazers"><img src="https://img.shields.io/github/stars/PATILYASHH/NOVA-AI?style=social" alt="Stars"/></a>
  <a href="https://github.com/PATILYASHH/NOVA-AI/network/members"><img src="https://img.shields.io/github/forks/PATILYASHH/NOVA-AI?style=social" alt="Forks"/></a>
</p>

<p align="center">
  <sub>Powered by Claude Code | ChromaDB | Graphify | python-telegram-bot</sub>
</p>
