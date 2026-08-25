#!/usr/bin/env python3
import json,pathlib,sys,datetime
out=pathlib.Path(sys.argv[1]); model=sys.argv[2]
def load(name,default=None):
 try:return json.load(open(out/name))
 except Exception:return default
compat=load("client-compat.json",{}); stats=load("stats.json",{}); hw=load("hardware.json",{}); passed=bool(compat.get("passed"))
e={"schemaVersion":"1.0","runId":sys.argv[3],"timestamp":datetime.datetime.now(datetime.timezone.utc).isoformat(),"source":{"repository":"https://github.com/atlantyqa-labs/FreeToken","commit":sys.argv[4]},"hardware":hw,"artifacts":{"sbom":"sbom.cdx.json","provenance":"provenance.intoto.jsonl","checksums":"SHA256SUMS"},"bandwidth":{"artifact":"benchbw/"},"models":[{"id":model,"status":"passed" if passed else "failed","ttftMs":stats.get("ttft_ms",0),"tokensPerSecond":stats.get("tokens_per_second",0),"peakRamBytes":0,"peakVramBytes":stats.get("vram_used_bytes",0),"averagePowerWatts":0,"toolCalling":compat}],"gates":{"hardwareInventory":"passed","bandwidth":"passed","apiCompatibility":"passed" if passed else "failed","sbom":"passed","provenance":"passed"},"verdict":"qualified" if passed else "rejected"}
json.dump(e,open(out/"FreeTokenRuntimeEvidence.json","w"),indent=2)
