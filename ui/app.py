import streamlit as st
import requests

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"

# --- UI Setup ---
st.set_page_config(page_title="Jigyasa", layout="wide", initial_sidebar_state="expanded")

# --- Initialize session state ---
if "last_summary" not in st.session_state:
    st.session_state.last_summary = None
if "last_url" not in st.session_state:
    st.session_state.last_url = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🧠 Jigyasa</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    selected_page = st.radio(
        "Select an Agent",
        [" Conversational Assistant", " Summarizer Agent", " My Notebook & Analysis"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.info("Use the 'Add to Jigyasa' bookmarklet in your browser to add notes from any website.")


# --- Main Content Area ---

# --- Page 1: The Main Chat Interface ---
if selected_page == " Conversational Assistant":
    st.header("Conversational Assistant (Synthesizer Agent)")
    st.write("Ask questions about your collected research here. The AI will synthesize answers based on your notes.")

    # Display the chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your notes..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🧠 Thinking...")
            try:
                response = requests.post(f"{BACKEND_URL}/ask", json={"question": prompt})
                if response.status_code == 200:
                    answer = response.json().get("answer")
                    message_placeholder.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error("The Synthesis Agent failed.")
            except requests.exceptions.RequestException as e:
                st.error("Could not connect to the backend.")

# --- Page 2: The Summarizer Agent "Subpage" ---
elif selected_page == " Summarizer Agent":
    st.header("Smart Summarizer Agent")
    st.write("Paste a URL for a context-aware summary. The summary will be tailored to the topics in your notebook.")
    
    url_to_summarize = st.text_input("URL to Summarize:")
    if st.button("Generate Smart Summary"):
        if url_to_summarize:
            with st.spinner(" Activating Summarizer Agent... This may take a moment."):
                try:
                    response = requests.post(f"{BACKEND_URL}/summarize-url", json={"url": url_to_summarize})
                    if response.status_code == 200:
                        summary = response.json().get("summary")
                        st.session_state.last_summary = summary
                        st.session_state.last_url = url_to_summarize
                    else:
                        st.error("The Summarizer Agent failed.")
                        st.session_state.last_summary = None
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the backend.")
                    st.session_state.last_summary = None
        else:
            st.warning("Please enter a URL.")

    # Display the summary and the "Add to Notebook" button
    if st.session_state.last_summary:
        st.markdown("---")
        st.subheader("Generated Summary")
        st.markdown(st.session_state.last_summary)
        if st.button("Add this Summary to My Notebook"):
            with st.spinner("Saving..."):
                note_text = f"AI Summary of {st.session_state.last_url}:\n\n{st.session_state.last_summary}"
                requests.post(f"{BACKEND_URL}/add-manual-note", json={"text": note_text})
                st.success("Summary saved to your notebook!")
                st.session_state.last_summary = None
                st.session_state.last_url = None
                st.rerun()

# --- Page 3: The Notebook & Analysis "Subpage" ---
elif selected_page == " My Notebook & Analysis":
    st.header("Notebook Actions & Review")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Verifier Agent")
        st.write("Check your most recently added note for contradictions against your existing research.")
        if st.button("Analyze for Contradictions"):
            with st.spinner("🕵️‍♂️ Asking the Verifier Agent to check your notes..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/check-contradictions")
                    if response.status_code == 200:
                        result = response.json().get("result")
                        if "CONTRADICTION:" in result:
                            st.warning(result)
                        else:
                            st.success(result)
                    else:
                        st.error("Failed to run analysis.")
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the backend.")

    with col2:
        st.subheader("View All Notes")
        st.write("Click the button to refresh and see all notes currently in your notebook.")
        if st.button("Show All Notes"):
            try:
                response = requests.get(f"{BACKEND_URL}/notes")
                if response.status_code == 200:
                    notes = response.json().get("notes", [])
                    if notes:
                        for i, note in enumerate(notes):
                            st.info(f"**Note {i+1}:**\n\n{note}")
                    else:
                        st.info("Your notebook is empty.")
                else:
                    st.error("Failed to fetch notes from the backend.")
            except requests.exceptions.RequestException:
                st.error("Could not connect to the backend.")

