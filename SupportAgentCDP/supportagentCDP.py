from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import requests
from bs4 import BeautifulSoup
import os
import faiss
import numpy as np
import spacy
from sentence_transformers import SentenceTransformer

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Initialize FastAPI app
app = FastAPI()

# Load NLP model for embedding
nlp = spacy.load("en_core_web_md")
transformer = SentenceTransformer("all-MiniLM-L6-v2")  # Efficient semantic search model

# Documentation sources
documentation_data = {
    "segment": "https://segment.com/docs/?ref=nav",
    "mparticle": "https://docs.mparticle.com/",
    "lytics": "https://docs.lytics.com/",
    "zeotap": "https://docs.zeotap.com/home/en-us/",
}

class Query(BaseModel):
    question: str

def scrape_documentation(base_url, max_pages=10):
    """Recursively scrape Segment docs by following internal links."""
    visited = set()  # Track visited URLs
    to_visit = [base_url]  # Start with the main docs page
    all_text = ""  # Store all scraped text

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)  # Get the next page to visit
        if url in visited:
            continue  # Skip already visited pages

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"🚨 ERROR: Failed to fetch {url} - Status Code {response.status_code}")
                continue  # Skip to the next URL

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract meaningful content from the page
            content = soup.find("article") or soup.find("main") or soup.find("div", {"class": ["content", "docs-content", "doc-section"]})

            if content:
                text = content.get_text(separator=" ", strip=True)
                if len(text) > 50:  # Ignore useless short texts
                    print(f"✅ Extracted {len(text)} characters from {url}")
                    all_text += f"📖 {url}\n{text[:5000]}\n\n"  # Append content from this page

            # Find and add new internal links to scrape
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if href.startswith("/") and "docs" in href:  # Only follow valid internal doc links
                    full_link = base_url.rstrip("/") + href
                    if full_link not in visited and full_link not in to_visit:
                        to_visit.append(full_link)

            visited.add(url)  # Mark this page as visited

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")

    print(f"✅ Finished scraping. Extracted {len(all_text)} characters from Segment docs.")
    return all_text[:50000]

def scrape_with_selenium(url):
    """Scrapes documentation using Selenium for JavaScript-rendered pages."""
    try:
        options = Options()
        options.add_argument("--headless") 
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        import time
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        content = soup.find("article") or soup.find("main") or soup.find("div", {"class": ["content", "docs-content", "doc-section"]})

        if content:
            text = content.get_text(separator=" ", strip=True)
            print(f"✅ Extracted {len(text)} characters from {url} using Selenium")
            return text[:10000]

        print(f"⚠️ WARNING: No meaningful content found in {url} using Selenium")
        return ""

    except Exception as e:
        print(f"❌ Selenium scraping error for {url}: {e}")
        return ""

def save_docs():
    """Scrape documentation from multiple sources and save it."""
    docs = {}

    for platform, url in documentation_data.items():
        if platform == "zeotap":  # Use Selenium for Zeotap
            docs[platform] = scrape_with_selenium(url)
        else:
            docs[platform] = scrape_documentation(url)

    with open("docs.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=4)

    print("✅ Documentation saved.")

def load_docs():
    """Load documentation from local storage."""
    if os.path.exists("docs.json"):
        with open("docs.json", "r", encoding="utf-8") as f:
            docs = json.load(f)
            print("📄 LOADED DOCUMENTATION PREVIEW:", json.dumps(docs, indent=2)[:1000])  # Print first 1000 characters
            return docs
    return {}

def build_faiss_index():
    """Build FAISS index from documentation"""
    docs = load_docs()
    sentences = []
    metadata = []
    
    for platform, doc_text in docs.items():

        if not doc_text:  # Check if documentation is empty
            print(f"⚠️ WARNING: No data found for {platform}")
            continue

        doc_sentences = doc_text.split(". ")
        for sentence in doc_sentences:
            if sentence.strip():
                sentences.append(sentence)
                metadata.append(platform)

    if not sentences:  # Check if we got any valid text
        print("🚨 ERROR: No valid sentences found in documentation!")
        return None, [], []
    
    embeddings = transformer.encode(sentences, convert_to_numpy=True)

    if len(embeddings) == 0:
        print("🚨 ERROR: No embeddings generated! Check your docs.json file.")
        return None, [], []

    print(f"✅ FAISS Index: {embeddings.shape} embeddings loaded.")
    
    index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 distance (Euclidean)
    index.add(embeddings)
    
    return index, sentences, metadata

index, sentences, metadata = build_faiss_index()

def search_faiss(question, k=3):
    """Perform semantic search using FAISS"""
    query_vector = transformer.encode([question], convert_to_numpy=True)
    distances, indices = index.search(query_vector, k)
    
    results = []
    
    for i in indices[0]:
        if i < len(sentences):  # Ensure valid index
            sentence = sentences[i]

            # Filter out generic one-word sentences
            if len(sentence.split()) < 5:
                continue

            # Boost ranking if sentence has instructional words
            if any(keyword in sentence.lower() for keyword in ["set up", "configure", "install", "steps", "connect", 'source']):
                results.insert(0, f"📌 {sentence}")  # Push to top
            else:
                results.append(f"📌 {sentence}")
        if not results:  # Return a default message if no results are found
            return ["No relevant documentation found."]

    return results[:3] 

@app.post("/ask")
def ask_question(query: Query):
    """Handles incoming questions and retrieves relevant documentation using FAISS"""
    if not query.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    results = search_faiss(query.question)
    
    if not results:  # Ensure lists are not empty
        return {"answer": "No relevant documentation found."}
    
    response_text = "\n\n".join(results)  # Join results without sources
    return {"answer": response_text}
        

if __name__ == "__main__":
    save_docs()  # Scrape and save documentation before starting
    index, sentences, metadata = build_faiss_index()  # Rebuild FAISS index
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
