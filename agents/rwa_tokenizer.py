# agents/rwa_tokenizer.py

import hashlib
import json
import logging
import time
import numpy as np # Import numpy for type checking

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RWATokenizerAgent:
    def __init__(self):
        logging.info("RWATokenizerAgent initialized (simulated).")

    def _convert_numpy_types(self, obj):
        """
        Recursively converts NumPy numerical types within a dictionary or list
        to standard Python types (int, float) to ensure JSON serializability.
        """
        if isinstance(obj, dict):
            return {k: self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(elem) for elem in obj]
        # FIX: Removed np.int6 as it's not a universal numpy attribute
        elif isinstance(obj, np.integer): # Handle NumPy integers
            return int(obj)
        elif isinstance(obj, np.floating): # Handle NumPy floats
            return float(obj)
        else:
            return obj

    def simulate_tokenize_rwa(self, loan_details):
        """
        Simulates the tokenization of a Real World Asset (RWA) loan.
        Generates a unique token ID and simulated metadata.

        Args:
            loan_details (dict): A dictionary containing details of the loan,
                                 e.g., loan_id, borrower_id, rwa_id, loan_amount, impact_score.

        Returns:
            dict: A dictionary containing simulated tokenization results:
                  - 'success' (bool)
                  - 'token_id' (str)
                  - 'token_symbol' (str)
                  - 'token_name' (str)
                  - 'metadata_url' (str) (simulated URL to decentralized metadata)
                  - 'error' (str, optional)
        """
        logging.info(f"Simulating RWA tokenization for loan: {loan_details.get('loan_id', 'N/A')}")
        time.sleep(1) # Simulate processing time

        try:
            # Convert NumPy types to standard Python types before JSON serialization
            serializable_loan_details = self._convert_numpy_types(loan_details)

            # Generate a unique token ID based on loan details hash
            loan_hash = hashlib.sha256(json.dumps(serializable_loan_details, sort_keys=True).encode()).hexdigest()
            token_id = f"RWA-{loan_hash[:10].upper()}"

            # Derive token name and symbol from loan details
            token_name = f"Green Loan #{loan_details.get('loan_id', 'Unknown')}"
            token_symbol = f"GL{loan_details.get('loan_id', '000').split('-')[-1]}" # e.g., GL0001

            # Simulate a metadata URL (e.g., on StorX or IPFS)
            simulated_metadata_url = f"https://simulated.storx.link/rwa_metadata/{token_id}.json"

            logging.info(f"RWA Tokenization simulated: Token ID {token_id}, Symbol {token_symbol}")
            return {
                "success": True,
                "token_id": token_id,
                "token_symbol": token_symbol,
                "token_name": token_name,
                "metadata_url": simulated_metadata_url
            }
        except Exception as e:
            logging.error(f"Simulated RWA tokenization failed: {e}")
            return {"success": False, "error": str(e)}

