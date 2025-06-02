# agents/goat_agent.py
import time
import numpy as np # Ensure numpy is imported

class GOATAgent:
    def _init_(self):
        print("Initialized local GOAT Agent (stub mode)")
        self.knowledge_base = {
            "risk_factors": ["credit_score", "default_history", "debt_to_income_ratio"],
            "impact_criteria": ["project_type", "estimated_co2_reduction_tons_per_year", "estimated_energy_generated_kwh_per_year", "estimated_jobs_created"]
        }

    def analyze_and_execute(self, borrower_data, rwa_data, context):
        print("\n🧠 AI Agent: Analyzing data in local GOAT Agent...")
        print(f"Context: {context}")
        time.sleep(1) # Simulate complex analysis

        summary = ""
        recommendation = ""
        confidence_score = 0.00

        # --- GOAT Agent's Decision-Making Logic ---
        # This logic determines the summary, recommendation, and confidence score.
        # It uses the data passed from app.py to make a simulated decision.

        # Financial Assessment (using borrower_data)
        credit_score = borrower_data.get("credit_score", 600)
        default_history = borrower_data.get("default_history", 0)
        debt_to_income_ratio = borrower_data.get("debt_to_income_ratio", 0.4) # Assuming a default if not present

        financial_risk_score = (1 - (credit_score / 850)) * 100
        if default_history > 0:
            financial_risk_score += 20
        if debt_to_income_ratio > 0.4:
            financial_risk_score += (debt_to_income_ratio - 0.4) * 50 # Increase risk for higher DTI
        financial_risk_score = round(min(max(financial_risk_score, 0), 100), 2)

        # Environmental Impact Assessment (using rwa_data)
        project_type = rwa_data.get("project_type")
        co2_reduction = rwa_data.get("estimated_co2_reduction_tons_per_year", 0)
        energy_generated = rwa_data.get("estimated_energy_generated_kwh_per_year", 0)
        jobs_created = rwa_data.get("estimated_jobs_created", 0)

        impact_score = 0
        if project_type == "solar":
            impact_score += 30
        if co2_reduction > 5000:
            impact_score += 40
        if energy_generated > 1000000:
            impact_score += 30
        if jobs_created > 10:
            impact_score += 10 # Small bonus for job creation
        impact_score = round(min(max(impact_score, 0), 100), 2)

        # Combined Recommendation Logic
        if financial_risk_score < 30 and impact_score > 70:
            summary = "Highly favorable project: low financial risk and significant green impact."
            recommendation = "Approve loan with priority; recommend favorable terms."
            confidence_score = 0.95
        elif financial_risk_score < 60 and impact_score > 40:
            summary = "Standard green loan project: moderate financial risk and good impact."
            recommendation = "Approve loan after standard due diligence; proceed."
            confidence_score = 0.70
        elif financial_risk_score >= 60 and impact_score > 50:
            summary = "Higher financial risk, but strong green impact. Requires careful review."
            recommendation = "Conditional approval: request additional collateral or higher interest."
            confidence_score = 0.55
        else:
            summary = "Project requires further review due to higher financial risk or limited green impact."
            recommendation = "Deny loan or request substantial additional information/collateral."
            confidence_score = 0.30

        # Add a bit of controlled randomness to confidence score for "AI feel"
        confidence_score = min(1.0, max(0.0, confidence_score + np.random.uniform(-0.05, 0.05))) # Reduced range

        # --- Placeholder for Crossmint GOAT SDK integration ---
        # As discussed, this is where you'd integrate actual Crossmint GOAT SDK calls
        # if you had access and time. For the hackathon, you'll explain this.
        # You could have a method here that calls the SDK to initiate a transaction
        # or manage an embedded wallet.
        print("\n🤖 GOAT Agent: Crossmint GOAT SDK integration point (SDK not integrated - due to private access).")
        print("   (If integrated, this agent would seamlessly create embedded wallets or sign transactions.)")
        # --------------------------------------------------------

        return {
            "goat_insights": {
                "summary": summary,
                "recommendation": recommendation,
                "confidence_score": confidence_score
            },
            "blockchain_action": "initiate_transaction" # This can be conditional later
        }
