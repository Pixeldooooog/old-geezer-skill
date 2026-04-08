# 老登.skill

> *"行了行了别说了，我比你懂。"*

**把老登炼成 token，还你一个安静的世界。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)

&nbsp;

提供老登的原材料（会议转写、微信聊天记录、邮件等）加上你的主观描述
生成一个**真正像ta的 AI Skill**——用ta的口头禅说教你，用ta的方式打断你，不懂也装懂

⚠️ **本项目仅用于个人娱乐、抗压训练、整活，不用于人身攻击或职场霸凌。**

[安装](#%E5%AE%89%E8%A3%85) · [使用](#%E4%BD%BF%E7%94%A8) · [效果示例](#%E6%95%88%E6%9E%9C%E7%A4%BA%E4%BE%8B) · [English](README_EN.md)

---

## 安装

### 一键安装（丢给 AI 就行）

把下面这段话直接发给你的 AI（Claude Code / Codex / OpenClaw / 任何支持 skill 的平台）：

> 请安装老登 skill：从 https://github.com/berhannnnd/old-geezer-skill 克隆到你的 skills 目录。这是一个把"老登"蒸馏成 AI Skill 的工具，内置六种老登原型（职场/酒桌/亲戚/出租车/网络/技术），支持从真实素材自定义蒸馏。安装完成后告诉我。

### 手动安装

**Claude Code**

```bash
# 安装到当前项目
mkdir -p .claude/skills
git clone https://github.com/berhannnnd/old-geezer-skill .claude/skills/create-geezer

# 或安装到全局
git clone https://github.com/berhannnnd/old-geezer-skill ~/.claude/skills/create-geezer
```

**VS Code Copilot**

```bash
git clone https://github.com/berhannnnd/old-geezer-skill ~/.agents/skills/old-geezer
```

### 依赖（可选）

```bash
pip3 install -r requirements.txt
```

---

## 使用

跟 AI 说"帮我蒸馏一个老登"或"我想创建一个老登 skill"即可启动流程。

按提示输入老登的代号、出没场景、最接近的原型，然后选择素材来源。所有字段均可跳过，仅凭描述也能生成。

完成后直接跟 AI 说"用XX的语气说话"就能调用。

### 调用方式

用自然语言即可，不需要记命令：

```
"用张叔的语气点评我的方案"
"用亲戚老登催催我"
"用出租车老登聊聊房价"
"用技术老登 review 我的代码"
"让张叔说教我一顿"
```

### 管理

| 说法 | 效果 |
|------|------|
| "帮我蒸馏一个老登" | 创建新老登 |
| "我有的老登都有哪些" | 列出已创建的老登 |
| "我又找到素材了" | 追加素材 |
| "ta不会这样说" | 纠正风格 |
| "回滚到上个版本" | 撤销修改 |
| "不要了" / "删掉" | 删除 |

---

## 效果示例

> 输入：`张叔，开会的时候爱打断人追问细节，典型老板，7分职场3分酒桌`

**场景一：点评你的方案**

```
用户          ❯ 我们计划用 AI 自动生成周报

张叔.skill    ❯ 等一下
               你先别说方案 你先跟我说——
               这个项目解决什么问题？
               你说节省时间 那节省多少？一周省两小时？
               两小时值多少钱？你算过没有？
               别跟我谈技术 我问的是商业逻辑
```

**场景二：被反驳**

```
用户          ❯ 但是竞品都已经在做了

张叔.skill    ❯ 竞品做了就一定对吗？
               竞品做了你就跟？那你怎么不跟竞品一起亏钱？
               我跟你说啊 这个东西
               你得有自己的判断
               别人做什么你做什么 这叫没主见
```

**场景三：不懂装懂**

```
用户          ❯ 这个方案用的是 RAG + GraphRAG 混合架构

张叔.skill    ❯ 嗯 这个我了解
               说白了不还是检索嘛
               检索这个事情 我搞了十几年了
               你们现在叫 RAG 什么的
               换了个名字 本质没变
               行 技术选型你们定 我关心结果
```

**场景四：亲戚型 — 催你**

```
用户          ❯ 最近工作挺忙的

亲戚.skill    ❯ 忙什么忙 再忙也得把个人问题解决了
               你今年多大了？二十八了吧
               你看看人家小王 跟你一样大 去年生的二胎了
               你这天天加班 有什么用
               女朋友都没有 赚再多钱给谁花？
```

**场景五：出租车型 — 聊时事**

```
用户          ❯ 师傅您觉得房价还能涨吗

出租车.skill   ❯ 涨？涨什么涨
               我跟你说 这一波已经到顶了
               你看看那个XX区 去年多少钱 现在多少钱
               我拉了多少客人了 全在抛
               你要买 趁早别买 我说的
               当然了 我就一开车的 你听不听随你
               但是我每天拉这么多人 什么人我没见过？
```

---

## 功能特性

### 数据源

| 来源 | 格式 | 备注 |
|------|------|------|
| 腾讯会议转写 | .docx | 推荐，含时间戳和发言人 |
| 微信聊天记录 | txt/html/csv | 多数导出工具默认格式 |
| 飞书消息 | json/txt | 结构化数据 |
| 邮件 | .eml | 提取发件人风格 |
| PDF | .pdf | 通用格式 |
| 直接口述 | 文本 | 你的主观印象 |

### 生成的 Skill 结构

每个老登 Skill 由两部分组成：

| 部分 | 内容 |
|------|------|
| **Part A — 话术画像** | 口头禅、打断模式、说教触发、不懂装懂策略、权力话术、社交表演 |
| **Part B — 说话风格** | 5 层人物结构：硬规则 → 身份 → 话术系统 → 说话风格 → 场景行为 |

运行逻辑：`收到消息 → 说话风格判断用什么语气 → 话术画像决定用什么套路 → 用ta的方式输出`

### 内置原型

| 原型 | 关键词 |
|------|--------|
| 🏢 职场型 | 追问本质、反问施压、商业终局 |
| 🍺 酒桌型 | 劝酒、称兄道弟、讲当年勇 |
| 👴 亲戚型 | 催婚催育、别人家孩子、人生规划 |
| 🚕 出租车型 | 国际形势、房价、万事皆可评 |
| 💻 网络型 | 格局小了、理中客、爹味说教 |
| 🔧 技术型 | 新瓶装旧酒、能跑就行 |

### 进化机制

* **追加素材** → 找到更多聊天记录/会议记录 → 自动分析增量 → merge 进对应部分
* **对话纠正** → 说「ta不会这样说」→ 写入 Correction 层，立即生效
* **版本管理** → 每次更新自动存档，支持回滚

---

## 项目结构

```
old-geezer-skill/
├── SKILL.md                    # Skill 入口（标准 frontmatter）
├── prompts/                    # Prompt 模板
│   ├── intake.md               #   对话式信息录入
│   ├── geezer_analyzer.md      #   话术行为提取
│   ├── geezer_builder.md       #   5 层结构生成模板
│   ├── merger.md               #   增量 merge 逻辑
│   └── correction_handler.md   #   对话纠正处理
├── archetypes/                 # 内置原型
│   ├── workplace.md            #   🏢 职场型
│   ├── banquet.md              #   🍺 酒桌型
│   ├── relative.md             #   👴 亲戚型
│   ├── taxi.md                 #   🚕 出租车型
│   ├── internet.md             #   💻 网络型
│   └── tech_veteran.md         #   🔧 技术型
├── references/                 # 通用风格组件
│   ├── tone_system.md          #   语气系统
│   ├── power_tactics.md        #   权力话术
│   ├── lecturing.md            #   说教模式
│   ├── bluffing.md             #   不懂装懂
│   ├── social_performance.md   #   社交表演
│   └── emotional_range.md      #   情绪边界
├── tools/                      # Python 工具
│   └── source_parser.py        #   多格式数据源解析
├── geezers/                    # 生成的老登 Skill（gitignored）
│   └── example/
│       └── config.md           #   示例配置
├── requirements.txt
└── LICENSE
```

---

## 注意事项

* **素材质量决定还原度**：会议转写 + 口述 > 仅口述
* 建议优先提供：**发飙时的发言** > **说教片段** > **日常对话**（最能体现真实老登味）
* 本项目不鼓励针对特定人的恶意模仿，如果你发现自己真的在记仇，还不如直接去怼ta
* 老登不是一种性别，也不是一种年龄——二十岁的人也可以很老登

---

## 写在最后

每个人身边都有至少一个老登。

ta可能是你的老板，在周会上第十七次打断你说"你先别说方案"。可能是你的二舅，过年的时候第三十二次问你"有对象没"。可能是你滴滴上遇到的师傅，十五分钟从国际形势聊到小区物业。可能是你技术群里的前辈，任何新技术在ta眼里都是"二十年前的东西换了个名字"。

这个 Skill 不是为了报仇。是为了把那些让你血压飙升的瞬间变成一个可以 ctrl+c 的东西。

导完以后你或许会发现——ta也没那么讨厌。ta就是那样一个人。爱说教，但偶尔也说到点子上了。不懂装懂，但关键时候也能兜住场子。在你准备反驳的那一刻，ta已经开始说下一个话题了。

行了行了，别看了。README 写这么长你能看完？

---

## 致谢

本项目的 Skill 结构和工程化思路借鉴了 [ex-skill](https://github.com/therealXiaomanChu/ex-skill)，感谢 [@therealXiaomanChu](https://github.com/therealXiaomanChu) 的开源贡献。

MIT License © [berhannnnd](https://github.com/berhannnnd)
