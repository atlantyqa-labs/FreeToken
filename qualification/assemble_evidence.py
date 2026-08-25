#!/usr/bin/env python3
import json,pathlib,sys,datetime
out=pathlib.Path(sys.argv[1]); model=sys.argv[2]
def load(name,default=None):
 try:return json.load(open(out/name))
 except Exception:return default
compat=load("client-compat.json",{}); stats=load("stats.json",{}); hw=load("hardware.json",{}); metrics=load("runtime-metrics.json",{}); passed=bool(compat.get("passed"))
latencies=[x.get("latencyMs",0) for x in compat.get("cases",{}).values()]
e={"schemaVersion":"1.0","runId":sys.argv[3],"timestamp":datetime.datetime.now(datetime.timezone.utc).isoformat(),"source":{"repository":"https://github.com/atlantyqa-labs/FreeToken","commit":sys.argv[4]},"hardware":hw,"artifacts":{"sbom":"sbom.cdx.json","provenance":"provenance.intoto.jsonl","checksums":"SHA256SUMS"},"bandwidth":{"artifact":"benchbw/"},"models":[{"id":model,"status":"passed" if passed else "failed","ttftMs":stats.get("ttft_ms",min(latencies) if latencies else 0),"tokensPerSecond":stats.get("tokens_per_second",stats.get("decode_tokens_per_second",0)),"peakRamBytes":int(metrics.get("peakRamBytes",0)),"peakVramBytes":int(metrics.get("peakVramBytes",0)),"averagePowerWatts":metrics.get("averagePowerWatts") or 0,"pcie":{"generation":next((x.get("pcieGeneration") for x in reversed(metrics.get("samples",[])) if x.get("pcieGeneration") is not None),None),"width":next((x.get("pcieWidth") for x in reversed(metrics.get("samples",[])) if x.get("pcieWidth") is not None),None)},"toolCalling":compat}],"gates":{"hardwareInventory":"passed","bandwidth":"passed","apiCompatibility":"passed" if passed else "failed","runtimeMetrics":"passed" if metrics.get("sampleCount",0)>0 else "failed","sbom":"passed","provenance":"passed"},"verdict":"qualified" if passed and metrics.get("sampleCount",0)>0 else "rejected"}
json.dump(e,open(out/"FreeTokenRuntimeEvidence.json","w"),indent=2)
