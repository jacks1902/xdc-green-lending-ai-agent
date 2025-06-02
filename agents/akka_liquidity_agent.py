# agents/akka_liquidity_agent.py
import time
import hashlib
import random

class AkkaLiquidityAgent:
    def __init__(self, w3_instance, private_key, from_address, to_address):
        self.w3 = w3_instance
        self.private_key = private_key
        self.from_address = from_address
        self.to_address = to_address
        print("🤖 AKKA Liquidity Agent Initialized!")

    def optimize_liquidity_route(self, rwa_token_address, amount_rwa, preferred_output_asset, max_risk_tolerance):
        """
        Simulates AKKA Finance's liquidity optimization for RWA tokens.
        Returns a dictionary indicating success/failure and optimization details.
        """
        print(f"🤖 AKKA Liquidity Agent: Optimizing liquidity route for {amount_rwa} {rwa_token_address}...")
        time.sleep(2) # Simulate API call/computation time

        # --- Check for early exit condition ---
        # If risk tolerance is too low, simulate no route found
        if float(max_risk_tolerance) < 2: # Increased threshold for better demo variety
            return {
                "route_found": False,
                "optimization_details": {},
                "simulated_slippage_percent": 0.0,
                "simulated_gas_cost_xdc": 0.0,
                "error_message": "No suitable liquidity route found with the given risk tolerance."
            }

        # --- Simulate finding a route ---
        # These details will be nested under 'optimization_details' in the final return
        optimal_route_details = {
            "selected_pool": "AKKA-USDC Liquidity Pool " + random.choice(["X", "Y", "Z"]),
            "via_dex": random.choice(["XDC Swap", "Pandora Dex", "FusionX"]), # Consistent with app.py expectation
            "liquidity_depth": random.randint(5_000_000, 15_000_000), # Numerical value
            "estimated_fees_percent": random.uniform(0.01, 0.1), # Numerical percentage for calculation
            "risk_score": max_risk_tolerance * random.uniform(0.7, 0.9), # Numerical value
        }

        # These values are expected directly at the top level of the `optimization_results` dictionary in app.py
        simulated_slippage_percent = random.uniform(0.01, 0.15) # Numerical
        simulated_gas_cost_xdc = random.uniform(0.00001, 0.00005) # Numerical


        print(f"✅ AKKA Liquidity Agent: Optimal route found: {optimal_route_details['selected_pool']}")
        
        # IMPORTANT: Return a single dictionary with consistent keys as expected by app.py
        return {
            "route_found": True,
            "optimization_details": optimal_route_details,
            "simulated_slippage_percent": simulated_slippage_percent,
            "simulated_gas_cost_xdc": simulated_gas_cost_xdc
        }

    def simulate_execute_trade(self, optimized_route_details, amount_rwa, preferred_output_asset):
        """
        Simulates the execution of a trade via the optimized route.
        Expects 'optimized_route_details' to be the dictionary returned by optimize_liquidity_route.
        """
        # Ensure optimal_route_details and its sub-keys exist before accessing
        selected_pool_name = optimized_route_details.get('optimization_details', {}).get('selected_pool', 'an unknown pool')
        print(f"🚀 AKKA Liquidity Agent: Simulating trade execution via {selected_pool_name}...")
        time.sleep(3) # Simulate blockchain transaction time

        trade_executed = False
        simulated_tx_hash = None
        output_amount_received = 0

        # Only proceed if a route was actually found in the previous step
        if optimized_route_details.get("route_found"):
            try:
                amount_rwa_float = float(amount_rwa)
                # Access estimated_fees_percent from nested 'optimization_details'
                fees_decimal = optimized_route_details['optimization_details']['estimated_fees_percent'] / 100
                slippage_decimal = optimized_route_details['simulated_slippage_percent'] / 100

                # Calculate simulated amount received after fees and slippage
                # Add some random variance to the final amount
                simulated_amount_received = amount_rwa_float * (1 - fees_decimal) * (1 - slippage_decimal) * random.uniform(0.995, 1.005)
                
                trade_executed = True
                simulated_tx_hash = '0x' + hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()

            except KeyError as e:
                print(f"Error accessing key in route details during trade simulation: {e}. Trade simulation failed.")
                # Keep trade_executed as False and output_amount_received as 0
            except Exception as e:
                print(f"An unexpected error occurred during trade simulation: {e}")
                # Keep trade_executed as False and output_amount_received as 0
        else:
            print("Trade simulation skipped: No optimal route was found initially.")

        print(f"✅ Simulated AKKA Trade Transaction: {'Executed' if trade_executed else 'Failed'}")

        return {
            "trade_executed": trade_executed,
            "simulated_tx_hash": simulated_tx_hash,
            "output_amount_received": output_amount_received,
            "output_asset": preferred_output_asset
        }

    def integrate_goat_sdk_trade(self, trade_params):
        """
        Placeholder method for integrating with Crossmint GOAT SDK for AI-powered
        transaction initiation and embedded wallets. This remains a simulation/placeholder.
        """
        print("🐐 AKKA Liquidity Agent: Placeholder for Crossmint GOAT SDK integration.")
        return {"status": "GOAT SDK integration simulated", "trade_params": trade_params}
