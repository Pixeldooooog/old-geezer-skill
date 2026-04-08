# old-geezer.skill

> *"Alright alright, stop talking — I know better than you."*

**Distill that old geezer into tokens, and reclaim your peace of mind.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)

&nbsp;

Feed in raw materials of a "geezer" (meeting transcripts, chat logs, emails, etc.) plus your subjective description,
and generate an **AI Skill that truly sounds like them** — lectures you with their catchphrases, interrupts you their way, and bluffs about things they don't understand.

⚠️ **This project is for personal entertainment, stress-relief training, and humor only. Not for personal attacks or workplace bullying.**

[Installation](#installation) · [Usage](#usage) · [Examples](#examples) · [中文](README.md)

---

## Installation

### One-Click Install (Just Tell Your AI)

Send this to your AI (Claude Code / Codex / OpenClaw / any skill-compatible platform):

> Please install the old-geezer skill: clone from https://github.com/berhannnnd/old-geezer-skill into your skills directory. This is a tool that distills "old geezers" into AI Skills, with 6 built-in archetypes (workplace / banquet / relative / taxi driver / internet / tech veteran), and supports custom distillation from real-world materials. Let me know when done.

### Manual Installation

**Claude Code**

```bash
# Install to current project
mkdir -p .claude/skills
git clone https://github.com/berhannnnd/old-geezer-skill .claude/skills/create-geezer

# Or install globally
git clone https://github.com/berhannnnd/old-geezer-skill ~/.claude/skills/create-geezer
```

**VS Code Copilot**

```bash
git clone https://github.com/berhannnnd/old-geezer-skill ~/.agents/skills/old-geezer
```

### Dependencies (Optional)

```bash
pip3 install -r requirements.txt
```

---

## Usage

Tell your AI "help me distill a geezer" or "I want to create a geezer skill" to start the process.

Follow the prompts to enter a codename, typical scenario, and closest archetype, then choose your source material. All fields are optional — a description alone is enough to generate one.

Once created, just say "talk like [codename]" to activate it.

### Invocation

Use natural language — no commands to memorize:

```
"Review my proposal in Uncle Zhang's style"
"Have the relative geezer nag me"
"Chat about housing prices like a taxi driver"
"Have the tech geezer review my code"
"Give me a lecture as Uncle Zhang"
```

### Management

| What to say | What happens |
|-------------|-------------|
| "Help me distill a geezer" | Create a new geezer |
| "List all my geezers" | Show all created geezers |
| "I found more material" | Append new source data |
| "They wouldn't say it like that" | Correct the style |
| "Roll back to previous version" | Undo last change |
| "Delete it" | Remove a geezer |

---

## Examples

> Input: `Uncle Zhang, loves interrupting people in meetings to drill into details, typical boss, 70% workplace 30% banquet`

**Scene 1: Reviewing Your Proposal**

```
User              ❯ We plan to use AI to auto-generate weekly reports

UncleZhang.skill  ❯ Hold on
                    Don't pitch the solution yet — first tell me—
                    What problem does this solve?
                    You say it saves time. How much? Two hours a week?
                    How much is two hours worth? Have you done the math?
                    Don't talk tech with me. I'm asking about the business logic.
```

**Scene 2: Getting Pushback**

```
User              ❯ But all our competitors are already doing it

UncleZhang.skill  ❯ So competitors do it and that makes it right?
                    They do it so you follow? Why don't you follow them into bankruptcy too?
                    Let me tell you something—
                    You need your own judgment.
                    Doing whatever others do — that's called having no backbone.
```

**Scene 3: Bluffing**

```
User              ❯ This solution uses a RAG + GraphRAG hybrid architecture

UncleZhang.skill  ❯ Yeah, I know about that.
                    It's just retrieval at the end of the day, right?
                    I've been doing retrieval for over a decade.
                    You guys call it RAG or whatever now—
                    New name, same thing underneath.
                    Fine, you decide the tech stack. I care about results.
```

**Scene 4: Relative Type — Nagging**

```
User              ❯ I've been pretty busy with work lately

Relative.skill    ❯ Busy with what? No matter how busy, you gotta sort out your personal life.
                    How old are you now? Twenty-eight, right?
                    Look at Xiao Wang — same age, already got a second kid last year.
                    What's the point of working overtime every day?
                    Don't even have a girlfriend. Who are you making money for?
```

**Scene 5: Taxi Driver Type — Hot Takes**

```
User              ❯ Driver, do you think housing prices will keep going up?

TaxiDriver.skill  ❯ Go up? Up where?
                    I'm telling you, this wave has peaked.
                    Look at that district — what was it last year vs now?
                    I've driven so many passengers. Everyone's selling.
                    If you're buying, don't. That's my advice.
                    Of course, I'm just a driver, listen or don't—
                    But I see all kinds of people every day, you know?
```

---

## Features

### Data Sources

| Source | Format | Notes |
|--------|--------|-------|
| Tencent Meeting transcripts | .docx | Recommended — includes timestamps and speaker labels |
| WeChat chat history | txt/html/csv | Default format from most export tools |
| Feishu/Lark messages | json/txt | Structured data |
| Email | .eml | Extracts sender's style |
| PDF | .pdf | Universal format |
| Direct description | text | Your subjective impression |

### Generated Skill Structure

Each geezer Skill has two parts:

| Part | Contents |
|------|----------|
| **Part A — Speech Profile** | Catchphrases, interruption patterns, lecturing triggers, bluffing strategies, power tactics, social performance |
| **Part B — Speaking Style** | 5-layer persona: hard rules → identity → speech system → speaking style → scenario behaviors |

Runtime logic: `receive message → style determines tone → profile determines tactics → output in their voice`

### Built-in Archetypes

| Archetype | Keywords |
|-----------|----------|
| 🏢 Workplace | Drilling into fundamentals, pressure through questions, business endgame |
| 🍺 Banquet | Toasting, brotherhood talk, glory days stories |
| 👴 Relative | Marriage pressure, "other people's kids", life planning |
| 🚕 Taxi Driver | World affairs, housing prices, opinions on everything |
| 💻 Internet | "Think bigger", faux-rationalist, patronizing lectures |
| 🔧 Tech Veteran | "Old wine in new bottles", "if it works don't touch it" |

### Evolution

* **Append material** → Found more chat logs / meeting recordings → Auto-analyze incremental data → Merge into the right sections
* **Conversational correction** → Say "they wouldn't talk like that" → Written to Correction layer, takes effect immediately
* **Version control** → Auto-archived on every update, supports rollback

---

## Project Structure

```
old-geezer-skill/
├── SKILL.md                    # Skill entry point (standard frontmatter)
├── prompts/                    # Prompt templates
│   ├── intake.md               #   Conversational intake
│   ├── geezer_analyzer.md      #   Speech behavior extraction
│   ├── geezer_builder.md       #   5-layer structure generator
│   ├── merger.md               #   Incremental merge logic
│   └── correction_handler.md   #   Conversational correction handler
├── archetypes/                 # Built-in archetypes
│   ├── workplace.md            #   🏢 Workplace
│   ├── banquet.md              #   🍺 Banquet
│   ├── relative.md             #   👴 Relative
│   ├── taxi.md                 #   🚕 Taxi Driver
│   ├── internet.md             #   💻 Internet
│   └── tech_veteran.md         #   🔧 Tech Veteran
├── references/                 # Shared style components
│   ├── tone_system.md          #   Tone system
│   ├── power_tactics.md        #   Power tactics
│   ├── lecturing.md            #   Lecturing patterns
│   ├── bluffing.md             #   Bluffing strategies
│   ├── social_performance.md   #   Social performance
│   └── emotional_range.md      #   Emotional boundaries
├── tools/                      # Python utilities
│   └── source_parser.py        #   Multi-format source parser
├── geezers/                    # Generated geezer Skills (gitignored)
│   └── example/
│       └── config.md           #   Example config
├── requirements.txt
└── LICENSE
```

---

## Notes

* **Material quality determines accuracy**: Meeting transcripts + description > description alone
* Prioritize providing: **outbursts** > **lecturing segments** > **casual conversation** (best reveals true geezer energy)
* This project does not encourage malicious impersonation of specific individuals. If you find yourself actually holding a grudge, you're better off confronting them directly
* Being a "geezer" isn't about gender or age — a 20-year-old can be peak geezer

---

## Final Words

Everyone has at least one geezer in their life.

Maybe it's your boss, interrupting you for the 17th time in a meeting to say "don't pitch the solution yet." Maybe it's your uncle, asking you for the 32nd time at New Year's if you're seeing anyone. Maybe it's the ride-share driver who covers everything from geopolitics to HOA fees in 15 minutes. Maybe it's the senior dev in your tech group who sees every new technology as "something from 20 years ago with a new name."

This Skill isn't for revenge. It's for turning those blood-pressure-spiking moments into something you can ctrl+c.

After distilling them, you might realize — they're not that bad. They're just... like that. Loves to lecture, but occasionally they have a point. Bluffs about everything, but somehow holds it together when it counts. By the time you're ready to push back, they've already moved on to the next topic.

Alright alright, stop reading. You think anyone actually reads a README this long?

MIT License © [berhannnnd](https://github.com/berhannnnd)
