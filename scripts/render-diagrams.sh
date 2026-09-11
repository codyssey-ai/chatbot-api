#!/usr/bin/env bash
# docs/architecture.md 의 mermaid 블록을 추출해 PNG 로 렌더링한다.
# 요구 사항: Node.js, Chrome
set -euo pipefail

cd "$(dirname "$0")/.."

SRC="docs/architecture.md"
MMD_DIR="docs/diagrams"
IMG_DIR="docs/images"

mkdir -p "$MMD_DIR" "$IMG_DIR"

echo "[1/2] mermaid 블록 추출"
python3 - "$SRC" "$MMD_DIR" <<'PY'
import re, sys, pathlib

src, out_dir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
names = ["01-deployment", "02-pipeline", "03-request-flow", "04-erd"]
blocks = re.findall(r"```mermaid\n(.*?)```", src.read_text(encoding="utf-8"), re.S)

if len(blocks) != len(names):
    sys.exit(f"블록 수가 맞지 않습니다: {len(blocks)}개 발견, {len(names)}개 기대. "
             "다이어그램을 추가했다면 이 스크립트의 names 목록도 갱신하세요.")

for name, body in zip(names, blocks):
    (out_dir / f"{name}.mmd").write_text(body.rstrip() + "\n", encoding="utf-8")
    print(f"  {out_dir / f'{name}.mmd'}")
PY

echo "[2/2] PNG 렌더링"
CFG="$(mktemp)"
echo '{ "args": ["--no-sandbox", "--font-render-hinting=none"] }' > "$CFG"
trap 'rm -f "$CFG"' EXIT

for f in "$MMD_DIR"/*.mmd; do
  name="$(basename "$f" .mmd)"
  npx -y @mermaid-js/mermaid-cli@latest \
    -i "$f" -o "$IMG_DIR/$name.png" \
    -b white -s 3 -p "$CFG" >/dev/null
  echo "  $IMG_DIR/$name.png"
done

echo "완료"
