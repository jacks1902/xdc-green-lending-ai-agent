# agents/impact_assessor.py

import random
import time
import logging
from datetime import datetime # Import datetime for timestamp in simulated report

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImpactAssessorAgent:
    def __init__(self, w3_instance=None, oracle_contract_address=None, oracle_contract_abi=None, private_key=None, from_address=None):
        self.w3 = w3_instance
        self.oracle_contract_address = oracle_contract_address
        self.oracle_contract_abi = oracle_contract_abi
        self.private_key = private_key
        self.from_address = from_address
        self.oracle_contract = None # Will be initialized if contract details are provided

        if self.w3 and self.oracle_contract_address and self.oracle_contract_abi:
            try:
                self.oracle_contract = self.w3.eth.contract(address=self.oracle_contract_address, abi=self.oracle_contract_abi)
                logging.info("ImpactAssessorAgent initialized with on-chain oracle (simulated interaction).")
            except Exception as e:
                logging.warning(f"Could not initialize oracle contract: {e}. Impact assessment will be purely simulated.")
        else:
            logging.info("ImpactAssessorAgent initialized (purely simulated - no on-chain oracle details provided).")

    def assess_impact(self, project_description, rwa_data, loan_amount, loan_term_years):
        """
        Assesses the environmental and social impact of a green loan proposal.
        This version includes a simulated LLM call for a comprehensive underwriting report.

        Args:
            project_description (str): A description of the green project.
            rwa_data (pd.Series): Data of the associated Real World Asset.
            loan_amount (float): The amount of the loan.
            loan_term_years (float): The term of the loan in years.

        Returns:
            dict: A dictionary containing impact assessment results:
                  - 'impact_score' (float)
                  - 'impact_category' (str)
                  - 'feedback_notes' (list)
                  - 'underwriting_report' (str) # NEW: Comprehensive report
        """
        logging.info(f"Assessing impact for project: {project_description[:50]}...")
        time.sleep(1.5) # Simulate AI processing time

        # Basic impact score calculation (can be made more complex)
        co2_reduction = rwa_data.get('estimated_co2_reduction_tons_per_year', 0)
        energy_generated = rwa_data.get('estimated_energy_generated_kwh_per_year', 0)
        jobs_created = rwa_data.get('estimated_jobs_created', 0)
        water_savings = rwa_data.get('estimated_water_savings_liters_per_year', 0)
        
        # FIX: Ensure certification is always a string
        certification = str(rwa_data.get('certification_level', 'None')) 

        impact_score = 0
        feedback_notes = []

        # CO2 Impact
        if co2_reduction > 10000: impact_score += 30
        elif co2_reduction > 1000: impact_score += 15
        else: feedback_notes.append("Consider projects with higher CO2 reduction potential.")

        # Energy Impact
        if energy_generated > 5000000: impact_score += 25
        elif energy_generated > 1000000: impact_score += 10
        else: feedback_notes.append("Seek RWAs with greater renewable energy generation capacity.")

        # Social Impact (Jobs)
        if jobs_created > 50: impact_score += 20
        elif jobs_created > 10: impact_score += 10
        else: feedback_notes.append("Encourage projects that create more local employment opportunities.")

        # Water Savings (if applicable)
        if water_savings > 1000000: impact_score += 15
        elif water_savings > 100000: impact_score += 5
        elif 'water' in project_description.lower() and water_savings == 0:
            feedback_notes.append("Project description mentions water, but no water savings estimated.")

        # Certification Bonus (now safe to use 'in' operator)
        if "Gold" in certification: impact_score += 10
        elif "Silver" in certification: impact_score += 5
        else: feedback_notes.append("Recommend seeking higher environmental certifications for stronger impact.")

        # Adjust score based on loan size and term (simulated)
        if loan_amount > 500000: impact_score += 5 # Larger loans for larger projects
        if loan_term_years > 5: impact_score -= 5 # Longer term might imply higher long-term risks

        impact_score = round(min(max(impact_score, 0), 100), 2) # Cap between 0 and 100

        impact_category = "Low"
        if impact_score >= 70:
            impact_category = "High"
        elif impact_score >= 40:
            impact_category = "Medium"

        # Simulate LLM call for comprehensive underwriting report
        underwriting_report = self._simulate_llm_underwriting_report(
            project_description, rwa_data, loan_amount, loan_term_years,
            impact_score, impact_category, feedback_notes
        )

        return {
            "impact_score": impact_score,
            "impact_category": impact_category,
            "feedback_notes": feedback_notes,
            "underwriting_report": underwriting_report 
        }

    def _simulate_llm_underwriting_report(self, project_description, rwa_data, loan_amount, loan_term_years,
                                           impact_score, impact_category, feedback_notes):
        """
        Simulates an LLM generating a detailed underwriting report.
        This uses a fixed template for demonstration. In a real app, this would be a Gemini API call.
        """
        logging.info("Simulating LLM generation of underwriting report...")
        
        report_template = f"""
## Comprehensive Green Loan Underwriting Report

**Project Overview:**
{project_description}

**Real World Asset (RWA) Details:**
* **Asset Type:** {rwa_data.get('project_type', 'N/A').title()}
* **Location:** {rwa_data.get('location', 'N/A')}
* **Certification Level:** {rwa_data.get('certification_level', 'N/A')}
* **Estimated CO₂ Reduction:** {rwa_data.get('estimated_co2_reduction_tons_per_year', 0):,} tons/year
* **Estimated Energy Generation:** {rwa_data.get('estimated_energy_generated_kwh_per_year', 0):,} kWh/year
* **Estimated Water Savings:** {rwa_data.get('estimated_water_savings_liters_per_year', 0):,} liters/year
* **Estimated Jobs Created:** {rwa_data.get('estimated_jobs_created', 0)}

**Loan Parameters:**
* **Requested Amount:** {loan_amount:,} XDC
* **Loan Term:** {loan_term_years:.1f} years

**Impact Assessment Summary:**
* **Calculated Impact Score:** {impact_score:.2f}/100
* **Impact Category:** {impact_category}
* **Key Feedback/Recommendations:**
    {'- ' + '\\n- '.join(feedback_notes) if feedback_notes else 'No specific feedback generated.'}

**ESG Factors Analysis (Simulated LLM Insights):**
This project demonstrates a strong commitment to environmental sustainability through its focus on {rwa_data.get('project_type', 'renewable energy')}. The estimated CO₂ reduction and energy generation metrics are significant, contributing positively to climate action goals. Socially, the project's ability to create {rwa_data.get('estimated_jobs_created', 0)} jobs is a notable benefit for local communities. The presence of a '{rwa_data.get('certification_level', 'N/A')}' certification adds credibility to its green credentials.

**Potential Risks & Mitigations (Simulated LLM Insights):**
* **Environmental Risk:** While the project aims for substantial environmental benefits, reliance on specific weather patterns (e.g., solar irradiance) could impact energy generation targets. Mitigation involves robust site selection and operational resilience planning.
* **Execution Risk:** The successful implementation of a project of this scale requires experienced project management and adherence to timelines. Regular progress monitoring and milestone-based disbursements are recommended.
* **Market Risk:** Fluctuations in energy prices or changes in renewable energy policies could affect project revenues. Long-term power purchase agreements (PPAs) can mitigate this.

**Overall Recommendation (Simulated LLM Insights):**
Based on the comprehensive assessment, this green loan proposal presents a compelling opportunity to finance a high-impact RWA. The project's alignment with green objectives, coupled with its potential for job creation, makes it a strong candidate for tokenization and inclusion in a sustainable finance portfolio. Further due diligence on the borrower's operational capacity and detailed financial projections is advised before final approval.

This report is a simulated output and should be validated with real-world data and expert analysis.
"""
        return report_template

