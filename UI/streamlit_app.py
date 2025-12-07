import streamlit as st
import requests
import json
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Agent Admin & Test", layout="wide")

st.title("Customer Service Agent - Test Dashboard")

tabs = st.tabs(["💬 Chat Test", "📚 Knowledge Base", "🧠 Memory Inspector"])

# --- Tab 1: Chat Test ---
with tabs[0]:
    st.header("Test Chat Interface")
    
    col1, col2 = st.columns(2)
    with col1:
        user_id = st.text_input("User ID", value="test_user_1")
    with col2:
        channel = st.selectbox("Channel Simulation", ["web", "whatsapp", "telegram"])

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call API
        with st.spinner("Agent is thinking..."):
            try:
                payload = {
                    "user_id": user_id,
                    "text": prompt,
                    "metadata": {"source": "streamlit"}
                }
                response = requests.post(f"{API_URL}/v1/chat/{channel}", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    # Handle different channel response formats if basic
                    # WebAdapter returns schema with 'text'
                    bot_text = data.get("text", str(data))
                    if isinstance(data, dict) and "Body" in data: # WA
                        bot_text = data["Body"]
                    
                    st.session_state.messages.append({"role": "assistant", "content": bot_text})
                    with st.chat_message("assistant"):
                        st.markdown(bot_text)
                    
                    # Show debug
                    with st.expander("Debug Response"):
                        st.json(data)
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- Tab 2: Knowledge Base ---
with tabs[1]:
    st.header("Knowledge Base Management")
    
    domain = st.selectbox("Select Domain", ["faq", "policy", "product_docs"], key="kb_domain")
    
    st.divider()
    
    # Ingestion Section
    st.subheader("Add Content")
    ingestion_mode = st.radio("Ingestion Method", ["File Upload", "Manual Text Entry"], horizontal=True)
    
    if ingestion_mode == "File Upload":
        st.info("Upload files (PDF, HTML, etc.) to ingest using Docling.")
        uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
        
        if st.button("Process & Ingest Files"):
            if not uploaded_files:
                st.warning("Please upload files first.")
            else:
                with st.spinner(f"Ingesting {len(uploaded_files)} files..."):
                    try:
                        files_payload = [
                            ("files", (file.name, file, file.type)) for file in uploaded_files
                        ]
                        data_payload = {"domain": domain}
                        
                        res = requests.post(
                            f"{API_URL}/admin/ingest/files", 
                            files=files_payload, 
                            data=data_payload
                        )
                        
                        if res.status_code == 200:
                            result = res.json()
                            st.success(f"Processing Complete! Total chunks: {result.get('total_processed', 'N/A')}")
                            st.json(result.get('details', result))
                        else:
                            st.error(f"Error: {res.status_code} - {res.text}")
                            
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

    else: # Manual Text Entry
        with st.form("add_doc_form"):
            new_text = st.text_area("Document Content")
            new_meta = st.text_input("Metadata (JSON)", value="{}")
            submitted = st.form_submit_button("Ingest Document")
            
            if submitted and new_text:
                try:
                    meta_dict = json.loads(new_meta)
                    payload = {
                        "domain": domain,
                        "texts": [new_text],
                        "metadatas": [meta_dict]
                    }
                    res = requests.post(f"{API_URL}/admin/vectorstore/ingest", json=payload)
                    if res.status_code == 200:
                        st.success(f"Ingested: {res.json()}")
                    else:
                        st.error(res.text)
                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()
    
    # Search Section
    st.subheader("Search Vector Store")
    search_query = st.text_input("Search Query")
    if st.button("Search"):
        try:
            payload = {"domain": domain, "query": search_query, "top_k": 3}
            res = requests.post(f"{API_URL}/admin/vectorstore/search", json=payload)
            if res.status_code == 200:
                results = res.json()
                for doc in results:
                    st.info(doc["content"])
                    st.caption(f"Metadata: {doc['metadata']}")
            else:
                st.error(res.text)
        except Exception as e:
            st.error(str(e))

# --- Tab 3: Memory Inspector ---
with tabs[2]:
    st.header("Memory Inspector")
    st.write("To implement: call memory controller endpoint if exposed.")
    st.info("Currently memory is handled internally by Mem0. Use the chat to test memory recall.")
