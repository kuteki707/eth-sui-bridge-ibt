from flask import Flask, request, render_template
import subprocess

app = Flask(__name__)

# Ethereum Configuration
ETH_PROVIDER = "http://127.0.0.1:8545"  # Local Anvil node
ETH_CHAIN_ID = "31337"  # Local Anvil chain ID
ETH_GAS_LIMIT = "2000000"  # Gas limit

# Ethereum IBT Token Contract
IBT_ETH_CONTRACT_ADDRESS = "0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6"

# Sui Configuration
SUI_PACKAGE_ID = "0x4b9c65ffeada92d4ed63f26b11f091ff19a9f099544efd34800f85ceb5c3f793"
SUI_TREASURY_CAP_ID = "0x5844ad4d5b889eeaa71ad1573ef4c8dbda7a56ff7528c314d638e2fa770c9a96"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/transfer_eth_to_sui', methods=['POST'])
def transfer_eth_to_sui():
    eth_sender = request.form['ethSender']
    eth_private_key = request.form['ethPrivateKey']
    amount = int(request.form['amountEthToSui'])
    sui_recipient = request.form['suiRecipient']

    try:
        # Step 2: Burn tokens on Ethereum
        burn_command = [
            "cast", "send", "--rpc-url", ETH_PROVIDER,
            "--private-key", eth_private_key,
            "--chain", ETH_CHAIN_ID,
            "--gas-price", "1",
            "--gas-limit", ETH_GAS_LIMIT,
            IBT_ETH_CONTRACT_ADDRESS, "burn(address,uint256)", eth_sender, str(amount)
        ]
        burn_result = subprocess.run(burn_command, capture_output=True, text=True)
        if burn_result.returncode != 0:
            raise Exception(f"Ethereum burn failed: {burn_result.stderr}")

        # Step 3: Mint tokens on Sui
        mint_command = [
            "sui", "client", "call",
            "--package", SUI_PACKAGE_ID, 
            "--module", "ibt",
            "--function", "mint",
            "--args", SUI_TREASURY_CAP_ID, str(amount), sui_recipient, 
            "--gas-budget", "300000000"  
        ]
        mint_result = subprocess.run(mint_command, capture_output=True, text=True)
        if mint_result.returncode != 0:
            raise Exception(f"Sui mint failed: {mint_result.stderr}")

        status = f"Success! Ethereum Burn Result: {burn_result.stdout}, Sui Mint Result: {mint_result.stdout}"
    except Exception as e:
        status = f"Error: {str(e)}"

    return render_template('index.html', status=status)


@app.route('/transfer_sui_to_eth', methods=['POST'])
def transfer_sui_to_eth():
    sui_sender = request.form['suiSender']
    sui_private_key = request.form['suiPrivateKey']
    amount = int(request.form['amountSuiToEth'])
    eth_recipient = request.form['ethRecipient']

    try:
        # Step 2: Burn tokens on Sui
        burn_command = [
            "sui", "client", "call",
            "--package", SUI_PACKAGE_ID,
            "--module", "ibt",
            "--function", "burn",
            "--args", SUI_TREASURY_CAP_ID, str(amount),
            "--gas-budget", "100000000"
        ]
        burn_result = subprocess.run(burn_command, capture_output=True, text=True)
        if burn_result.returncode != 0:
            raise Exception(f"Sui burn failed: {burn_result.stderr}")

        # Step 3: Mint tokens on Ethereum
        mint_command = [
            "cast", "send", "--rpc-url", ETH_PROVIDER,
            "--private-key", sui_private_key,
            "--chain", ETH_CHAIN_ID,
            "--gas-price", "1",
            "--gas-limit", ETH_GAS_LIMIT,
            IBT_ETH_CONTRACT_ADDRESS, "mint(address,uint256)", eth_recipient, str(amount)
        ]
        mint_result = subprocess.run(mint_command, capture_output=True, text=True)
        if mint_result.returncode != 0:
            raise Exception(f"Ethereum mint failed: {mint_result.stderr}")

        status = f"Success! Sui Burn Result: {burn_result.stdout}, Ethereum Mint Result: {mint_result.stdout}"
    except Exception as e:
        status = f"Error: {str(e)}"

    return render_template('index.html', status=status)


if __name__ == '__main__':
    app.run(debug=True)