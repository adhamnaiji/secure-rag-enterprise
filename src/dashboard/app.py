import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# ===== PAGE CONFIG =====
st.set_page_config(page_title="Secure RAG System", layout="wide")

# ===== CONFIGURATION =====
API_BASE_URL = "http://localhost:8000"
API_TOKEN = "test-token"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

st.title("🔐 Secure Enterprise RAG System")
st.subheader("Powered by Perplexity LLM + HuggingFace Embeddings")

# ===== SIDEBAR =====
st.sidebar.header("⚙️ Configuration")
api_url = st.sidebar.text_input("API URL", value=API_BASE_URL)
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# ===== TABS =====
tab1, tab2, tab3 = st.tabs(["🔍 Query", "🛡️ Security", "📊 System Health"])

# ===== TAB 1: QUERY INTERFACE =====
with tab1:
    st.subheader("Ask Questions About Your Documents")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_area("Enter your query:", height=100, placeholder="Ask anything about your uploaded documents...")
    with col2:
        top_k = st.slider("Results", 1, 10, 5)
        submit = st.button("🚀 Execute", use_container_width=True)
    
    if submit and query:
        with st.spinner("🔄 Processing query..."):
            try:
                response = requests.post(
                    f"{api_url}/query",
                    json={"query": query, "top_k": top_k},
                    headers=HEADERS,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✅ Query executed successfully!")
                    
                    # Display response
                    st.write("**Response:**")
                    st.write(result.get('response', 'No response'))
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Confidence", f"{result.get('confidence', 0):.0%}")
                    with col2:
                        st.metric("Time", f"{result.get('execution_time_ms', 0):.0f}ms")
                    with col3:
                        st.metric("Sources", len(result.get('sources', [])))
                else:
                    st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")

# ===== TAB 2: SECURITY DASHBOARD =====
with tab2:
    st.subheader("🛡️ Security Metrics")
    
    try:
        response = requests.get(f"{api_url}/security-stats", headers=HEADERS, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('metrics', {})
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🚨 Blocked", metrics.get('blocked_queries', 0))
            with col2:
                st.metric("⏱️ Rate Limited", metrics.get('rate_limit_hits', 0))
            with col3:
                st.metric("❌ Invalid", metrics.get('invalid_queries', 0))
            with col4:
                st.metric("🎯 Adversarial", metrics.get('adversarial_attempts', 0))
            
            st.write("---")
            
            # Recent events
            st.subheader("Recent Events")
            events = data.get('recent_events', [])
            
            if events:
                events_data = []
                for event in events[-10:]:
                    events_data.append({
                        "Time": event.get('timestamp', '')[-8:],
                        "Type": event.get('type', ''),
                        "Severity": event.get('severity', ''),
                    })
                
                if events_data:
                    df = pd.DataFrame(events_data)
                    st.dataframe(df, use_container_width=True)
            else:
                st.info("✅ No security events")
        else:
            st.error("❌ Failed to fetch security stats")
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")

# ===== TAB 3: SYSTEM HEALTH =====
with tab3:
    st.subheader("🏥 System Health")
    
    try:
        response = requests.get(f"{api_url}/health", headers=HEADERS, timeout=5)
        
        if response.status_code == 200:
            health = response.json()
            
            st.metric("Status", "✅ Online" if health.get('status') == 'operational' else "❌ Offline")
            st.metric("LLM", "✅ Ready" if health.get('llm_initialized') else "❌ Error")
            st.metric("Version", health.get('version', 'Unknown'))
        else:
            st.error("❌ API is offline")
    except Exception as e:
        st.error(f"❌ Cannot connect to API: {str(e)}\n\nMake sure to run: `uvicorn src.api.main:app --reload`")

# ===== FOOTER =====
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Quick Links")
st.sidebar.markdown(f"🔌 [API Status]({api_url}/health)")
st.sidebar.markdown("📚 Made with Perplexity + HuggingFace")