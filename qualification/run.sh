#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
ROOT="$(git rev-parse --show-toplevel)"
OUT="${OUT_DIR:-$ROOT/qualification/out}"; MODEL="${MODEL:-}"; GPU="${GPU:-0}"
mkdir -p "$OUT"; SHA="$(git rev-parse HEAD)"; RUN_ID="${GITHUB_RUN_ID:-local}-$(date -u +%Y%m%dT%H%M%SZ)"
exec > >(tee "$OUT/run.log") 2>&1
[[ "$SHA" == "2757bb5f91156fc8a44d88ec4b302a81f10c9e81" || -n "${ALLOW_QUALIFICATION_COMMITS:-}" ]] || { echo "Unexpected source SHA: $SHA"; exit 2; }
command -v nvidia-smi >/dev/null || { echo "NVIDIA runtime required"; exit 3; }; command -v ft >/dev/null || { echo "FreeToken CLI required"; exit 3; }
python3 "$ROOT/qualification/hardware.py" "$OUT/hardware.json"; ft --version | tee "$OUT/freetoken-version.txt"; ft bench bw --gpu "$GPU" | tee "$OUT/bench-bw.log"; cp -a "$HOME/.cache/freetoken/benchbw" "$OUT/" 2>/dev/null || true
[[ -n "$MODEL" ]] || { echo "MODEL is required"; exit 4; }
ft serve --model "$MODEL" --gpu "$GPU" --host 127.0.0.1 --port 1919 >"$OUT/server.log" 2>&1 & SERVER_PID=$!; trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
for _ in $(seq 1 180); do curl -fsS http://127.0.0.1:1919/health >"$OUT/health.json" && break; sleep 2; done
curl -fsS http://127.0.0.1:1919/health >/dev/null; python3 "$ROOT/qualification/client_compat.py" --model "$MODEL" --out "$OUT/client-compat.json"; curl -fsS http://127.0.0.1:1919/v1/stats >"$OUT/stats.json"
python3 "$ROOT/qualification/assemble_evidence.py" "$OUT" "$MODEL" "$RUN_ID" "$SHA"; sha256sum "$OUT"/* >"$OUT/SHA256SUMS"
