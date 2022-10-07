# Flatten_and_verify - standalone module to automate contract verification with pretty flattening (every file separated on blockexplorer).
 Code is a modified brownie built in flattener and verify.

### It can be used with scan-like website (etherscan, snowtrace) and blockscout explorers.



# Dependencies

Module use requests library to verify contracts.


# Instalation:

via pip

```
pip install flatten_and_verify
```
# Documentation:

Using module with example arguments
```
from flatten_and_verify import source_verify

#### REQUIRED ARGUMENTS - most can be taken from solcx
api = "https://api-sepolia.etherscan.io/api"
contract_address = "0x8412938129123213121212312321"
path_to_solidity_main_file = "/home/user/Desktop/solidity/MyContract.sol"
contract_name = "MyContract"
exact_solidity_version = "0.8.16+commit.07a7930e"
bytecode_len = 5132

#### OPTIONAL ARGUMENTS WITH ITS DEFAULT VALUES
compiler_settings={
        "evmVersion": "london",
        "optimizer": {"enabled": True, "runs": 200},
        "libraries": {},
    }
remaps=dict() # Example Remappings - remaps = {"@chainlink": "/home/user/Desktop/solidity/chainlink-brownie-contracts@1.1.1", "@openzeppelin": "/home/user/Desktop/solidity/openzeppelin-contracts}
silent=False
blockexplorer_list=explorers
api_key=0
blockscout=False


publish_source(
        api,
        contract_address,
        path_to_solidity_main_file,
        contract_name,
        exact_solidity_version,
        bytecode_len,
    )
```

# Required parameters
## api : string
link to blockexplorer api or blockexplorer name - take a look at blockexplorer_list
## contract_address : string
address of contract to verify
## path_to_solidity_main_file : string
path to your main solidity file
## contract_name : string
contract name used inside your solidity file
## exact_solidity_version : string
exact solidity version, e.g. 0.8.16+commit.07a7930e
## bytecode_len : int
contract bytecode length, without constructor arguments

# Optional parameters with default values

## - compiler_settings : dict, optional
```
compiler_settings={
        "evmVersion": "london",
        "optimizer": {"enabled": True, "runs": 200},
        "libraries": {},
    }
```
It is possible here to change evmVersion, disable optimizer and add libraries ("libraries": {MyContract.sol": {} })

## - remaps : dict, optional
remaps=dict()

Way to add Remappings - 
```
remaps = {"@chainlink": "/home/user/Desktop/solidity/chainlink-brownie-contracts@1.1.1", "@openzeppelin": "/home/user/Desktop/solidity/openzeppelin-contracts}
```

## - silent : bool, optional
silent=False - If true disable all prints

## - blockexplorer_list : dict, optional
blockexplorer_list=explorers 

explorers is a built in dict of 4 blockscout explorers - **moonriver, moonbeam, cronos, evmos**

Possible to prepare and add your list of explorers, in format shown delov, then you can access explorers in this dict by name e.g. api = sepolia:
```
explorers = {
    "sepolia": {
        "url": "https://api-sepolia.etherscan.io/api",
        "api_key": "api_key",
        "scan": 1, # 1 if scan explorer, else 0
    },
    "mordor": {
        "url": "https://blockscout.com/etc/mordor/api",
        "api_key": "0", # can stay zero, blockscout doesn't need apikey
        "scan": 0,
    },
}
```
## - api_key : string, optional

api_key=0 if u give url, then you must provide apikey to scans explorers, if u have it in your list and you give name, can stay 0, also can stay 0 with blockscout
## - blockscout : bool, optional
blockscout=False - must be true if u are using blockscout,  if u are using your own list and blockscout, can stay false, just change "scan" to 0 in explorers dict


# License

This project is licensed under the MIT license.