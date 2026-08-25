# Qualification Wave 0

This qualifies the unmodified upstream runtime pinned in `upstream.lock.json` and separates governance checks from hardware claims.

## Gates

1. Static CI validates the frozen SHA, schema, syntax, Apache-2.0 license and CycloneDX SBOM.
2. A trusted NVIDIA self-hosted runner executes the manual GPU workflow.
3. Run each model separately: `Qwen/Qwen3.6-35B-A3B`, `openai/gpt-oss-20b`, and `openai/gpt-oss-120b` only when RAM/VRAM/storage permit.
4. Evidence uploads even on failure. A skipped model must carry an explicit hardware reason; it is never reported as passed.
5. Promotion requires successful OpenAI Chat, OpenAI Responses and Anthropic Messages tool calls.

Runner labels: `self-hosted, linux, x64, gpu, freetoken-qualification`. Prerequisites: Linux x86_64, NVIDIA/CUDA 13-compatible container runtime, Python 3.10+, Docker, `uv`, `syft`, `cosign`, `jq` and `curl`.

Dispatch **Qualification Wave 0 GPU** with the model and GPU UUID/index. It builds an isolated OCI image, generates SBOM/provenance, runs `ft bench bw`, captures telemetry, validates tool calling and emits `FreeTokenRuntimeEvidence.json`. Missing power/PCIe counters block production promotion in human review; synthetic values are forbidden.
