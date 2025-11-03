# src/dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

st.set_page_config(page_title="Secure RAG System", layout="wide")

st.title("🔐 Secure Enterprise RAG System")
st.subheader("Powered by LIST AI Research")

# Sidebar authentication
st.sidebar.header("Authentication")
api_token = st.sidebar.text_input("API Token", type="password")

if not api_token:
    st.warning("Please provide API token in sidebar")
    st.stop()

# Main sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Query Interface", 
    "Security Dashboard",
    "Compliance & Audit",
    "Energy Metrics",
    "System Health"
])

with tab1:
    st.subheader("📝 Query Interface")
    
    query = st.text_area("Enter your query:", height=100)
    col1, col2 = st.columns(2)
    
    with col1:
        top_k = st.slider("Number of results", 1, 10, 5)
    
    with col2:
        submit = st.button("Execute Query")
    
    if submit and query:
        # Call API
        headers = {"Authorization": f"Bearer {api_token}"}
        response = requests.post(
            "http://localhost:8000/query",
            json={"query": query, "top_k": top_k},
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            st.success("Query executed successfully")
            
            st.write(f"**Response:** {result['response']}")
            st.write(f"**Confidence:** {result['confidence']:.2%}")
            st.write(f"**Execution Time:** {result['execution_time_ms']:.0f}ms")
            
            # Sources
            st.subheader("📚 Sources")
            for source in result['sources']:
                st.write(f"- {source}")
        else:
            st.error(f"Query failed: {response.text}")

with tab2:
    st.subheader("🛡️ Security Dashboard")
    
    # Threat indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Threats Blocked", "12", "+2")
    
    with col2:
        st.metric("Rate Limit Hits", "3", "0")
    
    with col3:
        st.metric("Invalid Queries", "7", "+1")
    
    with col4:
        st.metric("Adversarial Attempts", "2", "0")
    
    # Recent events
    st.subheader("Recent Security Events")
    events_data = {
        'Timestamp': ['2025-11-03 18:00', '2025-11-03 17:55', '2025-11-03 17:50'],
        'Type': ['QUERY_BLOCKED', 'RATE_LIMIT', 'ADVERSARIAL_DETECTED'],
        'Severity': ['MEDIUM', 'LOW', 'HIGH'],
        'User': ['user_123', 'user_456', 'user_789']
    }
    st.dataframe(pd.DataFrame(events_data))

with tab3:
    st.subheader("📋 Compliance & Audit")
    
    # GDPR compliance
    st.write("### GDPR Compliance")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Data Access Logs", "1,234")
        st.metric("Deletion Requests", "12")
    
    with col2:
        st.metric("Audit Trail Entries", "5,678")
        st.metric("Explainability Score", "96%")
    
    # Explainability
    st.write("### Model Explainability")
    explainability_score = {
        'Transparency': 0.95,
        'Auditability': 0.92,
        'Fairness': 0.88,
        'Privacy': 0.90
    }
    
    fig = go.Figure(data=[
        go.Bar(x=list(explainability_score.keys()),
               y=list(explainability_score.values()),
               marker_color='lightblue')
    ])
    st.plotly_chart(fig)

with tab4:
    st.subheader("⚡ Energy & Carbon Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Queries", "2,450")
    
    with col2:
        st.metric("Energy Used (kWh)", "12.5")
    
    with col3:
        st.metric("CO2 Emissions (kg)", "5.0")
    
    with col4:
        st.metric("Avg Energy/Query (mJ)", "5.1")
    
    # Energy trend
    st.write("### Energy Consumption Trend")
    dates = pd.date_range('2025-11-01', periods=30, freq='D')
    energy = [10 + i*0.2 for i in range(30)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=energy, mode='lines', name='Energy (kWh)'))
    st.plotly_chart(fig)

with tab5:
    st.subheader("🏥 System Health")
    
    # API status
    st.write("### API Status")
    st.metric("Uptime", "99.9%")
    st.metric("Response Time (avg)", "245ms")
    st.metric("Error Rate", "0.1%")
    
    # Database
    st.write("### Database Status")
    st.metric("Documents Stored", "15,234")
    st.metric("Vector DB Size (GB)", "4.2")
    st.metric("Query Cache Hit Rate", "73%")

st.sidebar.markdown("---")
st.sidebar.markdown("Built for LIST Luxembourg SnT")
st.sidebar.markdown("Secure RAG System v1.0")
