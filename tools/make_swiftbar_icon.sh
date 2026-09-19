#!/bin/bash
set -euo pipefail

RAW=$1
NAME=$2
DIR=$(dirname "$RAW")
OUT="$DIR/sipsip_${NAME}_icon-${NAME}.png"

magick "$RAW" -fuzz 2% -trim +repage -resize 32x32 -colorspace gray \
  -alpha set -channel A -fx "(1-r)" \
  -gravity center -background none -extent 44x44 \
  "$OUT"

sips -s dpiWidth 144 -s dpiHeight 144 "$OUT" 2>/dev/null

chmod -x "$OUT"

sips -g pixelWidth -g pixelHeight -g dpiWidth -g hasAlpha "$OUT" 2>/dev/null | grep -q "pixelWidth: 44" || { echo "FAIL: not 44px wide"; exit 1; }
sips -g pixelWidth -g pixelHeight -g dpiWidth -g hasAlpha "$OUT" 2>/dev/null | grep -q "dpiWidth: 144" || { echo "FAIL: not 144 DPI"; exit 1; }
sips -g pixelWidth -g pixelHeight -g dpiWidth -g hasAlpha "$OUT" 2>/dev/null | grep -q "hasAlpha: yes" || { echo "FAIL: no alpha"; exit 1; }
[ "$(magick "$OUT" -format "%[fx:int(minima.a*1000)]" info: 2>/dev/null)" = "0" ] || { echo "FAIL: corner not transparent"; exit 1; }
echo "OK $OUT"