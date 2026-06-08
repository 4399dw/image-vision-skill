# 🔮 Image Vision — AI Eyes for Claude Code

> **"Your desktop has a story. Let Claude read it."**

[![Skill Type](https://img.shields.io/badge/Claude%20Code-Skill-8A2BE2?logo=claude&logoColor=white)](https://claude.ai/code)
[![PowerShell](https://img.shields.io/badge/PowerShell-✓-5391FE?logo=powershell&logoColor=white)](https://learn.microsoft.com/en-us/powershell/)
[![Python](https://img.shields.io/badge/Python-3.7+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![API](https://img.shields.io/badge/Qwen--VL--Max-DashScope-FF6A00)](https://dashscope.aliyun.com/)

---

## ✨ What It Does

Image Vision gives Claude Code **superhuman eyes** — it can look at your screen, analyze any image, and extract text, layout, and visual details with precision.

| Mode | Trigger | What Happens |
|------|---------|--------------|
| 🖥️ **Screen Capture** | `/vision screen` | Captures your desktop, identifies everything on it |
| 📁 **File Vision** | `/vision ~/photo.jpg` | Reads and analyzes any image file |
| 📤 **VS Code Upload** | Paste an image | Auto-detects `[Unsupported Image]`, extracts from log, identifies |

---

## 🚀 Quick Start

### 1. Install

```bash
# Clone into your Claude Code skills directory
git clone https://github.com/4399dw/image-vision-skill.git ~/.claude/skills/image-vision
```

Or manually:
```bash
mkdir -p ~/.claude/skills/image-vision
cp -r ./* ~/.claude/skills/image-vision/
```

### 2. Set API Key

```bash
export DASHSCOPE_API_KEY="sk-your-dashscope-key"
```

Get a key from [DashScope Console](https://dashscope.console.aliyun.com/).

### 3. Use It

```
/vision screen              # What's on my screen?
/vision ~/Desktop/photo.jpg # What's in this image?
/vision                     # Auto-detect image in context
```

Claude will ask for permission — click **"Allow"** and watch the magic.

---

## 🎯 Real Examples

```
You: /vision screen
Claude: [asks permission] → Screenshot → API →
  "你的桌面上有：
   - VS Code 正在编辑 app.tsx
   - 浏览器打开了 GitHub PR #42
   - 右下角微信有新消息
   - 时间是 14:32"
```

```
You: [pastes a screenshot of a Chinese homework assignment]
Claude: [auto-detects] → Extracts from log → API →
  "这是一张手绘思维导图，中心主题：求职岗位
   - 公司及岗位背景：青岛日日顺...
   - 岗位要求：物流/供应链本科...
   - 核心工作内容：运输调度、仓储管理..."
```

---

## 🏗️ Architecture

```
~/.claude/skills/image-vision/
├── image-vision.md          ← Skill definition (Claude reads this)
├── README.md                ← You are here
└── scripts/
    ├── screen_capture.ps1   ← PowerShell: capture + auto-compress
    ├── vision_api.py        ← Python: Qwen-VL-Max API caller
    ├── extract_image.py     ← Python: extract base64 from Claude log
    └── smart_compress.py    ← Python: resize/compress images
```

### Flow: Three Pathways, One Engine

```
┌─────────────────────┐
│   User Input        │
│  Image Detected     │
└────────┬────────────┘
         │
    ┌────┴────┐
    │  Route  │  ← Claude autonomously decides
    └────┬────┘
         │
   ┌─────┼─────────────┐
   │     │             │
   ▼     ▼             ▼
┌────┐ ┌────┐     ┌────────┐
│ L1 │ │ L2 │     │   L3   │
│ 🖥️  │ │ 📁 │     │   📤   │
│ PS │ │Path│     │Extract │
└──┬─┘ └──┬─┘     └───┬────┘
   │      │            │
   └──────┼────────────┘
          ▼
   ┌─────────────┐
   │  vision_api │  ← Unified API caller
   │   Qwen-VL   │
   └──────┬──────┘
          ▼
   ┌─────────────┐
   │  Result     │
   │  Formatted  │
   └─────────────┘
```

---

## 🛡️ Permissions

This skill requires:

| Permission | Why |
|------------|-----|
| Screen capture (PowerShell) | To take desktop screenshots |
| Read image files | To analyze user-provided images |
| Read Claude logs | To extract VS Code pasted images |
| Network → `dashscope.aliyuncs.com` | Qwen-VL API calls |
| Temporary file write | Cache compressed images |

Claude Code will **prompt you before each action** — you're always in control.

---

## ⚙️ Configuration

```bash
# Environment variables
DASHSCOPE_API_KEY   # Required: your DashScope API key
PYTHONIOENCODING    # Optional: force UTF-8 (set to utf-8)

# Skill tuning (edit image-vision.md)
MAX_TOKENS          # Default: 2000
TEMPERATURE         # Default: 0.1 (factual output)
COMPRESS_THRESHOLD  # Default: 500KB for files, 1MB for screenshots
```

---

## 🌍 Cross-Platform

| OS | Screen Capture | File Vision | VS Code Upload |
|----|---------------|-------------|----------------|
| 🪟 **Windows** | ✅ PowerShell | ✅ | ✅ (VS Code log) |
| 🍎 **macOS** | 🔜 (use `screencapture`) | ✅ | ✅ |
| 🐧 **Linux** | 🔜 (use `import`/`grim`) | ✅ | ✅ |

*Contributions welcome for macOS/Linux screen capture!*

---

## 🔬 Under the Hood

- **API:** [Qwen-VL-Max](https://help.aliyun.com/zh/model-studio/) via DashScope (兼容 OpenAI 格式)
- **Model:** Vision-language model optimized for Chinese + English
- **Cost:** ~¥0.005/image (as of 2026, DashScope pricing)
- **Latency:** 2–8 seconds per image (depends on size)
- **Image support:** PNG, JPEG, GIF, WebP, BMP

---

## 👥 Authors

Created by **Dongtang Kui & Huzhang Youren** (东堂葵 & 虎杖优仁)

> *"我们就是最强的组合，Boogie Woogie！"*

---

## 📄 License

MIT — Use it, remix it, share it. Just keep the spirit of Boogie Woogie alive. ✋🤜

---

## ⭐ Star This If

- [ ] You've ever wanted Claude to see your screen
- [ ] You do homework with mind maps and screenshots
- [ ] You think AI + desktop vision is the future
- [ ] You appreciate a good Jujutsu Kaisen reference

---

*Made with 🔮 and ✋🤜 Boogie Woogie energy*
