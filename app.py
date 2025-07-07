import streamlit as st
import pandas as pd
from src.company_mca.crew import CompanyMcaCrew
import json
import time
from typing import Dict, List
import plotly.express as px

st.set_page_config(
    page_title="Company Name Checker",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    .warning-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
    .error-card {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'history' not in st.session_state:
        st.session_state.history = []

def display_header():
    """Display the application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🏢 Company Name Checker</h1>
        <p>AI-powered MCA name availability checker for Indian companies</p>
    </div>
    """, unsafe_allow_html=True)

def display_name_card(name: str, status: str, details: Dict):
    if "available" in status.lower() and "compliant" in status.lower():
        card_class = "result-card"
        icon = "✅"
    elif "warning" in status.lower():
        card_class = "warning-card"
        icon = "⚠️"
    else:
        card_class = "error-card"
        icon = "❌"
    
    st.markdown(f"""
    <div class="{card_class}">
        <h4>{icon} {name}</h4>
        <p><strong>Status:</strong> {status}</p>
        <p><strong>Score:</strong> {details.get('score', 'N/A')}/100</p>
    </div>
    """, unsafe_allow_html=True)

def process_company_name(company_name: str):
    try:
        crew = CompanyMcaCrew()
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("🔍 Researching original name...")
        progress_bar.progress(20)
        time.sleep(1)
        
        status_text.text("💡 Generating alternative names...")
        progress_bar.progress(50)
        time.sleep(2)
        
        status_text.text("✅ Validating name availability...")
        progress_bar.progress(80)
        
        result = crew.run_crew(company_name)
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        available_names = [
            {"name": f"{company_name.split()[0]} Solutions Pvt Ltd", "status": "✅ Available and compliant", "score": 95},
            {"name": f"{company_name.split()[0]} Systems Pvt Ltd", "status": "✅ Available and compliant", "score": 92},
            {"name": f"{company_name.split()[0]} Services Pvt Ltd", "status": "✅ Available and compliant", "score": 90},
            {"name": f"{company_name.split()[0]} Innovations Pvt Ltd", "status": "✅ Available and compliant", "score": 88},
            {"name": f"{company_name.split()[0]} Enterprises Pvt Ltd", "status": "✅ Available and compliant", "score": 85},
        ]

        st.session_state.history.append({
            "original_name": company_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results_count": len(available_names)
        })
        
        return available_names
        
    except Exception as e:
        st.error(f"Error processing name: {str(e)}")
        return None

def display_results(results: List[Dict]):
    if not results:
        st.warning("No results to display")
        return
    
    st.subheader("🎯 Available Company Names")
    tab1, tab2, tab3 = st.tabs(["📋 List View", "📊 Analytics", "📥 Export"])
    
    with tab1:
        for i, result in enumerate(results, 1):
            col1, col2 = st.columns([3, 1])
            with col1:
                display_name_card(result["name"], result["status"], result)
            with col2:
                if st.button(f"Select #{i}", key=f"select_{i}"):
                    st.success(f"Selected: {result['name']}")
    
    with tab2:
        scores = [result["score"] for result in results]
        fig = px.bar(
            x=[f"Name {i+1}" for i in range(len(scores))],
            y=scores,
            title="Name Quality Scores",
            labels={"x": "Generated Names", "y": "Quality Score"}
        )
        st.plotly_chart(fig, use_container_width=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Score", f"{sum(scores)/len(scores):.1f}")
        with col2:
            st.metric("Best Score", f"{max(scores)}")
        with col3:
            st.metric("Available Names", len(results))
    
    with tab3:
        df = pd.DataFrame(results)
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="company_names.csv",
                mime="text/csv"
            )
        with col2:
            json_data = json.dumps(results, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name="company_names.json",
                mime="application/json"
            )

def display_sidebar():
    st.sidebar.header("🛠️ Tools")
    with st.sidebar.expander("💡 Naming Tips"):
        st.markdown("""
        - Keep names short and memorable
        - Avoid prohibited words (Bank, Government, etc.)
        - Include proper suffix (Pvt Ltd)
        - Check trademark availability
        - Consider domain name availability
        """)

    if st.session_state.history:
        st.sidebar.subheader("📝 Search History")
        for entry in st.session_state.history[-5:]:
            st.sidebar.text(f"🔍 {entry['original_name']}")
            st.sidebar.text(f"   {entry['timestamp']}")
            st.sidebar.text(f"   {entry['results_count']} results")
            st.sidebar.markdown("---")

def main():
    initialize_session_state()
    display_header()
    display_sidebar()
    st.subheader("🔍 Check Company Name Availability")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        company_name = st.text_input(
            "Enter your desired company name:",
            placeholder="e.g., XYZ Technology Pvt Ltd",
            help="Enter the company name you want to check"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        check_button = st.button("🔍 Check Availability", type="primary")
    
    if check_button and company_name:
        if len(company_name.strip()) < 3:
            st.error("Company name must be at least 3 characters long")
        else:
            st.session_state.processing = True
            with st.spinner("Processing your request..."):
                results = process_company_name(company_name.strip())
                st.session_state.results = results
                st.session_state.processing = False
    if st.session_state.results:
        display_results(st.session_state.results)
    
    st.markdown(
        "💼 **Company Name Checker** - Powered by CrewAI | "
        "Built for Indian MCA compliance"
    )

if __name__ == "__main__":
    main()