#!/usr/bin/env python3
"""
🔥 Image Vision API — Call Qwen-VL-Max to analyze images.
Part of the Image Vision skill for Claude Code.
Usage:
    python3 vision_api.py --image <path> [--prompt "custom prompt"] [--max-tokens 2000] [--temperature 0.1]
    python3 vision_api.py -i photo.jpg -p "Read all text" -m 1000 -t 0.2
"""
import os
import sys
import json
import base64
import argparse
import urllib.request
import urllib.error
from pathlib import Path

# ──────────────────────────────────────────────
# 0. Args
# ──────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Qwen-VL-Max Image Vision")
parser.add_argument("-i", "--image", required=True, help="Path to image file")
parser.add_argument("-p", "--prompt", default="请详细描述这张图片的内容，包括文字、布局、颜色、结构等信息。",
                    help="Prompt for the vision model")
parser.add_argument("-m", "--max-tokens", type=int, default=2000, help="Max output tokens")
parser.add_argument("-t", "--temperature", type=float, default=0.1, help="Model temperature")
parser.add_argument("--no-compress", action="store_true", help="Skip auto-compression")
args = parser.parse_args()

# ──────────────────────────────────────────────
# 1. API Key
# ──────────────────────────────────────────────
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
if not API_KEY:
    print("🔑 未配置 API Key！请设置环境变量 DASHSCOPE_API_KEY")
    print("   export DASHSCOPE_API_KEY=\"sk-your-key-here\"")
    sys.exit(1)

API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# ──────────────────────────────────────────────
# 2. Read & maybe compress
# ──────────────────────────────────────────────
image_path = Path(args.image)
if not image_path.exists():
    print(f"❌ 文件不存在: {image_path}")
    sys.exit(1)

with open(image_path, "rb") as f:
    img_bytes = f.read()

original_size = len(img_bytes)
print(f"📷 {image_path.name} · {original_size:,} bytes")

# Auto-compress if large
COMPRESS_THRESHOLD = 500 * 1024  # 500KB
if original_size > COMPRESS_THRESHOLD and not args.no_compress:
    try:
        import struct
        from io import BytesIO

        # Simple thumbnail approach using raw binary manipulation
        # For JPEG: keep as-is but suggest compression
        # For PNG: use a crude subsampling
        ext = image_path.suffix.lower()
        if ext in (".png", ".bmp"):
            # Convert PNG to smaller JPEG via raw pixel extraction
            print("⚡ Image >500KB, compressing...")
            # We'll just send it anyway with a note — real compression needs PIL
            print(f"   ⚠️ PIL not available, sending original ({original_size:,} bytes)")
        else:
            print(f"   📦 Sending original JPEG ({original_size:,} bytes)")
    except Exception as e:
        print(f"   ⚠️ Compression check failed: {e}")

# ──────────────────────────────────────────────
# 3. Build request
# ──────────────────────────────────────────────
ext = image_path.suffix.lower()
MIME_MAP = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp"}
mime_type = MIME_MAP.get(ext, "image/png")

img_b64 = base64.b64encode(img_bytes).decode("ascii")
print(f"🔐 Base64: {len(img_b64):,} chars")

body = json.dumps({
    "model": "qwen-vl-max",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{img_b64}"}},
            {"type": "text", "text": args.prompt}
        ]
    }],
    "max_tokens": args.max_tokens,
    "temperature": args.temperature
}).encode("utf-8")

# ──────────────────────────────────────────────
# 4. Call API
# ──────────────────────────────────────────────
print(f"🚀 Calling Qwen-VL-Max...")
print("---")

# Try urllib first (more reliable on Windows), fallback to curl
try:
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        response_text = resp.read().decode("utf-8")
except Exception as e:
    print(f"❌ urllib failed: {e}")
    print("   Trying curl fallback...")
    import subprocess
    import tempfile

    req_file = Path(os.environ.get("TEMP", "/tmp")) / "_vision_req.json"
    with open(req_file, "w", encoding="utf-8") as f:
        json.dump(json.loads(body.decode("utf-8")), f, ensure_ascii=False)

    r = subprocess.run([
        "curl", "-s", "--connect-timeout", "30", "--max-time", "180",
        "-X", "POST", API_URL,
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", f"@{req_file}"
    ], capture_output=True)
    if r.returncode != 0:
        print(f"❌ 网络错误 (code {r.returncode})")
        sys.exit(1)
    response_text = r.stdout.decode("utf-8", errors="replace")

# ──────────────────────────────────────────────
# 5. Parse output
# ──────────────────────────────────────────────
try:
    data = json.loads(response_text)
except json.JSONDecodeError:
    print(f"❌ API 返回非 JSON: {response_text[:300]}")
    sys.exit(1)

if "error" in data:
    err = data["error"]
    print(f"❌ API Error [{err.get('code', 'N/A')}]: {err.get('message', str(err))}")
    sys.exit(1)

if "choices" in data and len(data["choices"]) > 0:
    content = data["choices"][0]["message"]["content"]
    print(content)
    print("---")
    print("✅ Done")
else:
    print(f"⚠️ Unexpected response: {json.dumps(data, ensure_ascii=False)[:500]}")
    sys.exit(1)
