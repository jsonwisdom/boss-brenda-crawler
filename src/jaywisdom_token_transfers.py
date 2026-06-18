#!/usr/bin/env python3
import os, json, requests
from datetime import datetime, UTC

RPC=os.getenv("BASE_RPC_URL","https://mainnet.base.org")
TOKEN=os.getenv("JAYWISDOM_TOKEN","0x84dc68b4354be610c44fe63dcadbf56847f7476b").lower()
WALLET=os.getenv("TARGET_WALLET","0x829adfedbe565f9885a7ea6bc78912acaef055e2").lower()
START=int(os.getenv("START_BLOCK","25000000"))
END=int(os.getenv("END_BLOCK","28520000"))
CHUNK=int(os.getenv("CHUNK_SIZE","5000"))

TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
PAD="0x"+"0"*24+WALLET[2:]

def rpc(method, params):
    r=requests.post(RPC,json={"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout=60)
    r.raise_for_status()
    return r.json()["result"]

def scan(topic_index):
    out=[]
    b=START
    while b<=END:
        e=min(b+CHUNK,END)
        topics=[TRANSFER,None,None]
        topics[topic_index]=PAD
        try:
            logs=rpc("eth_getLogs",[{
                "fromBlock":hex(b),
                "toBlock":hex(e),
                "address":TOKEN,
                "topics":topics
            }])
            out.extend(logs)
            print(b,e,len(logs),len(out))
            b=e+1
        except Exception as ex:
            print("RPC_ERROR", b, e, ex)
            if e == b:
                b += 1
            else:
                globals()["CHUNK"] = max(100, CHUNK//2)
                print("REDUCE_CHUNK_TO", CHUNK)
    return out

sent=scan(1)
received=scan(2)

entries=sent+received
out={
 "status":"TOKEN_TRANSFER_SCAN_COMPLETED",
 "token":TOKEN,
 "wallet":WALLET,
 "range":{"from":START,"to":END},
 "sent_count":len(sent),
 "received_count":len(received),
 "entries_count":len(entries),
 "timestamp":datetime.now(UTC).isoformat(),
 "entries":entries[:1000]
}

os.makedirs("evidence",exist_ok=True)
open("evidence/EV-BBC-003A-JAYWISDOM-TOKEN-TRANSFERS.json","w").write(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!="entries"},indent=2))
