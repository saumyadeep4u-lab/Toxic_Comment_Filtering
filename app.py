import os
import re
import streamlit as st
import pandas as pd
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from src.moderation import analyze_comment
from src.config import MODEL_DIR, LABELS_LIST

# Set page config
st.set_page_config(page_title="Toxic Comment Filter", page_icon="🛡️", layout="wide")

def clean_text(text: str) -> str:
    """Cleans and un-censors text exactly as it was during AI training."""
    if not isinstance(text, str):
        return ""
        
    # 1. Un-censor text FIRST (before removing punctuation!)
    text = re.sub(r'f\*\*\*ing', 'fucking', text, flags=re.IGNORECASE)
    text = re.sub(r'f\*\*\*', 'fuck', text, flags=re.IGNORECASE)
    text = re.sub(r's\*\*\*', 'shit', text, flags=re.IGNORECASE)
    text = re.sub(r'b\*tch', 'bitch', text, flags=re.IGNORECASE)
    text = re.sub(r'c\*\*t', 'cunt', text, flags=re.IGNORECASE)
    text = re.sub(r'a\$\$', 'ass', text, flags=re.IGNORECASE)
    
    # 2. Advanced Slur & Obfuscation Bypasses
    text = re.sub(r'r[\*e3]?t[@a]?rd', 'retard', text, flags=re.IGNORECASE)
    text = re.sub(r'f\*ggot', 'faggot', text, flags=re.IGNORECASE)
    
    # 3. Aggressive Star-Catcher for severe slurs
    text = re.sub(r'\bt[\*r]*[\*a4\@]+[\*n]*[\*y]+\b', 'tranny', text, flags=re.IGNORECASE)

    # 4. Apply standard NLP cleaning (Match Training Setup)
    text = text.lower()
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def ensure_model_downloaded(model_path: str):
    """Downloads the fine-tuned DistilBERT model folder from Google Drive if missing on Streamlit Cloud."""
    safetensors_file = os.path.join(model_path, "model.safetensors")
    if os.path.exists(safetensors_file):
        return

    os.makedirs(model_path, exist_ok=True)

    # Extract the Google Drive model folder link from README.md
    readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
    folder_url = None
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            match = re.search(r"https://drive\.google\.com/drive/folders/[^\s\)]+", f.read())
            if match:
                folder_url = match.group(0)

    if not folder_url:
        raise FileNotFoundError("Model weights not found locally and Google Drive folder link could not be read from README.md.")

    import gdown
    with st.spinner("Downloading fine-tuned DistilBERT model weights from Google Drive (first-time cloud setup)..."):
        gdown.download_folder(url=folder_url, output=model_path, quiet=False, use_cookies=False)

# Initialize the model ONLY ONCE using Streamlit's caching
@st.cache_resource
def load_toxicity_model():
    print("Loading model and tokenizer into memory...")
    
    # Dynamic path from config
    model_path = str(MODEL_DIR)
    
    # Ensure model weights exist locally (downloads from Google Drive on Streamlit Cloud)
    ensure_model_downloaded(model_path)
    
    # 1. LOAD TOKENIZER FROM THE INTERNET:
    # This bypasses your folder entirely so it doesn't need vocab.txt
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    
    # 2. LOAD MODEL FROM YOUR FOLDER:
    # This loads your saved model.safetensors
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    model.eval()
    
    return tokenizer, model

# Load the model and define the labels
tokenizer, model = load_toxicity_model()
labels = LABELS_LIST

# Title and Description
st.title("🛡️ Gaming Live-Chat Toxicity Filter")
st.markdown("This system flags toxic messages in real-time, assigns a severity score (0-5), and triggers moderation actions based on a hybrid AI and Zero-Tolerance Heuristics engine.")

# Create layout columns
col1, col2 = st.columns([1, 1])

# Initialize session state to store chat history
if 'chat_log' not in st.session_state:
    st.session_state.chat_log = []

with col1:
    st.subheader("Live Chat Input")
    user_input = st.text_input("Type a chat message...", placeholder="e.g., GG well played! or free vbucks link in bio")
    
    if st.button("Send Message"):
        if user_input.strip() == "":
            st.warning("Please type a message first.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    # 1. Clean the text EXACTLY like the training data
                    clean_input = clean_text(user_input)
                    
                    # 2. Translate cleaned text to numbers and get raw AI outputs
                    inputs = tokenizer(clean_input, return_tensors="pt", truncation=True, padding=True, max_length=128)
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                        # Apply sigmoid to convert raw math logits into probabilities (0.0 to 1.0)
                        probs_list = torch.sigmoid(outputs.logits).squeeze().tolist()
                    
                    # Ensure it's a list even if only one label (failsafe)
                    if not isinstance(probs_list, list):
                        probs_list = [probs_list]
                        
                    # Zip labels and probabilities into a dictionary
                    probs = dict(zip(labels, probs_list))
                    
                    # 3. Get tags, score, and action from the Hybrid Moderation Engine
                    # We pass clean_input so check_heuristics can catch the un-censored words!
                    result = analyze_comment(probs, clean_input)
                    
                    # 4. Save to log
                    log_entry = {
                        "Message": user_input, # Display the original text in the UI
                        "Score": result["severity_score"],
                        "Action": result["action"],
                        "Tags": ", ".join(result["tags"]) if result["tags"] else "Non-Toxic"
                    }
                    
                    # Add to beginning of list so newest is on top
                    st.session_state.chat_log.insert(0, log_entry) 
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")

with col2:
    st.subheader("Moderation Dashboard")
    
    if st.session_state.chat_log:
        # Convert log to dataframe for nice display
        df_log = pd.DataFrame(st.session_state.chat_log)
            
        # Display the dataframe safely without deprecated styling maps that crash React
        st.dataframe(
            df_log,
            use_container_width=True,
            column_config={
                "Score": st.column_config.NumberColumn(format="%.1f"),
                "Action": st.column_config.TextColumn("Moderation Action")
            },
            hide_index=True
        )
    else:
        st.info("No messages analyzed yet. Type something in the chat box!")
    
    
