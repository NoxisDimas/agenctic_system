import streamlit as st
import requests
import json
import os
import time
from datetime import datetime

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
LIGHTRAG_URL = os.getenv("LIGHTRAG_API_URL", "http://localhost:9621")

st.set_page_config(page_title="Agent Admin & Test", layout="wide")

st.title("🤖 Customer Service Agent - Dashboard")

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
                    bot_text = data.get("text", str(data))
                    if isinstance(data, dict) and "Body" in data:
                        bot_text = data["Body"]
                    
                    st.session_state.messages.append({"role": "assistant", "content": bot_text})
                    with st.chat_message("assistant"):
                        st.markdown(bot_text)
                    
                    with st.expander("Debug Response"):
                        st.json(data)
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- Tab 2: Knowledge Base ---
with tabs[1]:
    st.header("📚 Knowledge Base Management")
    
    # Sub-navigation
    kb_menu = st.radio(
        "Select Action",
        ["📤 Upload Documents", "📋 Document List", "🔍 Query Knowledge", "🕸️ Graph Explorer", "⚙️ Settings"],
        horizontal=True
    )
    
    st.divider()
    
    # ============ UPLOAD DOCUMENTS ============
    if kb_menu == "📤 Upload Documents":
        upload_method = st.radio("Method", ["File Upload", "Text Input"], horizontal=True)
        
        if upload_method == "File Upload":
            st.subheader("Upload Files to LightRAG")
            uploaded_files = st.file_uploader(
                "Choose files (PDF, TXT, MD, DOCX)", 
                type=["pdf", "txt", "md", "docx", "html"],
                accept_multiple_files=True,
                help="Files will be processed by LightRAG and indexed into the knowledge graph"
            )
            
            if uploaded_files and st.button("📤 Upload & Process", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                results_container = st.container()
                
                total_files = len(uploaded_files)
                success_count = 0
                
                for i, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Uploading {i+1}/{total_files}: {uploaded_file.name}...")
                    progress_bar.progress((i) / total_files)
                    
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        res = requests.post(f"{LIGHTRAG_URL}/documents/upload", files=files)
                        
                        if res.status_code == 200:
                            result = res.json()
                            success_count += 1
                            with results_container:
                                st.success(f"✅ {uploaded_file.name}: {result.get('message', 'Uploaded')}")
                                if result.get("track_id"):
                                    st.caption(f"Track ID: `{result['track_id']}`")
                        else:
                            with results_container:
                                st.error(f"❌ {uploaded_file.name}: {res.status_code} - {res.text}")
                    except Exception as e:
                        with results_container:
                            st.error(f"❌ {uploaded_file.name}: {e}")
                
                progress_bar.progress(1.0)
                status_text.text(f"Complete! {success_count}/{total_files} files uploaded successfully.")
        
        else:  # Text Input
            st.subheader("Insert Text Directly")
            with st.form("insert_text_form"):
                text_content = st.text_area(
                    "Text Content",
                    height=200,
                    placeholder="Paste or type the text you want to add to the knowledge base..."
                )
                file_source = st.text_input(
                    "Source (optional)", 
                    placeholder="e.g., FAQ document, Policy v2.0"
                )
                
                submitted = st.form_submit_button("📝 Insert Text", type="primary")
                
                if submitted and text_content:
                    with st.spinner("Inserting text..."):
                        try:
                            payload = {"text": text_content}
                            if file_source:
                                payload["file_source"] = file_source
                            
                            res = requests.post(f"{LIGHTRAG_URL}/documents/text", json=payload)
                            
                            if res.status_code == 200:
                                result = res.json()
                                st.success(f"✅ {result.get('message', 'Text inserted!')}")
                                if result.get("track_id"):
                                    st.info(f"📍 Track ID: `{result['track_id']}`")
                            else:
                                st.error(f"Error: {res.status_code} - {res.text}")
                        except Exception as e:
                            st.error(f"Connection Error: {e}")
    
    # ============ DOCUMENT LIST ============
    elif kb_menu == "📋 Document List":
        st.subheader("Documents in Knowledge Base")
        
        # Pipeline Status
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Get pipeline status
        try:
            pipeline_res = requests.get(f"{LIGHTRAG_URL}/documents/pipeline_status", timeout=5)
            if pipeline_res.status_code == 200:
                pipeline = pipeline_res.json()
                if pipeline.get("busy"):
                    st.warning(f"⏳ Pipeline busy: {pipeline.get('job_name', 'Processing')} - Batch {pipeline.get('cur_batch', 0)}/{pipeline.get('batchs', 0)}")
                    if pipeline.get("latest_message"):
                        st.caption(f"Latest: {pipeline['latest_message']}")
        except:
            pass
        
        # Document status counts
        try:
            counts_res = requests.get(f"{LIGHTRAG_URL}/documents/status_counts", timeout=5)
            if counts_res.status_code == 200:
                counts = counts_res.json().get("status_counts", {})
                cols = st.columns(5)
                status_colors = {
                    "pending": "🟡",
                    "processing": "🔵", 
                    "preprocessed": "🟠",
                    "processed": "🟢",
                    "failed": "🔴"
                }
                for i, (status, count) in enumerate(counts.items()):
                    with cols[i % 5]:
                        emoji = status_colors.get(status.lower(), "⚪")
                        st.metric(f"{emoji} {status}", count)
        except:
            pass
        
        st.divider()
        
        # Filter and fetch documents
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "pending", "processing", "preprocessed", "processed", "failed"]
        )
        
        try:
            payload = {"page": 1, "page_size": 50, "sort_field": "updated_at", "sort_direction": "desc"}
            if status_filter != "All":
                payload["status_filter"] = status_filter
            
            docs_res = requests.post(f"{LIGHTRAG_URL}/documents/paginated", json=payload, timeout=10)
            
            if docs_res.status_code == 200:
                docs_data = docs_res.json()
                documents = docs_data.get("documents", [])
                
                if documents:
                    for doc in documents:
                        status = doc.get("status", "unknown")
                        status_emoji = status_colors.get(status.lower(), "⚪")
                        
                        with st.expander(f"{status_emoji} {doc.get('file_path', doc.get('id', 'Unknown'))}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"**ID:** `{doc.get('id', 'N/A')}`")
                                st.write(f"**Status:** {status}")
                            with col2:
                                st.write(f"**Chunks:** {doc.get('chunks_count', 'N/A')}")
                                st.write(f"**Length:** {doc.get('content_length', 0):,} chars")
                            with col3:
                                st.write(f"**Created:** {doc.get('created_at', 'N/A')}")
                                st.write(f"**Updated:** {doc.get('updated_at', 'N/A')}")
                            
                            if doc.get("content_summary"):
                                st.caption(f"Summary: {doc['content_summary'][:200]}...")
                            
                            if doc.get("error_msg"):
                                st.error(f"Error: {doc['error_msg']}")
                            
                            # Delete button
                            if st.button(f"🗑️ Delete", key=f"del_{doc.get('id')}"):
                                try:
                                    del_res = requests.delete(
                                        f"{LIGHTRAG_URL}/documents/delete_document",
                                        json={"doc_ids": [doc.get("id")], "delete_file": True}
                                    )
                                    if del_res.status_code == 200:
                                        st.success("Document deletion started!")
                                        st.rerun()
                                    else:
                                        st.error(f"Delete failed: {del_res.text}")
                                except Exception as e:
                                    st.error(str(e))
                else:
                    st.info("No documents found.")
                    
                # Pagination info
                pagination = docs_data.get("pagination", {})
                st.caption(f"Page {pagination.get('page', 1)} of {pagination.get('total_pages', 1)} | Total: {pagination.get('total_count', 0)} documents")
            else:
                st.error(f"Failed to fetch documents: {docs_res.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")
        
        # Reprocess failed button
        st.divider()
        if st.button("🔄 Reprocess Failed Documents"):
            try:
                res = requests.post(f"{LIGHTRAG_URL}/documents/reprocess_failed")
                if res.status_code == 200:
                    st.success("Reprocessing started!")
                else:
                    st.error(res.text)
            except Exception as e:
                st.error(str(e))
    
    # ============ QUERY KNOWLEDGE ============
    elif kb_menu == "🔍 Query Knowledge":
        st.subheader("Query the Knowledge Base")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            query_text = st.text_input("Enter your question", placeholder="What is EcoThreads?")
        with col2:
            query_mode = st.selectbox(
                "Mode",
                ["mix", "hybrid", "local", "global", "naive"],
                help="mix: Best overall | hybrid: local+global | local: entities | global: patterns | naive: vector only"
            )
        
        include_refs = st.checkbox("Include references", value=True)
        
        if st.button("🔍 Search", type="primary") and query_text:
            with st.spinner("Querying knowledge base..."):
                try:
                    payload = {
                        "query": query_text,
                        "mode": query_mode,
                        "include_references": include_refs
                    }
                    res = requests.post(f"{LIGHTRAG_URL}/query", json=payload, timeout=120)
                    
                    if res.status_code == 200:
                        result = res.json()
                        
                        st.markdown("### Response")
                        st.markdown(result.get("response", "No response"))
                        
                        # Show references
                        refs = result.get("references", [])
                        if refs:
                            with st.expander(f"📚 References ({len(refs)})"):
                                for ref in refs:
                                    st.write(f"**[{ref.get('reference_id')}]** {ref.get('file_path', 'Unknown source')}")
                    else:
                        st.error(f"Query failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # ============ GRAPH EXPLORER ============
    elif kb_menu == "🕸️ Graph Explorer":
        st.subheader("Knowledge Graph Explorer")
        
        # Search entities
        entity_search = st.text_input("Search entities", placeholder="Type entity name...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔥 Popular Entities")
            try:
                pop_res = requests.get(f"{LIGHTRAG_URL}/graph/label/popular?limit=20", timeout=10)
                if pop_res.status_code == 200:
                    popular = pop_res.json()
                    if popular:
                        for entity in popular[:20]:
                            st.write(f"• {entity}")
                    else:
                        st.info("No entities found")
            except Exception as e:
                st.error(str(e))
        
        with col2:
            st.markdown("#### 🔍 Search Results")
            if entity_search:
                try:
                    search_res = requests.get(f"{LIGHTRAG_URL}/graph/label/search?q={entity_search}&limit=20", timeout=10)
                    if search_res.status_code == 200:
                        results = search_res.json()
                        if results:
                            for entity in results:
                                st.write(f"• {entity}")
                        else:
                            st.info("No matching entities")
                except Exception as e:
                    st.error(str(e))
        
        st.divider()
        
        # View graph for specific entity
        st.markdown("#### 🌐 View Entity Graph")
        selected_entity = st.text_input("Entity name", placeholder="Enter entity to explore...")
        max_depth = st.slider("Max depth", 1, 5, 2)
        
        if st.button("Load Graph") and selected_entity:
            try:
                graph_res = requests.get(
                    f"{LIGHTRAG_URL}/graphs",
                    params={"label": selected_entity, "max_depth": max_depth, "max_nodes": 100},
                    timeout=15
                )
                if graph_res.status_code == 200:
                    graph_data = graph_res.json()
                    st.json(graph_data)
                else:
                    st.error(f"Failed to load graph: {graph_res.text}")
            except Exception as e:
                st.error(str(e))
    
    # ============ SETTINGS ============
    elif kb_menu == "⚙️ Settings":
        st.subheader("Knowledge Base Settings")
        
        st.warning("⚠️ These actions are destructive and cannot be undone!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🧹 Clear LLM Cache")
            st.caption("Remove cached LLM responses to force fresh extraction")
            if st.button("Clear Cache"):
                try:
                    res = requests.post(f"{LIGHTRAG_URL}/documents/clear_cache", json={})
                    if res.status_code == 200:
                        st.success("Cache cleared!")
                    else:
                        st.error(res.text)
                except Exception as e:
                    st.error(str(e))
        
        with col2:
            st.markdown("#### 🗑️ Clear All Documents")
            st.caption("Remove ALL documents, entities, and relationships")
            confirm = st.text_input("Type 'DELETE' to confirm", key="confirm_delete")
            if st.button("Clear All", type="secondary"):
                if confirm == "DELETE":
                    try:
                        res = requests.delete(f"{LIGHTRAG_URL}/documents")
                        if res.status_code == 200:
                            st.success("All documents cleared!")
                        else:
                            st.error(res.text)
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.warning("Please type 'DELETE' to confirm")
        
        st.divider()
        
        # Cancel pipeline
        st.markdown("#### ⏹️ Cancel Running Pipeline")
        if st.button("Cancel Pipeline"):
            try:
                res = requests.post(f"{LIGHTRAG_URL}/documents/cancel_pipeline")
                if res.status_code == 200:
                    result = res.json()
                    st.info(result.get("message", "Cancellation requested"))
                else:
                    st.error(res.text)
            except Exception as e:
                st.error(str(e))

# --- Tab 3: Memory Inspector ---
with tabs[2]:
    st.header("🧠 Memory Inspector")
    st.info("Memory is handled internally by Mem0. Use the chat to test memory recall.")
    
    st.subheader("Test Memory Retrieval")
    mem_user_id = st.text_input("User ID to inspect", value="test_user_1", key="mem_user")
    
    if st.button("Load User Profile"):
        st.info("Memory inspection endpoint not yet implemented. Check agent logs for memory operations.")
