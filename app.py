import streamlit as st
import pandas as pd
from src.company_mca.crew import CompanyMcaCrew
from src.company_mca.tools.custom_tool import mca_name_checker
import json
import time
from typing import Dict, List
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="MCA Company Name Checker",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏢"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .result-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .warning-card {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .error-card {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'selected_name' not in st.session_state:
        st.session_state.selected_name = None

def display_header():
    st.markdown("""
    <div class="main-header">
        <h1>🏢 MCA Company Name Checker</h1>
        <p>AI-powered name availability checker using real MCA data via Finanvo API</p>
        <small>Validate company names against Indian MCA database</small>
    </div>
    """, unsafe_allow_html=True)

def display_name_card(name: str, status: str, details: Dict, index: int):
    score = details.get('score', 0)
    
    if "available" in status.lower() and "compliant" in status.lower():
        card_class = "result-card"
        icon = "✅"
    elif "warning" in status.lower() or "minor issues" in status.lower():
        card_class = "warning-card"
        icon = "⚠️"
    else:
        card_class = "error-card"
        icon = "❌"
    
    st.markdown(f"""
    <div class="{card_class}">
        <h4>{icon} {name}</h4>
        <p><strong>Status:</strong> {status}</p>
        <p><strong>Compliance Score:</strong> {score}/100</p>
        <p><strong>Validation:</strong> {details.get('validation_summary', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    return score

def check_single_name(company_name: str) -> Dict:
    try:
        with st.spinner(f"Checking '{company_name}'..."):
            result = mca_name_checker._run(company_name)
            
            if "error" in result:
                return {
                    "name": company_name,
                    "status": f"❌ Error: {result['error']}",
                    "score": 0,
                    "validation_summary": "Check failed",
                    "details": result
                }

            validation = result.get('validation', {})
            recommendation = result.get('recommendation', 'Unknown status')
            
            return {
                "name": company_name,
                "status": recommendation,
                "score": validation.get('score', 0),
                "validation_summary": f"{len(validation.get('errors', []))} errors, {len(validation.get('warnings', []))} warnings",
                "details": result
            }
            
    except Exception as e:
        return {
            "name": company_name,
            "status": f"❌ Error: {str(e)}",
            "score": 0,
            "validation_summary": "Check failed",
            "details": {"error": str(e)}
        }

def generate_alternative_names(base_name: str, count: int = 5) -> List[str]:
    base_clean = base_name.lower().replace('pvt ltd', '').replace('private limited', '').replace('ltd', '').strip()
    suffixes = ['Solutions Pvt Ltd', 'Systems Pvt Ltd', 'Services Pvt Ltd', 'Technologies Pvt Ltd', 'Innovations Pvt Ltd']

    alternatives = []
    words = base_clean.split()
    
    if len(words) > 0:
        first_word = words[0].title()
        
        # Add suffix variations
        for suffix in suffixes[:count]:
            alternatives.append(f"{first_word} {suffix}")
    
    return alternatives

def process_company_names(original_name: str, check_alternatives: bool = True):
    results = []
    st.write("🔍 **Checking original name...**")
    original_result = check_single_name(original_name)
    results.append(original_result)
    if check_alternatives:
        st.write("💡 **Generating and checking alternatives...**")
        alternatives = generate_alternative_names(original_name)
        
        progress_bar = st.progress(0)
        for i, alt_name in enumerate(alternatives):
            result = check_single_name(alt_name)
            results.append(result)
            progress_bar.progress((i + 1) / len(alternatives))

    st.session_state.history.append({
        "original_name": original_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "results_count": len(results),
        "best_score": max([r["score"] for r in results])
    })
    
    return results

def display_results(results: List[Dict]):
    if not results:
        st.warning("No results to display")
        return
    
    st.subheader("📊 Results Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    scores = [r["score"] for r in results]
    available_count = sum(1 for r in results if "available" in r["status"].lower())
    
    with col1:
        st.metric("Total Checked", len(results))
    with col2:
        st.metric("Available Names", available_count)
    with col3:
        st.metric("Average Score", f"{sum(scores)/len(scores):.1f}")
    with col4:
        st.metric("Best Score", f"{max(scores)}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Detailed Results", "📈 Score Analysis", "⚠️ Issues Summary", "📥 Export Data"])
    
    with tab1:
        st.write("### Name Availability Results")
        for i, result in enumerate(results):
            col1, col2 = st.columns([4, 1])
            with col1:
                display_name_card(result["name"], result["status"], result, i)
            with col2:
                st.write("")
                if st.button(f"View Details", key=f"details_{i}"):
                    st.session_state.selected_name = result
                
                if "available" in result["status"].lower():
                    if st.button(f"Select Name", key=f"select_{i}", type="primary"):
                        st.success(f"✅ Selected: {result['name']}")
                        st.balloons()
    
    with tab2:
        st.write("### Score Distribution")
        fig = px.bar(
            x=[f"Name {i+1}" for i in range(len(results))],
            y=scores,
            title="Company Name Compliance Scores",
            labels={"x": "Names", "y": "Score (0-100)"},
            color=scores,
            color_continuous_scale="RdYlGn"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("**Score Interpretation:**")
        st.write("- 90-100: Excellent compliance")
        st.write("- 70-89: Good with minor issues")
        st.write("- 50-69: Moderate issues")
        st.write("- Below 50: Significant problems")
    
    with tab3:
        st.write("### Common Issues Found")
        all_errors = []
        all_warnings = []
        
        for result in results:
            details = result.get("details", {})
            validation = details.get("validation", {})
            all_errors.extend(validation.get("errors", []))
            all_warnings.extend(validation.get("warnings", []))
        
        if all_errors:
            st.error(f"**Errors found ({len(all_errors)} total):**")
            for error in set(all_errors):
                st.write(f"- {error}")
        
        if all_warnings:
            st.warning(f"**Warnings found ({len(all_warnings)} total):**")
            for warning in set(all_warnings):
                st.write(f"- {warning}")
        
        if not all_errors and not all_warnings:
            st.success("No major issues found!")
    
    with tab4:
        st.write("### Export Results")
        df = pd.DataFrame([
            {
                "Name": r["name"],
                "Status": r["status"],
                "Score": r["score"],
                "Validation": r["validation_summary"]
            }
            for r in results
        ])
        
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"company_names_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            json_data = json.dumps(results, indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_data,
                file_name=f"company_names_{time.strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def display_sidebar():
    st.sidebar.header("🛠️ Tools & Info")
    with st.sidebar.expander("📋 MCA Naming Guidelines"):
        st.markdown("""
        **Required:**
        - Minimum 3 characters
        - Maximum 120 characters
        - Proper suffix (Pvt Ltd/Limited)
        
        **Prohibited:**
        - Bank, Insurance, Government
        - Ministry, National, Central
        - Starting with numbers
        
        **Recommendations:**
        - Keep it simple and memorable
        - Avoid special characters
        - Check trademark availability
        """)

    with st.sidebar.expander("🔌 API Status"):
        st.write("**Finanvo API:** Connected ✅")
        st.write("**Last Updated:** Real-time")
        st.write("**Data Source:** MCA Database")
    
    if st.session_state.history:
        st.sidebar.subheader("📈 Recent Searches")
        for i, entry in enumerate(st.session_state.history[-3:]):
            with st.sidebar.expander(f"Search {len(st.session_state.history) - i}"):
                st.write(f"**Name:** {entry['original_name']}")
                st.write(f"**Time:** {entry['timestamp']}")
                st.write(f"**Results:** {entry['results_count']}")
                st.write(f"**Best Score:** {entry['best_score']}")

def main():
    initialize_session_state()
    display_header()
    display_sidebar()

    st.subheader("🔍 Company Name Availability Checker")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        company_name = st.text_input(
            "Enter your desired company name:",
            placeholder="e.g., Tech Innovations Pvt Ltd",
            help="Enter the company name you want to check for availability"
        )
    
    with col2:
        st.write("")
        check_alternatives = st.checkbox("Generate alternatives", value=True)
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        if st.button("🔍 Check Name", type="primary"):
            if company_name and len(company_name.strip()) >= 3:
                st.session_state.processing = True
                results = process_company_names(company_name.strip(), check_alternatives)
                st.session_state.results = results
                st.session_state.processing = False
            else:
                st.error("Please enter a valid company name (minimum 3 characters)")
    
    with col2:
        if st.button("🔄 Clear Results"):
            st.session_state.results = None
            st.session_state.selected_name = None
            st.rerun()
    
    with col3:
        if st.button("📊 View History"):
            if st.session_state.history:
                st.write("### Search History")
                history_df = pd.DataFrame(st.session_state.history)
                st.dataframe(history_df, use_container_width=True)
            else:
                st.info("No search history available")
    if st.session_state.results:
        st.markdown("---")
        display_results(st.session_state.results)
    if st.session_state.selected_name:
        st.markdown("---")
        st.subheader("📋 Detailed Analysis")
        selected = st.session_state.selected_name
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Name:** " + selected["name"])
            st.write("**Status:** " + selected["status"])
            st.write("**Score:** " + str(selected["score"]) + "/100")
        
        with col2:
            details = selected.get("details", {})
            validation = details.get("validation", {})
            
            if validation.get("errors"):
                st.error("**Errors:**")
                for error in validation["errors"]:
                    st.write(f"- {error}")
            
            if validation.get("warnings"):
                st.warning("**Warnings:**")
                for warning in validation["warnings"]:
                    st.write(f"- {warning}")
    st.markdown("---")
    st.markdown(
        "🏢 **MCA Company Name Checker** | "
        "Powered by Finanvo API & CrewAI | "
        "Real-time MCA database access"
    )

if __name__ == "__main__":
    main()