#!/bin/sh
# Renders the link-preview card and the home-screen icon from their HTML templates with headless Chrome.
# Run from the repo root: sh tools/render-images.sh
set -e
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
render() { # template output width height
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --virtual-time-budget=6000 --window-size="$3,$4" --screenshot="$2" "file://$PWD/$1" 2>/dev/null
}
render tools/og.html og.png 1200 630
render tools/icon.html apple-touch-icon.png 180 180
ls -l og.png apple-touch-icon.png
