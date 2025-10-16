import streamlit as st
import requests
import uuid
import time

# --- Page config for full width ---
st.set_page_config(layout="wide")

# --- CSS to remove horizontal padding for main content ---
st.markdown("""
<style>
.block-container {
    padding-left: 0rem;
    padding-right: 0rem;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("⚙️ Controls")
if st.sidebar.button("🆕 New Session"):
    st.session_state["chat"] = []
    st.session_state["session_id"] = str(uuid.uuid4())
    st.sidebar.success("✅ New session started")

# --- Initialize session state ---
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
if "chat" not in st.session_state:
    st.session_state["chat"] = []

st.title("🤖 Hackathon Bedrock Chatbot")

# --- Display chat messages ---
for msg in st.session_state["chat"]:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# --- Chat input ---
question = st.chat_input("Ask something...")
if question:
    # Show user message immediately
    st.chat_message("user").markdown(question)
    st.session_state["chat"].append({"role": "user", "content": question})

    # --- Start job ---
    API_START = "https://hculxoeutg.execute-api.us-east-1.amazonaws.com/dev/Hackathon-sales"
    API_RESULT = "https://hculxoeutg.execute-api.us-east-1.amazonaws.com/dev/Hackathon-sales-result"

    resp = requests.post(API_START, json={
        "question": question,
        "session_id": st.session_state["session_id"]
    }).json()
    job_id = resp["job_id"]

    # --- Polling for result ---
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            for _ in range(60):  # poll up to 2 minutes (every 2 sec)
                time.sleep(2)
                result = requests.get(API_RESULT, params={"job_id": job_id}).json()
                if result["status"] == "completed":
                    st.markdown(result["response"])  # show response immediately inside chat bubble
                    st.session_state["chat"].append({"role": "assistant", "content": result["response"]})
                    break
            else:
                st.warning("Response not ready, try again later.")
