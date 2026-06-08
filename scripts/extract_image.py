#!/usr/bin/env python3
"""
🔍 Extract Image — Pull the latest base64 image from Claude VS Code logs.
Part of the Image Vision skill for Claude Code.

When a user pastes/uploades an image in VS Code, Claude Code receives
it as [Unsupported Image] because the base64 data is embedded in the
Claude VSCode log file, not saved to disk.

This script:
1. Finds the most recent Claude VSCode log directory
2. Extracts the latest base64 image from the log
3. Decodes and saves it as a temp file
4. Prints the path for downstream use

Usage:
    python3 extract_image.py
    # Output: C:\Users\...\Temp\_extracted_image.jpg
"""
import os
import re
import json
import base64
import sys
from pathlib import Path
from datetime import datetime

# ──────────────────────────────────────────────
# 1. Find Claude log directory
# ──────────────────────────────────────────────
APPDATA = os.environ.get("APPDATA", "")
LOG_BASE = Path(APPDATA) / "Code" / "logs"

if not LOG_BASE.exists():
    print("❌ VS Code logs directory not found")
    sys.exit(1)

# Find the most recent log directory
log_dirs = sorted(
    [d for d in LOG_BASE.iterdir() if d.is_dir()],
    reverse=True
)

claude_log = None
for log_dir in log_dirs:
    candidate = log_dir / "window1" / "exthost" / "Anthropic.claude-code" / "Claude VSCode.log"
    if candidate.exists():
        claude_log = candidate
        break

if not claude_log:
    print("❌ Claude VSCode log not found")
    sys.exit(1)

print(f"📋 Log: {claude_log}")

# ──────────────────────────────────────────────
# 2. Find latest image entry
# ──────────────────────────────────────────────
with open(claude_log, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

# Search from end for speed (latest image is at the bottom)
b64data = None
media_type = "image/jpeg"

for i in range(len(lines) - 1, -1, -1):
    line = lines[i]
    if '"type":"image"' in line:
        # Extract base64 data
        match = re.search(r'"data":"([^"]+)"', line)
        if match:
            b64data = match.group(1)
            # Check media type
            mt_match = re.search(r'"media_type":"([^"]+)"', line)
            if mt_match:
                media_type = mt_match.group(1)
            break

if not b64data:
    print("❌ No embedded image found in recent log entries")
    sys.exit(1)

print(f"🔐 Base64: {len(b64data):,} chars")
print(f"📁 Type: {media_type}")

# ──────────────────────────────────────────────
# 3. Decode and save
# ──────────────────────────────────────────────
try:
    img_bytes = base64.b64decode(b64data)
except Exception as e:
    print(f"❌ Base64 decode failed: {e}")
    sys.exit(1)

TEMP = Path(os.environ.get("TEMP", "/tmp"))

# Determine extension
ext = ".jpg"
if "png" in media_type:
    ext = ".png"
elif "gif" in media_type:
    ext = ".gif"
elif "webp" in media_type:
    ext = ".webp"

outpath = TEMP / f"_extracted_image{ext}"
with open(outpath, "wb") as f:
    f.write(img_bytes)

print(f"💾 Saved: {outpath} ({len(img_bytes):,} bytes)")
print(outpath)  # ← This is the key output line — downstream scripts read this
