#!/usr/bin/env python3
import os, json, requests, hashlib, time
from datetime import datetime, UTC

RPC=os.getenv("BASE_RPC_URL","https://mainnet.base.org")
WALLET=os.getenv("TARGET_WALLET","0x829adfedbe565f9885a7ea6bc78912acaef055e2").lower()
START=int(os.getenv("START_BLOCK","28500000"))
END=int(os.getenv("END_BLOCK","28520000"))
CHUNK=int(os.getenv("CHUNK_SIZE","2000"))

SEEDS=[
 "0xfc33d0c818d95dcfb49374a9cfd4ef956e9ec0f4",
 "0x694ce46c64d9d1a5e9376a9febcf85ec05d72e9f"
]
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
PAD="0x"+"0"*24+WALLET[2:]

def rpc(method, params):
    for attempt in range(6):
        r=requests.post(RPC,json={"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout=60)
        if r.status_code == 429:
            wait = 2 ** attempt
            print("RATE_LIMIT_WAIT", wait)
            time.sleep(wait)
            continue
        r.raise_for_status()
        j=r.json()
        if "error" in j:
            raise RuntimeError(j["error"])
        return j["result"]
    raise RuntimeError("RPC_RATE_LIMIT_EXCEEDED")

graph={}
def add(log, rel):
    c=log["address"].lower()
    if c not in graph:
        graph[c]={
            "contract": c,
            "relationship": rel,
            "first_seen_tx": log["transactionHash"],
            "first_seen_block": int(log["blockNumber"],16)
        }

for contract in SEEDS:
    for idx, rel in [(1,"wallet_transfer_from"),(2,"wallet_transfer_to")]:
        b=START
        while b<=END:
            e=min(b+CHUNK,END)
            logs=rpc("eth_getLogs",[{
                "fromBlock":hex(b),
                "toBlock":hex(e),
                "address":contract,
                "topics":[TRANSFER, PAD if idx==1 else None, PAD if idx==2 else None]
            }])
            for log in logs: add(log, rel)
            print(contract, rel, b, e, len(logs))
            b=e+1

out={
 "wallet":WALLET,
 "known_seeds":SEEDS,
 "contracts_found":len(graph),
 "scan_range":{"from":START,"to":END},
 "scan_timestamp":datetime.now(UTC).isoformat(),
 "status":"GRAPH_DISCOVERY_SEED",
 "graph":list(graph.values())
}

os.makedirs("data/zora",exist_ok=True)
path="data/zora/jay-contract-graph.json"
open(path,"w").write(json.dumps(out,indent=2,sort_keys=True))
sha=hashlib.sha256(open(path,"rb").read()).hexdigest()
open(path+".sha256","w").write(sha+"  "+path+"\n")
print(json.dumps({"contracts_found":out["contracts_found"],"sha256":sha},indent=2))
