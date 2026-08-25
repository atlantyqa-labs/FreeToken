#!/usr/bin/env python3
"""Protocol and tool-calling qualification against a running FreeToken server."""
import argparse,json,time,urllib.request
def request(url,payload=None,headers=None):
 data=None if payload is None else json.dumps(payload).encode(); req=urllib.request.Request(url,data=data,headers=headers or {"Content-Type":"application/json"}); start=time.perf_counter()
 with urllib.request.urlopen(req,timeout=300) as r: body=json.load(r)
 return body,(time.perf_counter()-start)*1000
def main():
 p=argparse.ArgumentParser(); p.add_argument("--base-url",default="http://127.0.0.1:1919"); p.add_argument("--model",required=True); p.add_argument("--out",required=True); a=p.parse_args()
 tool={"type":"function","function":{"name":"add","description":"Add two integers","parameters":{"type":"object","properties":{"a":{"type":"integer"},"b":{"type":"integer"}},"required":["a","b"]}}}; cases={}
 body,ms=request(a.base_url+"/v1/chat/completions",{"model":a.model,"messages":[{"role":"user","content":"Use add with a=19 and b=23."}],"tools":[tool],"tool_choice":"required","max_tokens":128}); calls=body.get("choices",[{}])[0].get("message",{}).get("tool_calls",[]); cases["openaiChat"]={"passed":bool(calls),"latencyMs":ms,"response":body}
 body,ms=request(a.base_url+"/v1/responses",{"model":a.model,"input":"Use add with a=19 and b=23.","tools":[tool],"tool_choice":"required","max_output_tokens":128}); cases["openaiResponses"]={"passed":any(x.get("type")=="function_call" for x in body.get("output",[])),"latencyMs":ms,"response":body}
 anth_tool={"name":"add","description":"Add two integers","input_schema":tool["function"]["parameters"]}; body,ms=request(a.base_url+"/v1/messages",{"model":a.model,"max_tokens":128,"messages":[{"role":"user","content":"Use add with a=19 and b=23."}],"tools":[anth_tool],"tool_choice":{"type":"tool","name":"add"}},{"Content-Type":"application/json","anthropic-version":"2023-06-01","x-api-key":"local"}); cases["anthropicMessages"]={"passed":any(x.get("type")=="tool_use" for x in body.get("content",[])),"latencyMs":ms,"response":body}
 with open(a.out,"w") as f: json.dump({"passed":all(x["passed"] for x in cases.values()),"cases":cases},f,indent=2)
 if not all(x["passed"] for x in cases.values()): raise SystemExit(1)
if __name__=="__main__": main()
