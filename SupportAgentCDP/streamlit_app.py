import streamlit as st
import requests

# Backend API URL
FASTAPI_URL = "http://127.0.0.1:8000/ask"

# Streamlit UI Setup
st.set_page_config(page_title="CDP Support Chatbot", layout="wide")

st.title("🤖 CDP Support Chatbot")
st.write("Ask me questions about Segment, mParticle, Lytics, and Zeotap!")

# User Input Field
user_query = st.text_input("💬 Ask a question:")

if st.button("🔍 Get Answer"):
    if user_query.strip() == "":
        st.warning("⚠️ Please enter a question.")
    if len(user_query) > 500:
        st.warning("⚠️ Your question is too long. Try making it more specific.")
    elif any(word in user_query.lower() for word in ["movie", "weather", "sports"]):
        st.warning("⚠️ This chatbot only answers questions about CDPs.")
    else:
        with st.spinner("Thinking... 🤔"):
            try:
                # Send question to FastAPI chatbot
                response = requests.post(FASTAPI_URL, json={"question": user_query})
                response_data = response.json()

                if "answer" in response_data:
                    st.success("✅ Answer:")
                    st.write(response_data["answer"])
                else:
                    st.error("⚠️ Sorry, I couldn't find an answer.")
            except Exception as e:
                st.error(f"❌ Error connecting to backend: {e}")
