#!/usr/bin/env bash
# Usage: check.sh file.drawio [...]  -> validate.py --score + draft PNG (no -e) in ../_previews/
# Note: --disable-dev-shm-usage needed (64 MB /dev/shm crashes the renderer on big pages).
SK=/opt/data/profiles/blueprint/skills/drawio-skill/scripts
DRAWIO=/opt/data/profiles/blueprint/tools/squashfs-root/drawio
PREV=/opt/data/uml/marketplace-produits-locaux-maroc/_previews
mkdir -p "$PREV"
for f in "$@"; do
  b=$(basename "$f" .drawio)
  echo "=== $b"
  python3 "$SK/validate.py" "$f" --score
  echo "validate_exit=$?"
  if [ -z "$NOPNG" ]; then
    rm -f "$PREV/$b.png"
    timeout 60 xvfb-run -a "$DRAWIO" -x -f png -o "$PREV/$b.png" "$f" --disable-gpu --no-sandbox --disable-dev-shm-usage 2>&1 | grep -iv dbus | grep -i "error\|crash"
    ls -la "$PREV/$b.png" 2>/dev/null | awk '{print "png", $5, $NF}'
  fi
done
