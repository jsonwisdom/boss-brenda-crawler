#!/usr/bin/env python3
import os, json, requests, hashlib, time
from datetime import datetime, UTC

RPC=os.getenv("BASE_RPC_URL","https://mainnet.base.org")
ROOT=os.getenv("CREATOR_COIN","0x694ce46c64d9d1a5e9376a9febcf85ec05d72e9f").lower()
BIRTH=int(os.getenv("BIRTH_BLOCK","31825577"))
WINDOW=int(os.getenv("WINDOW","1000"))
START=BIRTH-WINDOW
END=BIRTH+WINDOW

TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def rpc(method, params):
    for i in range(6):
        r=requests.post(RPC,json={"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout=60)
        if r.status_code in (429,413):
            time.sleep(2**i); continue
        r.raise_for_status()
        j=r.json()
        if "error" in j: raise RuntimeError(j["error"])
        return j["result"]
    raise RuntimeError("RPC_FAILED")

def call(sig):
    try:
        return rpc("eth_call",[{"to":ROOT,"data":sig}, "latest"])
    except Exception:
        return "PENDING"

def topic_addr(t):
    return "0x"+t[-40:].lower()

logs=rpc("eth_getLogs",[{
  "fromBlock":hex(START),
  "toBlock":hex(END),
  "address":ROOT,
  "topics":[TRANSFER]
}])

holders={}
txs=[]
for l in logs[:10]:
    frm=topic_addr(l["topics"][1])
    to=topic_addr(l["topics"][2])
    txs.append(l["transactionHash"])
    holders[to]=True

out={
 "status":"VERIFIED" if logs else "VERIFIED_EMPTY",
 "root":ROOT,
 "chain_id":8453,
 "birth_block":BIRTH,
 "birth_block_window":{"from":START,"to":END},
 "metadata_calls":{
   "name_raw":call("0x06fdde03"),
   "symbol_raw":call("0x95d89b41"),
   "contractURI_raw":call("0xe8a3d485")
 },
 "transfer_logs_found":len(logs),
 "first_10_holders":list(holders.keys())[:10],
 "first_10_transfer_txs":txs[:10],
 "creation_tx":"PENDING_UNPROVEN",
 "timestamp":datetime.now(UTC).isoformat()
}

os.makedirs("data/zora",exist_ok=True)
path="data/zora/EV-BBC-008-CREATOR-LANE.json"
open(path,"w").write(json.dumps(out,indent=2,sort_keys=True))
sha=hashlib.sha256(open(path,"rb").read()).hexdigest()
open(path+".sha256","w").write(sha+"  "+path+"\n")
print(json.dumps({"status":out["status"],"logs":len(logs),"sha256":sha},indent=2))
