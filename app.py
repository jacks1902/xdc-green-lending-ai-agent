import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
from web3 import Web3 

# Import your custom agents
from agents.impact_assessor import ImpactAssessorAgent
from agents.goat_agent import GOATAgent
from agents.akka_liquidity_agent import AkkaLiquidityAgent
from agents.storx_agent import StorXAgent 
from agents.rwa_tokenizer import RWATokenizerAgent 
from agents.oracle_monitor import OracleMonitorAgent 
from agents.dao_governance import DAOGovernanceAgent 

# Import the blockchain interaction functions from your blockchain folder
from blockchain.xdc_interact import send_xdc_transaction, connect_to_xdc_testnet

# --- App Configuration ---
st.set_page_config(layout="wide", page_title="XDC Green Lending AI Agent")

DATA_PATH = "data"
MOCK_BORROWER_PROFILES_PATH = os.path.join(DATA_PATH, "mock_borrower_profiles.csv")
MOCK_RWA_PROPERTIES_PATH = os.path.join(DATA_PATH, "mock_rwa_properties.csv")

# --- XDC Network Configuration ---
XDC_TESTNET_RPC_URL = "https://erpc.apothem.network"

# --- Global Web3 Connection (connect once when app starts and cache it) ---
@st.cache_resource
def get_web3_instance():
    """Establishes and returns a Web3 connection to the XDC network."""
    return connect_to_xdc_testnet(XDC_TESTNET_RPC_URL)

global_w3 = get_web3_instance()

# Stop the app if connection fails
if not global_w3:
    st.error("🚨 Failed to connect to XDC Testnet. Please check your internet connection or RPC URL.")
    st.stop()

# --- Retrieve XDC wallet details from secrets ---
try:
    XDC_PRIVATE_KEY = st.secrets["xdc"]["private_key"]
    XDC_FROM_ADDRESS = st.secrets["xdc"]["from_address"]
    XDC_TO_ADDRESS = st.secrets["xdc"]["to_address"]
except KeyError as e:
    st.error(f"🚨 Missing XDC wallet details in .streamlit/secrets.toml: {e}. Please ensure 'private_key', 'from_address', and 'to_address' are set under the [xdc] section.")
    st.stop()


@st.cache_data
def load_mock_data():
    """Loads mock borrower and RWA data from CSV files."""
    try:
        borrower_df = pd.read_csv(MOCK_BORROWER_PROFILES_PATH)
        rwa_df = pd.read_csv(MOCK_RWA_PROPERTIES_PATH)
        return borrower_df, rwa_df
    except Exception as e:
        st.error(f"Error loading data: {e}. Ensure 'data' folder and CSVs exist.")
        st.stop()

borrower_profiles_df, rwa_properties_df = load_mock_data()

# Initialize core agents
impact_assessor = ImpactAssessorAgent(
    w3_instance=global_w3,
    oracle_contract_address=None,
    oracle_contract_abi=None,
    private_key=XDC_PRIVATE_KEY,
    from_address=XDC_FROM_ADDRESS
)
goat_agent = GOATAgent()

akka_liquidity_agent = AkkaLiquidityAgent(
    w3_instance=global_w3,
    private_key=XDC_PRIVATE_KEY,
    from_address=XDC_FROM_ADDRESS,
    to_address=XDC_TO_ADDRESS
)

# Initialize StorX Agent (FIXED: Safely retrieve 'storx' section)
storx_secrets = st.secrets.get("storx", {}) # <-- FIX IS HERE: Use .get() for the 'storx' key itself
STORX_ACCESS_KEY_ID = storx_secrets.get("access_key_id")
STORX_SECRET_ACCESS_KEY = storx_secrets.get("secret_access_key")
STORX_ENDPOINT_URL = storx_secrets.get("endpoint_url")
STORX_BUCKET_NAME = storx_secrets.get("bucket_name")

