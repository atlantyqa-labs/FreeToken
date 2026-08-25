#!/usr/bin/env python3
import argparse,json,subprocess,time,signal
p=argparse.ArgumentParser(); p.add_argument("--pid",type=int,required=True); p.add_argument("--gpu",required=True); p.add_argument("--out",required=True); p.add_argument("--interval",type=float,default=.25); a=p.parse_args()
running=True
def stop(*_): 
 global running; running=False
signal.signal(signal.SIGTERM,stop); signal.signal(signal.SIGINT,stop)
samples=[]
def sh(args):
 try:return subprocess.check_output(args,text=True,stderr=subprocess.DEVNULL).strip()
 except Exception:return ""
while running:
 rss=sh(["ps","-o","rss=","--ppid",str(a.pid),"-p",str(a.pid)])
 rss_bytes=sum(int(x) for x in rss.split() if x.isdigit())*1024
 raw=sh(["nvidia-smi","--id",a.gpu,"--query-gpu=memory.used,power.draw,pcie.link.gen.current,pcie.link.width.current,utilization.gpu","--format=csv,noheader,nounits"])
 vals=[x.strip() for x in raw.split(",")]
 sample={"timestamp":time.time(),"rssBytes":rss_bytes}
 if len(vals)==5:
  for k,v,scale in zip(["vramBytes","powerWatts","pcieGeneration","pcieWidth","gpuUtilizationPercent"],vals,[1048576,1,1,1,1]):
   try:sample[k]=float(v)*scale
   except ValueError:sample[k]=None
 samples.append(sample); time.sleep(a.interval)
valid_power=[x["powerWatts"] for x in samples if x.get("powerWatts") is not None]
summary={"sampleCount":len(samples),"peakRamBytes":max([x["rssBytes"] for x in samples] or [0]),"peakVramBytes":max([x.get("vramBytes") or 0 for x in samples] or [0]),"averagePowerWatts":sum(valid_power)/len(valid_power) if valid_power else None,"peakPowerWatts":max(valid_power) if valid_power else None,"samples":samples}
json.dump(summary,open(a.out,"w"),indent=2)
