# agents/oracle_monitor.py

import random
import time
import logging
from datetime import datetime # FIX: Import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OracleMonitorAgent:
    def __init__(self):
        logging.info("OracleMonitorAgent initialized (simulated).")

    def fetch_simulated_rwa_data(self, rwa_id, current_month):
        """
        Simulates fetching real-world data for an RWA project via a decentralized oracle.
        Data will show slight variations over time.

        Args:
            rwa_id (str): The ID of the Real World Asset.
            current_month (int): A numerical representation of the current monitoring period (e.g., month number).

        Returns:
            dict: A dictionary containing simulated oracle data:
                  - 'success' (bool)
                  - 'co2_reduction_tons' (float)
                  - 'energy_generated_kwh' (float)
                  - 'jobs_created' (int)
                  - 'water_savings_liters' (float)
                  - 'status_update' (str)
                  - 'timestamp' (str)
                  - 'error' (str, optional)
        """
        logging.info(f"Simulating oracle data fetch for RWA: {rwa_id}, Month: {current_month}")
        time.sleep(0.5) # Simulate network latency

        try:
            # Simulate slight variations in performance
            co2_factor = 0.9 + (random.random() * 0.2) # 90% to 110% of expected
            energy_factor = 0.85 + (random.random() * 0.3) # 85% to 115% of expected
            jobs_variation = random.randint(-1, 1) # +/- 1 job
            water_factor = 0.9 + (random.random() * 0.2)

            # These base values would ideally come from the initial loan_details
            # For this simulation, we'll use some arbitrary bases for demonstration
            base_co2 = 5000 * (1 + (current_month * 0.005)) # Slight increase over time
            base_energy = 1000000 * (1 + (current_month * 0.003))
            base_jobs = 10
            base_water = 500000 * (1 + (current_month * 0.002))

            co2_reduction = base_co2 * co2_factor
            energy_generated = base_energy * energy_factor
            jobs_created = max(0, base_jobs + jobs_variation)
            water_savings = base_water * water_factor

            status = "On Track"
            if co2_reduction < base_co2 * 0.8:
                status = "Underperforming CO2"
            if energy_generated < base_energy * 0.8:
                status = "Underperforming Energy"

            logging.info(f"Simulated oracle data for {rwa_id}: CO2={co2_reduction:.2f}, Energy={energy_generated:.2f}")
            return {
                "success": True,
                "co2_reduction_tons": co2_reduction,
                "energy_generated_kwh": energy_generated,
                "jobs_created": jobs_created,
                "water_savings_liters": water_savings,
                "status_update": status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logging.error(f"Simulated oracle data fetch failed for {rwa_id}: {e}")
            return {"success": False, "error": str(e)}

