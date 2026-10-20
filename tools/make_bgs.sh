#!/bin/bash
# Convert generated photos img/bg_src/<id>.(jpg|png) → img/bg/<id>.webp (≤ ~180 KB, 900px wide) and list them in js/config.js
set -euo pipefail; cd "$(dirname "$0")/.."; mkdir -p img/bg
ids=()
for f in img/bg_src/*.{jpg,jpeg,png}; do [ -e "$f" ] || continue; id=$(basename "${f%.*}"); id=${id#bg_}
  python3 - "$f" "img/bg/$id.webp" <<'PY'
import sys; from PIL import Image
im = Image.open(sys.argv[1]).convert('RGB'); w = 900; im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
q = 80
while True:
    im.save(sys.argv[2], 'WEBP', quality=q, method=6)
    import os
    if os.path.getsize(sys.argv[2]) <= 190_000 or q <= 45: break
    q -= 7
PY
  ids+=("'$id'"); done
list=$(IFS=,; echo "${ids[*]}")
sed -i "s/  photos: \[[^]]*\] };/  photos: [$list] };/" js/config.js
ls -la img/bg; grep photos js/config.js