storx_agent = StorXAgent(
    access_key_id=STORX_ACCESS_KEY_ID,
    secret_access_key=STORX_SECRET_ACCESS_KEY,
    endpoint_url=STORX_ENDPOINT_URL,
    bucket_name=STORX_BUCKET_NAME
)

# NEW: Initialize Bonus Agents (Simulated)
rwa_tokenizer_agent = RWATokenizerAgent()
oracle_monitor_agent = OracleMonitorAgent()
dao_governance_agent = DAOGovernanceAgent()


if "submitted_loans" not in st.session_state:
    st.session_state.submitted_loans = []
if "latest_loan_for_storx" not in st.session_state: 
    st.session_state.latest_loan_for_storx = None
if "current_monitoring_month" not in st.session_state: # For Oracle simulation
    st.session_state.current_monitoring_month = 0


# --- Utility ---
def calculate_financial_risk(borrower, loan_amount, loan_term_months):
    """Calculates a simplified financial risk score."""
    score = (1 - (borrower["credit_score"] / 850)) * 100
    if borrower["default_history"] > 0:
        score += 15
    if loan_amount > 500000:
        score += ((loan_amount - 500000) / 100000) * 2
    if loan_term_months > 36:
        score += ((loan_term_months - 36) / 12) * 3
    score = round(min(max(score, 0), 100), 2)
    category = "High" if score >= 60 else "Medium" if score >= 30 else "Low"
    return score, category

# --- UI Layout ---
st.markdown("""
    <div style='text-align: center; padding: 1.5rem 0;'>
        <h1 style='font-size: 2.8rem;'>🌿 <span style="color:#00BFA6">XDC Green Lending AI</span></h1>
        <p style='font-size: 1.1rem;'>AI-powered due diligence for sustainable loans — assess, simulate, and monitor RWA-backed projects on the XDC blockchain.</p>
    </div>
""", unsafe_allow_html=True)


# --- Loan Proposal Form (Always visible now) ---
st.subheader("📋 Submit a New Green Loan Proposal")

