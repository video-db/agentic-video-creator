<div align="center">

# 🎬 Agentic Video Creator

**AI-powered video creation workflows** — autonomous agents that research, gather assets, and produce professional videos.

[![VideoDB](https://img.shields.io/badge/Powered_by-VideoDB-orange?style=for-the-badge)](https://videodb.io)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![GitHub stars](https://img.shields.io/github/stars/video-db/agentic-video-creator?style=for-the-badge)](https://github.com/video-db/agentic-video-creator)

[View Examples](#available-skills) • [Quick Start](#quick-start) • [Documentation](https://docs.videodb.io)

</div>

---

## What Is This?

A collection of **production-ready agentic skills** that autonomously create professional videos. Each skill follows a complete workflow: research → gather assets → generate scripts → assemble timeline → deliver video.

Built on [VideoDB](https://videodb.io) for video infrastructure and designed for Claude Code agents.

---

## Available Skills

| Skill | Description | Output | Runtime |
|-------|-------------|--------|---------|
| **[news-digest](news-digest/)** | Multi-source news digest videos with YouTube clips, tweets, and article analysis | 3-4 min broadcast-style video | ~15-20 min |
| **[financial-market-analysis](financial-market-analysis/)** | Proof-backed financial news recaps with charts, screenshots, and selected clips | Custom length market summary | Varies |

---

## Quick Start

### Prerequisites

1. **VideoDB API Key** (get free at [console.videodb.io](https://console.videodb.io))
   ```bash
   export VIDEO_DB_API_KEY=your_key_here
   ```

2. **VideoDB Python SDK**
   ```bash
   pip install videodb python-dotenv
   ```

3. **VideoDB Skill**
   ```bash
   npx skills add video-db/skills
   ```

### Usage

Each skill has its own detailed README. Pick one and give the agent a topic:

**News Digest:**
```
Create a news digest video about "climate summit 2026"
```

**Financial Analysis:**
```
Create a daily financial news video for 2026-04-01
```

The agent will autonomously research, gather assets, and deliver the final video.

---

## How It Works

Each agentic skill follows this pattern:

1. **Research** — Real web research via browser-use (no hallucinated data)
2. **Asset Collection** — YouTube videos, tweets, article screenshots, charts
3. **Script Writing** — Professional voiceover scripts with TTS generation
4. **Timeline Assembly** — 5-track composition with VideoDB Editor
5. **Delivery** — Stream URL + metadata

**Output:** Professional videos ready to publish.

---

## Example Outputs

### News Digest
**Iran War 2026** — Multi-source analysis with Al Jazeera, BBC, CNN  
[▶ Watch Video](https://console.videodb.io/player?url=https://play.videodb.io/v1/e979397c-58c3-4f74-ad45-e5b4736d1d77.m3u8) (3:31)

### Financial Market Analysis
**Daily Market Recap** — Proof-backed financial news with charts, screenshots, and clips  
[▶ Watch Video](https://console.videodb.io/player?url=https://play.videodb.io/v1/f37914dd-5239-4c10-aa2e-006f9095ac7c.m3u8)

---

## Key Features

### 🔍 Real Web Research
Every fact, URL, and asset comes from actual web sources. Browser-use skill handles all internet access. No hallucinated data.

### 🎥 Professional Quality
- Broadcast-style text overlays
- Multi-track timeline composition
- Background music and voiceovers
- Clean typography and transitions

### 🤖 Fully Autonomous
Give the agent a topic → get a finished video. No manual intervention required.

### 📊 Proof-Backed
Every claim is sourced. Every asset is verified. Perfect for news, finance, and compliance use cases.

---

## Philosophy

Each skill is:
- **Self-contained** — All dependencies documented
- **Reproducible** — Same inputs → same outputs
- **Agent-friendly** — Clear instructions, no ambiguity
- **Production-ready** — Battle-tested workflows

---

## Requirements

- Python 3.8+
- VideoDB API key ([get free](https://console.videodb.io))
- VideoDB skill and Python SDK
- Claude Code or compatible agent framework

---

## Contributing

Contributions welcome! To add a new skill:

1. Create a new folder with `SKILL.md`, `AGENTS.md`, and `README.md`
2. Follow the structure of existing skills
3. Include working examples
4. Submit a PR

---


## Community & Support

- **Docs**: [docs.videodb.io](https://docs.videodb.io)
- **Issues**: [GitHub Issues](https://github.com/video-db/agentic-video-creator/issues)
- **Discord**: [Join community](https://discord.gg/py9P639jGz)
- **Console**: [Get API key](https://console.videodb.io)

---

<p align="center">Made with ❤️ by the <a href="https://videodb.io">VideoDB</a> team</p>

---
