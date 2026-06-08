# 🔮 Image Vision — AI Eyes for Your Desktop

> **"Boogie Woogie" your way through any image — screenshot, upload, or clipboard."**

---

## ⚡ Trigger Keywords

This skill activates whenever Claude detects:

| Trigger | Example |
|---------|---------|
| `/vision` command | `/vision`, `/vision screen`, `/vision ~/photo.jpg` |
| `[Unsupported Image]` in user message | VS Code pasted image |
| User asks to "see my screen" / "look at this" / "识别" / "看图" | Natural language |
| Screenshot request | "截图识别" / "capture and identify" |

---

## 🎯 Three-Level Architecture

When activated, Claude autonomously selects the correct pipeline:

### Level 1 — Screen Capture 🖥️
**When:** User says "看我屏幕" / "screen" / "桌面" / "截屏"

**Flow:**
1. Run `scripts/screen_capture.ps1` via PowerShell
2. Screenshot saved → Compressed if >1MB
3. Call Qwen-VL-Max API with `scripts/vision_api.py`
4. Present results in structured format

**Permission prompt:** _"Screen capture and send to Qwen-VL API"_

### Level 2 — File Path 📁
**When:** User provides explicit image path (`~/Desktop/photo.jpg`)

**Flow:**
1. Verify file exists, check size
2. Compress if >500KB (max 1200px width, JPEG quality 70)
3. Call Qwen-VL-Max API
4. Present results

**Permission prompt:** _"Read image file and send to Qwen-VL API"_

### Level 3 — VS Code Upload 📤
**When:** `[Unsupported Image]` appears in the message (image pasted/uploaded in VS Code)

**Flow:**
1. Run `scripts/extract_image.py` to extract latest base64 from Claude log
2. Decode and compress if needed
3. Call Qwen-VL-Max API
4. Present results

**Permission prompt:** _"Extract uploaded image from Claude log and send to vision API"_

---

## 🔧 Script Reference

All scripts in `scripts/` directory, relative to this skill.

| Script | Language | Purpose |
|--------|----------|---------|
| `scripts/screen_capture.ps1` | PowerShell | Capture primary screen, auto-compress |
| `scripts/vision_api.py` | Python 3 | Call Qwen-VL-Max with image + prompt |
| `scripts/extract_image.py` | Python 3 | Extract base64 image from Claude VS Code logs |
| `scripts/smart_compress.py` | Python 3 | Compress image to API-friendly size (used by all levels) |

---

## 📋 Execution Protocol

### Level 1 — Screen Capture
```bash
# Step 1: Capture screen
powershell -ExecutionPolicy Bypass -File "<SKILL_DIR>/scripts/screen_capture.ps1"

# Step 2: Vision API (runs automatically within screen_capture.ps1 or manually)
python3 "<SKILL_DIR>/scripts/vision_api.py" \
  --image "$TEMP/_screenshot_compressed.jpg" \
  --prompt "Describe this screenshot in detail. Include all visible windows, text, UI elements, and layout."
```

### Level 2 — File Vision
```bash
python3 "<SKILL_DIR>/scripts/vision_api.py" \
  --image "<provided_path>" \
  --prompt "Describe this image in detail. Include all visible text, layout, and content."
```

### Level 3 — Extract from Log
```bash
# Step 1: Extract latest image from Claude log
python3 "<SKILL_DIR>/scripts/extract_image.py"

# Step 2: Vision API on extracted image
python3 "<SKILL_DIR>/scripts/vision_api.py" \
  --image "$TEMP/_extracted_image.jpg" \
  --prompt "Describe this image in detail."
```

---

## 🎨 Output Format

Present results in this format:

```
## 🔮 识别结果

[Brief 1-line summary of what the image shows]

---

### 📊 Details

| Category | Content |
|----------|---------|
| **Key Thing** | Value |
| ... | ... |

---

[Any additional narrative or analysis]

⚡ *Qwen-VL-Max · <N> sec*
```

---

## ⚙️ Dependencies

- **PowerShell** (for screen capture on Windows)
- **Python 3.7+** with standard library only (no pip packages needed)
- **DashScope API Key** in environment variable `DASHSCOPE_API_KEY`
- **curl** or Python `urllib` for API calls

---

## 🔑 API Key Setup

```bash
# Set your DashScope API key
export DASHSCOPE_API_KEY="sk-your-key-here"
```

If not set, the skill will prompt you to configure it on first use.

---

## 🛡️ Error Handling

| Error | Response |
|-------|----------|
| No API key | _"🔑 需要配置 API Key，请设置 DASHSCOPE_API_KEY 环境变量"_ |
| Network timeout | Auto-retry once with smaller image. If still fails, tell user the API is unreachable |
| Image too large | Auto-compress before sending |
| Unsupported format | Convert to JPEG automatically |
| Claude log not found | Fall back to asking user for explicit file path |

---

## 💡 Smart Defaults

- **Prompt defaults** to Chinese detail description: `"请详细描述这张图片的内容，包括文字、布局、颜色、结构等信息。"`
- **Max output tokens:** 2000 (configurable)
- **Temperature:** 0.1 for consistent, factual output
- **Compression threshold:** 500KB for files, 1MB for screenshots
- **Auto-cleanup:** Temp files deleted after each call

---

## 🧪 Quick Test

After setup, run:
```bash
/vision screen
```
Should capture your desktop and describe what it sees.
