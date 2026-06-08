#!/usr/bin/env python3
"""
🗜️ Smart Compress — Shrink images for efficient API transfer.
Part of the Image Vision skill for Claude Code.

Attempts to use PIL (Pillow) if available, otherwise falls back to
basic binary compression or passes through as-is.

Usage:
    python3 smart_compress.py <input_path> [--max-kb 500] [--max-width 1200]
    # Output: compressed path printed to stdout
"""
import os
import sys
import struct
from pathlib import Path

# ──────────────────────────────────────────────
# 0. Args
# ──────────────────────────────────────────────
import argparse
parser = argparse.ArgumentParser(description="Smart Image Compressor")
parser.add_argument("input", help="Input image path")
parser.add_argument("--max-kb", type=int, default=500, help="Max output size in KB")
parser.add_argument("--max-width", type=int, default=1200, help="Max width in pixels")
parser.add_argument("--quality", type=int, default=70, help="JPEG quality (1-100)")
args = parser.parse_args()

input_path = Path(args.input)
if not input_path.exists():
    print(f"❌ File not found: {input_path}")
    sys.exit(1)

orig_size = input_path.stat().st_size
max_bytes = args.max_kb * 1024

# ──────────────────────────────────────────────
# 1. Check if compression needed
# ──────────────────────────────────────────────
if orig_size <= max_bytes:
    print(f"✅ Already under {args.max_kb}KB ({orig_size:,} bytes)")
    print(input_path)
    sys.exit(0)

print(f"📦 {orig_size:,} bytes → target <{args.max_kb}KB")

# ──────────────────────────────────────────────
# 2. Try PIL compression
# ──────────────────────────────────────────────
try:
    from PIL import Image
    img = Image.open(input_path)

    # Resize if needed
    w, h = img.size
    if w > args.max_width:
        ratio = args.max_width / w
        nh = int(h * ratio)
        img = img.resize((args.max_width, nh), Image.LANCZOS)
        print(f"🔍 Resized: {w}x{h} → {args.max_width}x{nh}")

    # Convert to RGB if needed (for JPEG)
    ext = input_path.suffix.lower()
    if ext in (".png", ".bmp", ".gif", ".webp"):
        if img.mode in ("RGBA", "P", "LA"):
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = rgb_img
        else:
            img = img.convert("RGB")

    output_path = input_path.parent / f"{input_path.stem}_compressed.jpg"
    img.save(output_path, "JPEG", quality=args.quality, optimize=True)

    new_size = output_path.stat().st_size
    ratio = (1 - new_size / orig_size) * 100
    print(f"🗜️ Compressed: {orig_size:,} → {new_size:,} bytes ({ratio:.0f}% smaller)")
    print(output_path)

except ImportError:
    # ──────────────────────────────────────────────
    # 3. Fallback: pass through
    # ──────────────────────────────────────────────
    print("⚠️ PIL not available, sending original (install Pillow for compression)")
    print(input_path)
except Exception as e:
    print(f"⚠️ Compression error: {e}, sending original")
    print(input_path)
