# blockchain/xdc_interact.py
from web3 import Web3
from decimal import Decimal
import time

# --- CONFIGURATION (RPC URL only, secrets handled by Streamlit) ---
XDC_TESTNET_RPC_URL = "https://erpc.apothem.network"
# Or mainnet: "https://rpc.xinfin.network"

# Define a reasonable minimum gas price in Gwei for the Apothem testnet
# This helps prevent 'under min gas price' errors often seen on XDC testnet nodes.
# You might need to adjust this value (e.g., 50, 100, 250, 500) based on specific node requirements.
MIN_GAS_PRICE_GWEI = 250

# --- CONNECT TO TESTNET ---
def connect_to_xdc_testnet(rpc_url):
    """Establishes and returns a Web3 connection to the XDC network."""
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if w3.is_connected():
            print(f"✅ Connected to XDC Apothem Testnet: {rpc_url}")
            chain_id = w3.eth.chain_id
            print(f"🔗 Chain ID: {chain_id} (expected: 51 for Apothem)")
            if chain_id != 51: # Check for Apothem Testnet chain ID
                print("⚠️ WARNING: Unexpected Chain ID! Ensure you're on the correct network.")
            return w3
        else:
            print("❌ Connection failed. Web3 instance is not connected.")
            return None
    except Exception as e:
        print(f"❌ Error connecting to XDC network: {e}")
        return None

# --- CHECK BALANCE ---
def get_account_balance(w3_instance, address):
    """Retrieves and prints the balance of an XDC address."""
    try:
        checksum_address = Web3.to_checksum_address(address)
        print(f"📥 Checking balance for: {checksum_address}")
        balance_wei = w3_instance.eth.get_balance(checksum_address)
        balance_xdc = w3_instance.from_wei(balance_wei, 'ether')
        print(f"💰 Balance: {balance_xdc:.8f} tXDC")
        return balance_xdc
    except Exception as e:
        print(f"❌ Error getting balance for {address}: {e}")
        return None

# --- SIMULATED AI AGENT TO OPTIMIZE GAS PRICE ---
def ai_agent_optimize_gas_price(w3_instance, transaction_type="standard"):
    """
    Simulates an AI agent optimizing gas price, fetching current network price
    and ensuring it meets a minimum threshold for XDC testnet compatibility.
    """
    print("\n🧠 AI Agent: Analyzing network conditions for optimal gas price...")
    time.sleep(1)  # Simulate agent "thinking"

    # 1. Get the current recommended gas price from the network
    # For XDC, w3_instance.eth.gas_price often returns 0 or a very low value.
    network_gas_price_wei = w3_instance.eth.gas_price
    print(f"🔍 Network's suggested gas price: {w3_instance.from_wei(network_gas_price_wei, 'gwei')} Gwei")

    # 2. Convert minimum gas price to Wei for comparison
    min_gas_price_wei = w3_instance.to_wei(MIN_GAS_PRICE_GWEI, 'gwei')

    # 3. Choose the higher of the two: network suggested or our defined minimum
    # This addresses the 'under min gas price' issue for XDC testnet where nodes
    # might enforce a higher minimum than the network reports as default.
    if network_gas_price_wei < min_gas_price_wei:
        final_gas_price = min_gas_price_wei
        print(f"⚠️ Network suggested price too low ({w3_instance.from_wei(network_gas_price_wei, 'gwei')} Gwei). Using enforced minimum of {MIN_GAS_PRICE_GWEI} Gwei.")
    else:
        final_gas_price = network_gas_price_wei
        print(f"✅ Using network's suggested gas price ({w3_instance.from_wei(network_gas_price_wei, 'gwei')} Gwei).")

    print(f"🧠 AI Agent: Final recommended gas price: {w3_instance.from_wei(final_gas_price, 'gwei')} Gwei")

    return final_gas_price

