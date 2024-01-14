import requests
import json
import os
from tqdm import tqdm
from requests.auth import HTTPBasicAuth
import time

sample_node_a = {
    "name": "sample_node_a",
    "endpoint": "http://your_cp_api_endpoint:with_port",
    "user": "rpc",
    "password": "rpc"
}

sample_node_b = {
    "name": "sample_node_b",
    "endpoint": "http://your_cp_api_endpoint:with_port",
    "user": "rpc",
    "password": "rpc"
}




def create_payload(method, params):
    base_payload = {
        "method": method,
        "params": params,
        "jsonrpc": "2.0",
        "id": 0
    }
    return base_payload


def get_block(node_info, params={}):
    auth = HTTPBasicAuth(node_info["user"], node_info["password"])
    payload = create_payload(
        "get_blocks",
        params
    )
    headers = {'content-type': 'application/json'}
    response = requests.post(
        node_info["endpoint"],
        data=json.dumps(payload),
        headers=headers,
        auth=auth
    )
    return json.loads(response.text)["result"]


def get_block_count(node_info):
    auth = HTTPBasicAuth(node_info["user"], node_info["password"])
    payload = create_payload("get_running_info", {})
    headers = {'content-type': 'application/json'}
    response = requests.post(
        node_info["endpoint"],
        data=json.dumps(payload),
        headers=headers,
        auth=auth
    )
    return json.loads(response.text)["result"]["last_block"]["block_index"]


def get_starting_block(node_info, filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                return data.get('last_block', get_block_count(node_info))
        except json.JSONDecodeError:
            return get_block_count(node_info)
    else:
        return get_block_count(node_info)


NODE_A = xja_node
NODE_B = xchain_node
START_BLOCK = get_starting_block(xja_node, './out/hashes_matching.json')

hashes_matching = {
    "ledger_hash": False,
    "txlist_hash": False,
    "messages_hash": False,
    "block_index_ledger_match": 0,
    "block_index_tx_match": 0,
    "block_index_msg_match": 0,
    "block_index": 0,
    "last_block": START_BLOCK
}

try:
    os.system(f'say "Starting consensus check at block index: {START_BLOCK}"')
    for i in tqdm(range(START_BLOCK, 0, -1), desc="Processing Blocks"):
        block_a = get_block(NODE_A, {"block_indexes": [i]})
        block_b = get_block(NODE_B, {"block_indexes": [i]})

        ledger_hash_a = block_a[0]["ledger_hash"]
        ledger_hash_b = block_b[0]["ledger_hash"]
        if ledger_hash_a == ledger_hash_b and hashes_matching["ledger_hash"] is False:
            hashes_matching["ledger_hash"] = True
            hashes_matching["block_index_ledger_match"] = i
            print(f"Ledger hashes match at block index: {i}")
            os.system(f'say "Ledger hashes match at block index: {i}"')

        tx_hash_a = block_a[0]["txlist_hash"]
        tx_hash_b = block_b[0]["txlist_hash"]
        if (
            tx_hash_a == tx_hash_b
            and hashes_matching["txlist_hash"] is False
        ):
            hashes_matching["txlist_hash"] = True
            hashes_matching["block_index_tx_match"] = i
            print(f"Tx hashes match at block index: {i}")
            os.system(f'say "Tx hashes match at block index: {i}"')

        msg_hash_a = block_a[0]["messages_hash"]
        msg_hash_b = block_b[0]["messages_hash"]
        if (
            msg_hash_a == msg_hash_b
            and hashes_matching["messages_hash"] is False
        ):
            hashes_matching["messages_hash"] = True
            hashes_matching["block_index_msg_match"] = i
            os.system(f'say "Msg hashes match at block index: {i}"')
            print(f"Msg hashes match at block index: {i}")

        hashes_matching["last_block"] = i
        with open('./out/hashes_matching.json', 'w') as file:
            json.dump(hashes_matching, file, indent=4)

        if (
            hashes_matching["ledger_hash"]
            and hashes_matching["txlist_hash"]
            and hashes_matching["messages_hash"]
        ):
            hashes_matching["block_index"] = i
            print(f"All Hashes match at block index: {i}")
            os.system(f'say "All Hashes match at block index: {i}"')
            break

        time.sleep(1)
    print(hashes_matching)
except:
    os.system(f'say "Error in consensus check relaunch script, last block checked {hashes_matching["last_block"]}"')