with st.form("loan_proposal_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        borrower_id = st.selectbox("Borrower ID", borrower_profiles_df["borrower_id"].unique())
        loan_amount = st.number_input("Loan Amount (XDC)", 10.0, 1e7, 1000.0, step=10.0)
    with col2:
        rwa_id = st.selectbox("Collateral RWA ID", rwa_properties_df["rwa_id"].unique())
        loan_term_months = st.slider("Loan Term (Months)", 6, 120, 36)

    project_description = st.text_area("🌞 Project Description", "Developing a 5MW solar farm in a semi-arid region.", height=100)

    selected_rwa = rwa_properties_df[rwa_properties_df["rwa_id"] == rwa_id].iloc[0]
    st.markdown("##### 🌍 Expected Impact Metrics from RWA")
    st.success(f"""
        CO₂ Reduction: {selected_rwa['estimated_co2_reduction_tons_per_year']:,} tons/year
        Energy Generation: {selected_rwa['estimated_energy_generated_kwh_per_year']:,} kWh/year
        Water Savings: {selected_rwa.get('estimated_water_savings_liters_per_year', 0):,} liters/year
        Certification: {selected_rwa.get('certification_level', 'N/A')}
        Project Type: {selected_rwa.get('project_type', 'N/A').title()}
        Jobs Created: {selected_rwa.get('estimated_jobs_created', 0)} 
    """)

    submit_button = st.form_submit_button("🚀 Assess Loan & Impact")

if submit_button:
    st.balloons()
    st.header("🔎 Assessment Results")
    selected_borrower = borrower_profiles_df[borrower_profiles_df["borrower_id"] == borrower_id].iloc[0]

    # --- Financial Risk ---
    financial_risk_score, financial_risk_category = calculate_financial_risk(
        selected_borrower, loan_amount, loan_term_months
    )
    st.subheader("📉 Financial Risk Assessment")
    st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 10px;'>
        <h4>Borrower: {borrower_id}</h4>
        <p>Credit Score: {selected_borrower['credit_score']} | Default History: {selected_borrower['default_history']}</p>
        <p><b style="color:{'green' if financial_risk_category == 'Low' else 'orange' if financial_risk_category == 'Medium' else 'red'}">
        Financial Risk Category: {financial_risk_category}</b></p>
    </div>
    """, unsafe_allow_html=True)
    st.metric("📊 Financial Risk Score", f"{financial_risk_score:.2f}")

    # --- Impact Assessment & Underwriting Report ---
    loan_term_years = loan_term_months / 12
    impact_results = impact_assessor.assess_impact(project_description, selected_rwa, loan_amount, loan_term_years)
    impact_score = impact_results["impact_score"]
    impact_category = impact_results["impact_category"]
    feedback_notes = impact_results["feedback_notes"]
    underwriting_report = impact_results["underwriting_report"] 

    st.subheader("🌿 Environmental & Social Impact Assessment")
    st.metric("🪴 Green/Social Impact Score", f"{impact_score:.2f}")
    st.markdown(f"<b>Impact Category:</b> {'🌿 High' if impact_category == 'High' else '🌱 Medium' if impact_category == 'Medium' else '🍂 Low'}", unsafe_allow_html=True)
    st.progress(min(impact_score / 100, 1.0))

    st.markdown("##### Detailed Impact Feedback:")
    if feedback_notes:
        for note in feedback_notes:
            st.info(f"- {note}")
    else:
        st.info("No specific feedback notes generated.")

    # Display AI-Powered Comprehensive Underwriting Report
    st.subheader("📝 AI-Powered Comprehensive Underwriting Report (Simulated)")
    st.info("This report is generated by an AI agent, simulating a deep dive into ESG factors, risks, and recommendations for the loan.")
    with st.expander("View Full Underwriting Report"):
        st.markdown(underwriting_report)


    # --- GOAT Agent (Simulated - Crossmint GOAT SDK Integration Point) ---
    st.subheader("🤖 GOAT Agent Recommendation (Simulated)")
    st.info("This agent serves as the AI-driven layer for the Crossmint GOAT SDK integration, simulating AI-powered transaction initiation and embedded wallet management.")
    goat_response = goat_agent.analyze_and_execute(
        borrower_data=selected_borrower,
        rwa_data=selected_rwa,
        context={
            "loan_amount": loan_amount,
            "loan_term_months": loan_term_months,
            "project_description": project_description
        }
    )
    goat_insights = goat_response.get("goat_insights", {})
    st.markdown(f"Summary: {goat_insights.get('summary', 'N/A')}")
    st.markdown(f"Recommendation: {goat_insights.get('recommendation', 'N/A')}")
    st.metric("Confidence Score", f"{goat_insights.get('confidence_score', 0):.2f}")


    # --- Blockchain Call (Loan Transaction) ---
    st.subheader("⛓️ Blockchain Integration (XDC Loan Transaction)")
    st.info("This transaction records the essence of the green loan proposal on the XDC blockchain, demonstrating the RWA issuance/management capability. It uses your from_address from secrets.toml to send loan_amount tXDC to a to_address.")
    try:
        tx_hash = send_xdc_transaction(
            w3_instance=global_w3,
            private_key_str=XDC_PRIVATE_KEY,
            from_address=XDC_FROM_ADDRESS,
            to_address=XDC_TO_ADDRESS,
            amount_xdc=loan_amount
        )
        if tx_hash:
            st.success("✅ Loan proposal recorded on XDC blockchain.")
            st.code(f"Transaction Hash: {tx_hash}")
            st.markdown(f"[View Loan Transaction on XDC Explorer](https://explorer.apothem.network/tx/{tx_hash})")
        else:
            st.error("❌ Loan blockchain transaction failed: No transaction hash returned. Check console for details.")
    except Exception as e:
        st.error(f"❌ Loan blockchain transaction failed: {e}")
        tx_hash = "N/A"

    # Save submission and store latest loan for StorX and other bonus features
    new_loan_entry = {
        "loan_id": f"LOAN-{len(st.session_state.submitted_loans)+1:04d}",
        "borrower_id": borrower_id,
        "rwa_id": rwa_id,
        "financial_risk": financial_risk_category,
        "impact_category": impact_category,
        "impact_score": impact_score,
        "status": "Proposed",
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expected_co2": selected_rwa["estimated_co2_reduction_tons_per_year"],
        "expected_kwh": selected_rwa["estimated_energy_generated_kwh_per_year"],
        "expected_jobs": selected_rwa.get("estimated_jobs_created", 0), 
        "expected_water_savings": selected_rwa.get("estimated_water_savings_liters_per_year", 0),
        "underwriting_report": underwriting_report 
    }
    st.session_state.submitted_loans.append(new_loan_entry)
    st.session_state.latest_loan_for_storx = new_loan_entry # Store the latest loan for StorX and Tokenizer
    st.success("🎉 Loan proposal submitted successfully!")


# --- StorX Integration (Moved outside the initial submit_button block) ---
# This section will now appear AFTER a loan has been submitted, and persist across reruns
if st.session_state.latest_loan_for_storx: # Only show if a loan has been submitted
    latest_loan = st.session_state.latest_loan_for_storx
    loan_id_for_storx = latest_loan["loan_id"]
    
    st.markdown("---") # Visual separator
    st.subheader("☁️ StorX Integration (Decentralized Document Storage)")
    
    # Dynamic info message based on whether real credentials were provided
    if storx_agent.is_real_integration_possible:
        st.info("This uploads a summary of the latest loan proposal details to StorX for immutable, decentralized storage.")
    else:
        st.warning("⚠️ **StorX Integration is in SIMULATION MODE** because no real StorX credentials were found in `.streamlit/secrets.toml` or connection failed. To enable real integration for the bounty, please add your `access_key_id`, `secret_access_key`, `endpoint_url`, and `bucket_name` under the `[storx]` section, and ensure your Access Grant has permissions to manage the vault.")
        st.info("This simulation demonstrates the *concept* of uploading documents to StorX.")

    # Prepare content for upload
    document_content = f"""
## Loan Proposal Document for {loan_id_for_storx}

**Summary:**
This document outlines the details of the green loan proposal, including its financial and environmental impact assessments. It serves as an immutable record stored on the decentralized StorX network.

**Basic Loan Details:**
* Borrower ID: {latest_loan['borrower_id']}
* Collateral RWA ID: {latest_loan['rwa_id']}
* Submitted At: {latest_loan['submitted_at']}

**Assessment Highlights:**
* Financial Risk: {latest_loan['financial_risk']}
* Green/Social Impact Category: {latest_loan['impact_category']} (Score: {latest_loan['impact_score']:.2f})

**Expected Annual Impact Metrics:**
* CO2 Reduction: {latest_loan['expected_co2']:,} tons/year
* Energy Generation: {latest_loan['expected_kwh']:,} kWh/year
* Jobs Created: {latest_loan.get('expected_jobs', 0)}
* Water Savings: {latest_loan['expected_water_savings']:,} liters/year

---
**Full Underwriting Report:**
{latest_loan['underwriting_report']}
"""
    object_key = f"loan_proposals/{loan_id_for_storx}_{datetime.now().strftime('%Y%m%d%H%M%S')}.md" 
    
    if st.button(f"Store Loan Proposal {loan_id_for_storx} on StorX", key="storx_upload_button"): 
        print("--- StorX Button Clicked ---") 
        print(f"Attempting to upload file '{object_key}' to vault '{storx_agent.bucket_name}'") 
        
        with st.spinner("Uploading document to StorX..."):
            try: 
                upload_result = storx_agent.upload_document(
                    document_content.encode('utf-8'), # Content must be bytes
                    object_key
                )
                print(f"Upload result received: {upload_result}") 
            except Exception as e: 
                print(f"!!! CRITICAL ERROR DURING STORX UPLOAD: {e}") 
                upload_result = {"success": False, "error": f"Internal app error: {e}"} 

        if upload_result["success"]:
            st.success(f"✅ Loan proposal document successfully processed by StorX Agent!")
            st.markdown(f"**StorX URL:** [{upload_result['url']}]({upload_result['url']})")
            st.info("This demonstrates how decentralized storage enhances transparency and data integrity for RWA projects.")
        else:
            st.error(f"❌ StorX document processing failed: {upload_result['error']}")
        print("--- StorX Button Logic Finished ---") 


    # --- NEW BONUS FEATURE: Dynamic RWA Tokenization Simulation ---
    st.markdown("---")
    st.subheader("🔗 Dynamic RWA Tokenization (Simulated)")
    st.info("This agent simulates the on-chain tokenization of the Real World Asset, creating a unique, trackable digital representation.")

    if st.button(f"Simulate Tokenize RWA for {loan_id_for_storx}", key="tokenize_rwa_button"):
        with st.spinner("Simulating RWA tokenization..."):
            tokenization_result = rwa_tokenizer_agent.simulate_tokenize_rwa(latest_loan)
        
        if tokenization_result["success"]:
            st.success(f"✅ RWA Tokenization Simulated!")
            st.markdown(f"**Token Name:** `{tokenization_result['token_name']}`")
            st.markdown(f"**Token Symbol:** `{tokenization_result['token_symbol']}`")
            st.markdown(f"**Simulated Token ID:** `{tokenization_result['token_id']}`")
            st.markdown(f"**Simulated Metadata URL:** `{tokenization_result['metadata_url']}`")
            st.info("This token could represent fractional ownership or a debt instrument backed by the green asset, enabling secondary market liquidity.")
        else:
            st.error(f"❌ RWA Tokenization Simulation Failed: {tokenization_result['error']}")

    # --- NEW BONUS FEATURE: DAO Governance Simulation ---
    st.markdown("---")
    st.subheader("🗳️ DAO Governance for Loan Approval (Simulated)")
    st.info("This simulates a decentralized autonomous organization (DAO) voting on the loan proposal, demonstrating community-driven decision-making.")

    if st.button(f"Simulate DAO Vote for {loan_id_for_storx}", key="dao_vote_button"):
        with st.spinner("Simulating DAO voting process..."):
            vote_result = dao_governance_agent.simulate_vote_on_proposal(loan_id_for_storx, latest_loan)
        
        if vote_result["success"]:
            if vote_result["vote_outcome"] == "Approved":
                st.success(f"🎉 DAO Vote Outcome: {vote_result['vote_outcome']}!")
            elif vote_result["vote_outcome"] == "Rejected":
                st.error(f"🚫 DAO Vote Outcome: {vote_result['vote_outcome']}!")
            else:
                st.warning(f"⏳ DAO Vote Outcome: {vote_result['vote_outcome']}...")
            
            st.write(f"**Yes Votes:** {vote_result['yes_votes_percent']}%")
            st.write(f"**No Votes:** {vote_result['no_votes_percent']}%")
            st.write(f"**Total Voters:** {vote_result['total_voters']}")
            st.info(f"**Reason:** {vote_result['reason']}")
            st.info("This demonstrates how community governance can be integrated into the RWA lifecycle.")
        else:
            st.error(f"❌ DAO Vote Simulation Failed: {vote_result['error']}")


else:
    # This block is only shown if no loan has been submitted yet.
    # The StorX and other bonus sections will only appear after the first loan submission.
    pass


# --- Monitoring Dashboard (Enhanced with Oracle Simulation) ---
st.markdown("---")
st.header("📈 Active Loan Monitoring & Real-time Impact (Simulated Oracle)")

if st.session_state.submitted_loans:
    df = pd.DataFrame(st.session_state.submitted_loans)
    st.markdown("### 📝 Submitted Loan Proposals (PolyTrade User Onboarding/Distribution Demo)")
    st.info("This dashboard represents the 'distribution' and 'monitoring' phase of RWA. Our AI agents (Impact & Financial) facilitate 'user onboarding' by pre-assessing projects before they reach here.")
    st.data_editor(df, use_container_width=True, disabled=[
        "loan_id", "borrower_id", "rwa_id", "status",
        "expected_co2", "expected_kwh", "expected_jobs",
        "expected_water_savings", "financial_risk", "impact_category",
        "impact_score", "submitted_at", "underwriting_report" # Disable editing of report
    ])

    st.download_button("⬇️ Download CSV", df.to_csv(index=False), "loan_data.csv")

    st.subheader("🔄 Simulate Monthly Loan Progress with Oracle Data")
    monitor_loan_id = st.selectbox("Select Loan to Monitor", df["loan_id"].unique(), key="monitor_select")
    
    if st.button("Fetch Real-time Data (Simulated Oracle)", key="fetch_oracle_data_button"):
        st.session_state.current_monitoring_month += 1
        with st.spinner(f"Fetching simulated oracle data for {monitor_loan_id} (Month {st.session_state.current_monitoring_month})..."):
            oracle_data = oracle_monitor_agent.fetch_simulated_rwa_data(
                rwa_id=df[df["loan_id"] == monitor_loan_id]["rwa_id"].iloc[0],
                current_month=st.session_state.current_monitoring_month
            )
        
        if oracle_data["success"]:
            st.success(f"✅ Oracle Data Fetched for {monitor_loan_id} (Month {st.session_state.current_monitoring_month})!")
            st.write(f"**CO₂ Reduction:** {oracle_data['co2_reduction_tons']:.2f} tons")
            st.write(f"**Energy Generated:** {oracle_data['energy_generated_kwh']:.2f} kWh")
            st.write(f"**Jobs Created:** {oracle_data['jobs_created']}")
            st.write(f"**Water Savings:** {oracle_data['water_savings_liters']:.2f} liters")
            st.write(f"**Project Status Update:** {oracle_data['status_update']}")
            st.caption(f"Data as of: {oracle_data['timestamp']}")
            st.info("This demonstrates how decentralized oracles can provide verifiable, real-time project performance data for RWA monitoring.")

            # Optionally, update the loan status in the DataFrame based on oracle data
            idx = df[df["loan_id"] == monitor_loan_id].index[0]
            st.session_state.submitted_loans[idx]["status"] = f"Monitoring ({oracle_data['status_update']})"
            st.rerun() # Rerun to update the data_editor immediately
        else:
            st.error(f"❌ Simulated Oracle Data Fetch Failed: {oracle_data['error']}")

else:
    st.info("No loan proposals submitted yet.")


# --- AKKA Finance Integration ---
st.markdown("---")
st.header("⚡ AKKA Finance Integration: RWA Liquidity & Trading")
st.markdown("""
    <p>This section demonstrates how our AI agents would leverage AKKA Finance's liquidity aggregation
    to optimize trading and manage Real World Asset (RWA) tokens on the XDC Network.</p>
    <p>Imagine your green loan has been successfully tokenized. You can now use this agent to simulate
    finding the best liquidity for trading or collateralization.</p>
""", unsafe_allow_html=True)

with st.expander("Simulate RWA Token Liquidity Optimization"):
    st.info("Note: This feature simulates the integration with AKKA Finance principles. Actual tokenization and live liquidity pools are beyond the scope of this hackathon demo, but the logic shows how our AI would interact.")

    # Placeholder for RWA Token Address (assuming a tokenized green loan)
    rwa_token_mock_address = st.text_input(
        "RWA Token Contract Address (Simulated)",
        "0xFakeRWAContractAddress1234567890abcdef1234567890abcdef",
        key="akka_rwa_address"
    )
    amount_to_trade_rwa = st.number_input("Amount of RWA Token to Trade (Simulated)", 1.0, 1000000.0, 100.0, step=1.0, key="akka_amount")
    preferred_output_asset = st.selectbox("Preferred Output Asset", ["XDC", "tUSDT", "tUSDC"], key="akka_output_asset")
    max_risk_tolerance = st.slider("Max Risk Tolerance (1=Low, 5=High)", 1, 5, 3, key="akka_risk")

    if st.button("Optimize Liquidity Route via AKKA Agent", key="akka_optimize_button"):
        st.subheader("AKKA Agent's Optimization Results:")
        optimization_results = akka_liquidity_agent.optimize_liquidity_route(
            rwa_token_mock_address,
            amount_to_trade_rwa,
            preferred_output_asset,
            max_risk_tolerance
        )

        if optimization_results["route_found"]:
            details = optimization_results["optimization_details"]
            st.success(f"✅ Optimal Liquidity Route Found!")
            st.write(f"*Selected Pool:* {details['selected_pool']}")
            st.write(f"*Via Simulated DEX:* {details['via_dex']}")
            st.write(f"*Liquidity Depth:* {details['liquidity_depth']:,}")
            st.write(f"*Estimated Fees:* {details['estimated_fees_percent']:.2f}%")
            st.write(f"*Risk Score:* {details['risk_score']:.2f}")
            st.write(f"*Simulated Slippage:* {optimization_results['simulated_slippage_percent']:.2f}%")
            st.write(f"*Simulated Gas Cost:* {optimization_results['simulated_gas_cost_xdc']:.4f} tXDC")

            # Store results in session state to persist for next button click
            st.session_state["akka_optimization_results"] = optimization_results
            st.session_state["akka_trade_rwa_amount"] = amount_to_trade_rwa
            st.session_state["akka_trade_output_asset"] = preferred_output_asset

        else:
            st.warning("No suitable liquidity route found based on your criteria.")
            # Display error message if available from the agent
            if "error_message" in optimization_results:
                st.error(optimization_results["error_message"])
            st.session_state["akka_optimization_results"] = None # Reset if no route found

    # Ensure this button only appears if optimization results exist AND a route was found
    if st.session_state.get("akka_optimization_results") and st.session_state["akka_optimization_results"]["route_found"]:
        if st.button("Simulate Trade Execution", key="akka_execute_button"):
            st.subheader("Simulating Trade Execution...")
            optimization_results = st.session_state["akka_optimization_results"]
            amount_to_trade_rwa = st.session_state["akka_trade_rwa_amount"]
            preferred_output_asset = st.session_state["akka_trade_output_asset"]

            trade_execution_results = akka_liquidity_agent.simulate_execute_trade(
                optimized_route_details=optimization_results,
                amount_rwa=amount_to_trade_rwa,
                preferred_output_asset=preferred_output_asset
            )

            if trade_execution_results["trade_executed"]:
                st.success(f"🚀 Simulated trade executed successfully!")
                st.code(f"Simulated Transaction Hash: {trade_execution_results['simulated_tx_hash']}")
                st.write(f"Amount of {preferred_output_asset} Received: {trade_execution_results['output_amount_received']:.4f}")
                st.info("This demonstrates how an AI agent would use AKKA Finance to manage RWA liquidity post-tokenization.")
            else:
                st.error("❌ Simulated trade execution failed.")
                if "error_message" in trade_execution_results:
                    st.error(trade_execution_results["error_message"])


st.markdown("""
---
<center>
    Built for the <b>XDC Green Finance Hackathon</b> 💚<br>
    Powered by <a href='https://xdc.org' target='_blank'>XDC Network</a> | Made with ❤️ and Streamlit
</center>
""", unsafe_allow_html=True)
