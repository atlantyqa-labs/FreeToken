#!/usr/bin/env python3
import json,os,platform,subprocess,sys
def cmd(args):
 try:return subprocess.check_output(args,text=True,stderr=subprocess.DEVNULL).strip()
 except Exception:return ""
gpus=[]; raw=cmd(["nvidia-smi","--query-gpu=index,uuid,name,memory.total,driver_version,pci.bus_id,power.limit","--format=csv,noheader,nounits"])
for line in raw.splitlines():
 p=[x.strip() for x in line.split(",")]
 if len(p)>=7:gpus.append(dict(zip(["index","uuid","name","memoryMiB","driver","pciBusId","powerLimitWatts"],p)))
try:ram=os.sysconf("SC_PAGE_SIZE")*os.sysconf("SC_PHYS_PAGES")
except Exception:ram=0
json.dump({"os":platform.platform(),"kernel":platform.release(),"cpu":platform.processor() or cmd(["lscpu"]),"ramBytes":ram,"gpus":gpus,"pcie":cmd(["lspci","-nn"])},open(sys.argv[1],"w"),indent=2)