# --- SEND TRANSACTION ---
def send_xdc_transaction(w3_instance, private_key_str, from_address, to_address, amount_xdc):
    """
    Sends an XDC transaction from one address to another.
    Requires a connected Web3 instance, sender's private key, sender's address,
    recipient's address, and the amount in XDC.
    """
    try:
        from_addr = Web3.to_checksum_address(from_address)
        to_addr = Web3.to_checksum_address(to_address)

        nonce = w3_instance.eth.get_transaction_count(from_addr)

        gas_price = ai_agent_optimize_gas_price(w3_instance, "standard")
        print(f"⛽ Using Gas Price: {w3_instance.from_wei(gas_price, 'gwei')} Gwei")

        # Standard gas limit for a simple XDC transfer
        gas_limit = 21000
        gas_cost_wei = gas_limit * gas_price
        gas_cost_xdc = w3_instance.from_wei(gas_cost_wei, 'ether')
        print(f"💸 Estimated Gas Cost: {gas_cost_xdc:.8f} tXDC")

        sender_balance = get_account_balance(w3_instance, from_address)
        if sender_balance is None:
            print("❌ Could not retrieve sender's balance. Transaction aborted.")
            return None

        # Ensure amount_xdc is Decimal for accurate arithmetic
        amount_xdc_decimal = Decimal(str(amount_xdc)) # Convert to Decimal if not already

        total_required = amount_xdc_decimal + gas_cost_xdc
        if sender_balance < total_required:
            print(f"❌ Insufficient funds! Required: {total_required:.8f} tXDC, Available: {sender_balance:.8f} tXDC")
            print("Please fund your account with more tXDC from a faucet (e.g., search 'Apothem Testnet Faucet'). Transaction aborted.")
            return None

        tx = {
            'nonce': nonce,
            'to': to_addr,
            'value': w3_instance.to_wei(amount_xdc_decimal, 'ether'),
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': w3_instance.eth.chain_id,
        }

        print(f"📤 Preparing to send {amount_xdc_decimal} tXDC from {from_address} to {to_address}...")

        signed_tx = w3_instance.eth.account.sign_transaction(tx, private_key_str)

        tx_hash = w3_instance.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"✅ Transaction sent! Hash: {tx_hash.hex()}")

        print("⏳ Waiting for transaction receipt...")
        receipt = w3_instance.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        if receipt.status == 1:
            print(f"🎉 Transaction Confirmed in Block {receipt.blockNumber}")
            print(f"⛽ Gas Used: {receipt.gasUsed}")
            return tx_hash.hex()
        else:
            print(f"❌ Transaction Failed. Receipt: {receipt}")
            return None

    except Exception as e:
        print(f"❌ Error sending transaction: {e}")
        error_msg = str(e).lower()
        if "insufficient funds" in error_msg or "balance" in error_msg:
            print("🔍 Reason: Insufficient balance. Please fund your account.")
        elif "invalid signature" in error_msg or "private key" in error_msg:
            print("🔍 Reason: Invalid private key. Double-check your private key configuration.")
        elif "nonce too low" in error_msg or "nonce" in error_msg:
            print("🔍 Reason: Nonce conflict. The transaction count might be out of sync. Try resyncing or waiting a moment.")
        elif "gas" in error_msg and "limit" in error_msg:
            print("🔍 Reason: Gas limit too high or too low for the network/transaction type.")
        return None

# --- MAIN EXECUTION (for direct testing of xdc_interact.py) ---
if __name__ == "__main__":
    print("Running xdc_interact.py directly for testing purposes.")
    # WARNING: For direct testing ONLY. In your Streamlit app, use st.secrets.
    # Replace with your actual testnet private key and addresses for direct testing
    TEST_PRIVATE_KEY = "YOUR_XDC_TESTNET_PRIVATE_KEY_HERE" # Get this from an Apothem faucet or create a new testnet wallet
    TEST_FROM_ADDRESS = "0x..." # The public address corresponding to TEST_PRIVATE_KEY
    TEST_TO_ADDRESS = "xdc..." # A recipient testnet address (e.g., another testnet wallet)

    print("🚀 Connecting to XDC Apothem Testnet...")
    w3_test_instance = connect_to_xdc_testnet(XDC_TESTNET_RPC_URL)

    if w3_test_instance:
        print("\n🔍 Checking Account Balance...")
        get_account_balance(w3_test_instance, TEST_FROM_ADDRESS)

        print("\n🔁 Sending Test Transaction...")
        # Note: You should have some tXDC in TEST_FROM_ADDRESS for this to succeed
        send_xdc_transaction(
            w3_test_instance,
            TEST_PRIVATE_KEY,
            TEST_FROM_ADDRESS,
            TEST_TO_ADDRESS,
            Decimal('0.0001')  # Amount to send (make sure this is less than your balance)
        )
    else:
        print("❌ Could not connect to the network. Please check your RPC URL or internet connection.")
