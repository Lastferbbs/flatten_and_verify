import io
import json
import time
from typing import Dict
import requests
from .flattener import Flattener
import sys

python_version = (
    f"{sys.version_info.major}.{sys.version_info.minor}"
    f".{sys.version_info.micro} {sys.version_info.releaselevel}"
)
REQUEST_HEADERS = {"User-Agent": f"Brownie/1.19.1 (Python/{python_version})"}
BLOCKSCOUT_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


explorers = {
    "rinkeby": {
        "url": "https://api-rinkeby.etherscan.io/api",
        "api_key": "api_key",
        "scan": 1,
    },
    "mordor": {
        "url": "https://blockscout.com/etc/mordor/api",
        "api_key": "0",
        "scan": 0,
    },
}


def get_verification_info(
    source_fp, _name, remaps, compiler_settings, bytecode_len, solidity_exact_version
) -> Dict:
    """
    Return a dict with flattened source code for this contract
    and further information needed for verification
    """

    flattener = Flattener(source_fp, _name, remaps, compiler_settings)

    return {
        "standard_json_input": flattener.standard_input_json,
        "contract_name": _name,
        "compiler_version": solidity_exact_version,
        "optimizer_enabled": True,
        "optimizer_runs": 200,
        "license_identifier": flattener.license,
        "bytecode_len": bytecode_len,
    }, flattener


def publish_source(
    _url,
    _address,
    source_fp,
    _name,
    solidity_exact_version,
    bytecode_len,
    compiler_settings={
        "evmVersion": "london",
        "optimizer": {"enabled": True, "runs": 200},
        "libraries": {},
    },
    remaps=dict(),
    silent=False,
    blockexplorer_list=explorers,
    api_key=False,
    blockscout=False,
) -> bool:
    """Flatten contract and publish source on the selected explorer"""

    compiler_settings["libraries"] = {_name + ".sol": {}}
    # Check required conditions for verifying
    try:
        if "api" in _url:
            url = _url
        else:
            chain = blockexplorer_list[_url]
            url = chain["url"]
        if not api_key:
            api_key = chain["api_key"]

    except:
        raise ValueError("Explorer API not set for this network")

    address = _address

    contract_info, flattener = get_verification_info(
        source_fp,
        _name,
        remaps,
        compiler_settings,
        bytecode_len,
        solidity_exact_version,
    )
    # Get source code and contract/compiler information

    # Select matching license code (https://etherscan.io/contract-license-types)
    identifier = contract_info["license_identifier"].lower()
    if "unlicensed" in identifier:
        license_code = 2
    elif "mit" in identifier:
        license_code = 3
    elif "agpl" in identifier and "3.0" in identifier:
        license_code = 13
    elif "lgpl" in identifier:
        if "2.1" in identifier:
            license_code = 6
        elif "3.0" in identifier:
            license_code = 7
    elif "gpl" in identifier:
        if "2.0" in identifier:
            license_code = 4
        elif "3.0" in identifier:
            license_code = 5
    elif "bsd-2-clause" in identifier:
        license_code = 8
    elif "bsd-3-clause" in identifier:
        license_code = 9
    elif "mpl" in identifier and "2.0" in identifier:
        license_code = 10
    elif identifier.startswith("osl") and "3.0" in identifier:
        license_code = 11
    elif "apache" in identifier and "2.0" in identifier:
        license_code = 12

    # get constructor arguments
    params_tx: Dict = {
        "apikey": api_key,
        "module": "account",
        "action": "txlist",
        "address": address,
        "page": 1,
        "sort": "asc",
        "offset": 1,
    }
    i = 0
    while True:
        response = requests.get(url, params=params_tx, headers=REQUEST_HEADERS)
        if response.status_code != 200:
            return f"Status {response.status_code} when querying {url}: {response.text}"
        data = response.json()
        if int(data["status"]) == 1:
            # Constructor arguments received
            break
        else:
            # Wait for contract to be recognized by etherscan
            # This takes a few seconds after the contract is deployed
            # After 10 loops we throw with the API result message (includes address)
            if i >= 10:
                return f"API request failed with: {data['result']}"
            elif i == 0:
                if not silent:
                    print(f"Waiting for {url} to process contract...")
            i += 1
            time.sleep(10)

    if data["message"] == "OK":
        constructor_arguments = data["result"][0]["input"][
            contract_info["bytecode_len"] + 2 :
        ]
    else:
        constructor_arguments = ""

    # Submit verification
    if blockscout:
        payload_verification: Dict = {
            "apikey": api_key,
            "module": "contract",
            "action": "verifysourcecode",
            "codeformat": "solidity-standard-json-input",
            "contractaddress": address,
            "contractname": f"{flattener.contract_file}:{flattener.contract_name}",
            "compilerversion": f"v{contract_info['compiler_version']}",
            "constructorArguements": constructor_arguments,
            "sourceCode": io.StringIO(json.dumps(flattener.standard_input_json)),
        }

        headers = BLOCKSCOUT_HEADERS

    else:
        payload_verification: Dict = {
            "apikey": api_key,
            "module": "contract",
            "action": "verifysourcecode",
            "contractaddress": address,
            "sourceCode": io.StringIO(json.dumps(flattener.standard_input_json)),
            "codeformat": "solidity-standard-json-input",
            "contractname": f"{flattener.contract_file}:{flattener.contract_name}",
            "compilerversion": f"v{contract_info['compiler_version']}",
            "optimizationUsed": 1 if contract_info["optimizer_enabled"] else 0,
            "runs": contract_info["optimizer_runs"],
            "constructorArguements": constructor_arguments,
            "licenseType": license_code,
        }
        headers = REQUEST_HEADERS

    response = requests.post(url, data=payload_verification, headers=headers)

    if response.status_code != 200:
        return f"Status {response.status_code} when querying {url}: {response.text}"
    data = response.json()
    if int(data["status"]) != 1:
        return f"Failed to submit verification request: {data['result']}"

    # Status of request
    guid = data["result"]
    if not silent:
        print("Verification submitted successfully. Waiting for result...")
    time.sleep(10)
    params_status: Dict = {
        "apikey": api_key,
        "module": "contract",
        "action": "checkverifystatus",
        "guid": guid,
    }
    while True:
        response = requests.get(url, params=params_status, headers=REQUEST_HEADERS)
        if response.status_code != 200:
            return f"Status {response.status_code} when querying {url}: {response.text}"
        data = response.json()
        if data["result"] == "Pending in queue":
            if not silent:
                print("Verification pending...")
        else:
            if not silent:
                print(f"Verification complete. Result: {data['result']}")
            return data["message"] == "OK"
        time.sleep(10)
