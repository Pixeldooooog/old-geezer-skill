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

> Please install the old-geezer skill: clone from https://github.com/Pixeldooooog/old-geezer-skill into your skills directory. This is a tool that distills "old geezers" into AI Skills, with 6 built-in archetypes (workplace / banquet / relative / taxi driver / internet / tech veteran), and supports custom distillation from real-world materials. Let me know when done.

### Manual Installation

**Claude Code**

```bash
# Install to current project
mkdir -p .claude/skills
git clone https://github.com/Pixeldooooog/old-geezer-skill .claude/skills/create-geezer

# Or install globally
git clone https://github.com/Pixeldooooog/old-geezer-skill ~/.claude/skills/create-geezer
```

**VS Code Copilot**

```bash
git clone https://github.com/Pixeldooooog/old-geezer-skill ~/.agents/skills/old-geezer
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

One scene per archetype, showcasing different flavors of geezer energy:

**🏢 Workplace — "Don't Pitch the Solution Yet"**

```
User              ❯ We want to use AI to improve customer service efficiency

Workplace.skill   ❯ Hold on.
                    Don't pitch the solution yet — first tell me—
                    How many tickets does support handle per day? What's the cost?
                    How much can AI bring it down? Have you calculated the ROI?
                    Don't talk tech with me. I'm asking about the business logic.
                    Your engineers' problem is always looking for nails when you have a hammer.
                    Send me the requirements doc. I'll review it tomorrow.
```

**🍺 Banquet — "Not Drinking Means You Don't Respect Me"**

```
User              ❯ I can't really drink, I'll have a soda

Banquet.skill     ❯ Soda? You must be joking.
                    Do you know what this is? Moutai. 53 proof.
                    People would kill for a glass.
                    Here — I'll toast you. You sip, I'll down it.
                    Let me tell you, when I was your age,
                    I closed a three-million-dollar deal over one dinner.
                    You young people are all about "wellness" now.
                    What's one drink? It's called social skills.
```

**👴 Relative — "Look at How Well Little Wang Is Doing"**

```
User              ❯ I've been learning to paint lately

Relative.skill    ❯ Paint? Can painting pay the bills?
                    How old are you now? Got a partner yet?
                    Your cousin is about your age, you know—
                    her kid's already in kindergarten.
                    Your mom tells me about you all the time. Says you're not worried at all.
                    That college classmate of yours, Xiao Wang — works at a bank.
                    Makes 200K a year plus housing fund.
                    How much does your painting bring in a month?
```

**🚕 Taxi Driver — "What Haven't I Seen?"**

```
User              ❯ What do you think about the economy right now?

TaxiDriver.skill  ❯ Think what? The guy before you used to drive a Porsche.
                    Now he's taking my cab. Let that sink in.
                    I'm telling you, this economy? Not recovering for years.
                    See that office tower? Lit up like Christmas last year.
                    Half dark now. Everyone moved out.
                    Picked up a kid two days ago, opened a bubble tea shop,
                    lost 400K in six months. I said, shoulda listened to me.
                    I'm on the road twelve hours a day.
                    Who has better intel than me? Nobody.
```

**💻 Internet — "Think Bigger"**

```
User              ❯ PinkPantheress makes great music

Internet.skill    ❯ Objectively speaking — not targeting you personally—
                    but can you call a two-minute song "music"?
                    Have you listened to Jay Chou's "In the Name of the Father"?
                    Now THAT's arrangement. THAT's depth.
                    You Gen Z kids got your brains rewired by short videos.
                    Can't even focus for three minutes.
                    I'd suggest systematically listening to some 90s albums first.
                    Build your aesthetic foundation before making judgments.
                    Think bigger. Stop living in your filter bubble.
```

**🔧 Tech Veteran — "Old Wine in New Bottles"**

```
User              ❯ I'm planning to deploy this on Kubernetes

TechVet.skill     ❯ K8s?
                    It's just container orchestration when you strip it down.
                    Fifteen years ago I managed clusters with shell scripts.
                    Same thing. New name, same idea.
                    For your scale? Three machines would do the job.
                    How many people on your team can even operate K8s?
                    The learning curve alone will eat you alive.
                    If it works, why mess with it?
                    Wait till something breaks at 3AM and you're on your own.
                    Then you'll understand: simplicity is king.
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

---

## Acknowledgements

The Skill structure and engineering approach of this project was inspired by [ex-skill](https://github.com/therealXiaomanChu/ex-skill). Thanks to [@therealXiaomanChu](https://github.com/therealXiaomanChu) for the open-source contribution.

MIT License © [Pixeldooooog](https://github.com/Pixeldooooog)
