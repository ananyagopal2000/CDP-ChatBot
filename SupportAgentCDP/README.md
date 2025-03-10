# CDP Support Chatbot

## 📌 Overview
This is a chatbot that provides answers to "how-to" questions related to four Customer Data Platforms (CDPs): **Segment, mParticle, Lytics, and Zeotap**. The chatbot retrieves information from official documentation and, if needed, utilizes OpenAI for more advanced responses.

---

## 🎯 Features
✅ Answer "how-to" questions based on CDP documentation
✅ Retrieve relevant sections from official docs
✅ Handle variations in question phrasing
✅ Use OpenAI GPT-4 for complex queries (optional)
✅ Compare functionalities across different CDPs
✅ Web-based UI using Streamlit

---

## 🛠️ Tech Stack
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **AI (Optional):** OpenAI API (GPT-4)
- **Web Scraping:** BeautifulSoup
- **Deployment:** Uvicorn (for FastAPI)

---

## 🚀 Installation & Setup
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-repo/cdp-chatbot.git
cd cdp-chatbot
```

### **2️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3️⃣ Set Up OpenAI API Key (Optional)**
If using OpenAI, create a `.env` file in the project folder and add:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### **4️⃣ Run the FastAPI Backend**
```bash
python -m uvicorn supportagentCDP:app --host 127.0.0.1 --port 8000 --reload
```

### **5️⃣ Run the Streamlit Frontend**
```bash
streamlit run streamlit_app.py
```

---

## 🔥 How It Works
1️⃣ **User enters a question** in the Streamlit UI
2️⃣ **Backend searches documentation** or uses OpenAI
3️⃣ **Best-matching response is returned** to the UI

---

## 🛠️ API Usage (Testing Without UI)
Use **Postman** or **cURL** to test the FastAPI endpoint:
```bash
curl -X POST "http://127.0.0.1:8000/ask" -H "Content-Type: application/json" -d '{"question": "How do I create an audience in Lytics?"}'
```

Expected response:
```json
{
  "answer": "Found relevant info in Lytics docs. Check the documentation."
}
```

---

## 📌 Edge Cases Handled
- **Long queries** → Warns users about overly lengthy inputs
- **Non-CDP questions** → Prevents irrelevant queries (e.g., movies, sports)
- **Unknown queries** → Uses OpenAI fallback (if enabled)

---

## 🚀 Future Improvements
🔹 Better documentation search (vector-based retrieval)
🔹 User authentication & saved queries
🔹 Multi-language support

---

## 🤝 Contributing
Feel free to submit issues and pull requests to improve the chatbot!

---

## 📜 License
This project is licensed under the **MIT License**.

