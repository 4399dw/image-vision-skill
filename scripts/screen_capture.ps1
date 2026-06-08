<#
.SYNOPSIS
    🔮 Image Vision — Screen Capture + Qwen-VL Analysis
    Part of the Image Vision skill for Claude Code.
.DESCRIPTION
    Captures the primary monitor, auto-compresses if >1MB, then calls
    the vision_api.py script to analyze the screenshot.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File screen_capture.ps1
    powershell -ExecutionPolicy Bypass -File screen_capture.ps1 -Prompt "Describe this UI"
#>
param(
    [string]$Prompt = "Describe this screenshot in detail. Include all visible windows, text, code, UI elements, layout, and any content being played or displayed."
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# ──────────────────────────────────────────────
# 1. Capture Screen
# ──────────────────────────────────────────────
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bounds.Size)
$g.Dispose()

$output = "$env:TEMP\_screenshot.png"
$bmp.Save($output, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

$size = (Get-Item $output).Length
Write-Host "📷 Screen: $($bounds.Width)x$($bounds.Height) — $($size) bytes"

# ──────────────────────────────────────────────
# 2. Compress if > 1MB
# ──────────────────────────────────────────────
if ($size -gt 1048576) {
    Write-Host "⚡ Compressing screenshot..."
    $img = [System.Drawing.Image]::FromFile($output)
    $ratio = [Math]::Sqrt(1048576.0 / $size)
    $nw = [int]($img.Width * $ratio)
    $nh = [int]($img.Height * $ratio)

    $small = New-Object System.Drawing.Bitmap($nw, $nh)
    $g2 = [System.Drawing.Graphics]::FromImage($small)
    $g2.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g2.DrawImage($img, 0, 0, $nw, $nh)
    $img.Dispose(); $g2.Dispose()

    $compressed = "$env:TEMP\_screenshot_compressed.jpg"
    $codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() |
             Where-Object { $_.MimeType -eq 'image/jpeg' }
    $params = New-Object System.Drawing.Imaging.EncoderParameters(1)
    $params.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter(
        [System.Drawing.Imaging.Encoder]::Quality, 70L)
    $small.Save($compressed, $codec, $params)
    $small.Dispose()

    $compSize = (Get-Item $compressed).Length
    Write-Host "   $($nw)x$($nh) JPEG — $($compSize) bytes"
    $output = $compressed
}

# ──────────────────────────────────────────────
# 3. Call Vision API
# ──────────────────────────────────────────────
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$visionScript = Join-Path $scriptDir "vision_api.py"

if (-not (Test-Path $visionScript)) {
    Write-Host "❌ vision_api.py not found at: $visionScript"
    exit 1
}

$env:PYTHONIOENCODING = 'utf-8'
python3 $visionScript --image $output --prompt $Prompt

Write-Host ""
Write-Host "✅ Screen capture + analysis complete"
