#!/bin/bash

SCRIPT_PATH="${SWIFTBAR_PLUGIN_PATH:-$0}"
ICON_DIR="$(dirname "$SCRIPT_PATH")/../assets"
STATE_FILE="$(dirname "$SCRIPT_PATH")/.caffeinete_state"

img_b64() { base64 < "$1" 2>/dev/null | tr -d '\n'; }

toggle() {
    read -r TIER DEADLINE < "$STATE_FILE" 2>/dev/null || { TIER=0; DEADLINE=0; }
    NOW=$(date +%s)

    if [ "$DEADLINE" -gt "$NOW" ] && pgrep -x caffeinate >/dev/null 2>&1; then
        case "$TIER" in
            40) NEXT=0 ;;
            30) NEXT=40 ;;
            20) NEXT=30 ;;
            10) NEXT=20 ;;
            *)  NEXT=10 ;;
        esac
    else
        echo "0 0" > "$STATE_FILE"
        killall caffeinate >/dev/null 2>&1
        NEXT=10
    fi

    killall caffeinate >/dev/null 2>&1

    if [ "$NEXT" -gt 0 ]; then
        caffeinate -d -u -t $((NEXT * 60)) >/dev/null 2>&1 &
        echo "$NEXT $(($(date +%s) + NEXT * 60))" > "$STATE_FILE"
    else
        echo "0 0" > "$STATE_FILE"
    fi

    exit 0
}

if [ "$1" = "toggle" ]; then
    toggle
fi

NOW=$(date +%s)
read -r TIER DEADLINE < "$STATE_FILE" 2>/dev/null || { TIER=0; DEADLINE=0; }

if [ "$DEADLINE" -gt "$NOW" ] && pgrep -x caffeinate >/dev/null 2>&1; then
    ICON="$ICON_DIR/caffeinete_icon-${TIER}m.png"
else
    ICON="$ICON_DIR/caffeinete_icon-off.png"
fi

IMAGE_B64=$(img_b64 "$ICON")
echo "| image=$IMAGE_B64 templateImage=true bash=$0 param1=toggle terminal=false refresh=true"