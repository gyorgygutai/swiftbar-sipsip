# SwiftBar

My SwiftBar menu bar plugin — caffeinate timer.

## Structure

- `.`, `sipsip.30s.sh` — SwiftBar plugin at repo root. Executable; SwiftBar auto-runs it.
- `assets/` — icon files (`sipsip_icon-{active,inactive}.png`) and raw artwork (`sipsip_raw.png`). Scripts locate this via `readlink -f` resolving the symlink to real path, then `assets/` as sibling.
- `tools/make_swiftbar_icon.sh` — regenerates menu bar icons from artwork raws.
- `tools/make_demo_gif.py` — renders `assets/sipsip_demo.gif`, a square animated demo of the icon click cycle (off → 10 → 20 → 30 → 40m, with press pulses). Re-run after changing any `sipsip_icon-*.png`.

## Plugins

- `sipsip.30s.sh` — caffeinate toggle with 10/20/30/40m timers. `.30s` = 30s refresh interval suffix.

Plugin conventions:
- Refresh interval in filename suffix: `.30s.sh`, `.1m.sh`.
- Menu actions: `bash=$0 param1=... terminal=false refresh=true`.
- Icons live in `assets/` — script resolves them via `readlink -f` to real path then `assets/`. Emoji fallback if icon missing.
- SwiftBar shows any non-hidden non-executable file in the bar — keep support files as dotfiles.

## Menu bar icons

Full pipeline is `tools/make_swiftbar_icon.sh <raw.png> <name>` → writes `sipsip_<name>_icon-<name>.png` beside the raw.

- **Source**: black glyph on white PNG (Flux raws fine). Flux produces near-white (254) backgrounds — always trim with `-fuzz 2%`.
- **Framing (Apple HIG)**: working area for menu bar extras is 22pt; glyph should be ~16pt to match system icon weight. At 144 DPI that's a 32px glyph centered on a 44px canvas.
- **Rules that were learned the hard way**:
  - NEVER `-negate` after alpha exists — it flips the alpha channel → white shapes / inverted transparency.
  - 44px at default 72 DPI renders DOUBLE size in the bar → density MUST be 144.
  - Active + inactive BOTH render as `templateImage=` (macOS auto-tints white in dark / black in light). Inactive is dimmed alpha-only: `-channel A -evaluate multiply 0.65 +channel`. No gray colorize, no `image=` for the bar.
- **Verify every output**: 44x44 px, 144 DPI, `hasAlpha yes`, corner alpha=0, glyph alpha=1. The script checks all of these and exits non-zero on failure.

## Rebuilding

```bash
tools/make_swiftbar_icon.sh assets/.sipsip_raw.png sipsip
open -g "swiftbar://refreshall"
```
