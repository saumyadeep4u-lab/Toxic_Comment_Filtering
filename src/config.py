import os
import logging
from pathlib import Path

# Dynamic path resolution based on where this script lives
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Updated to match the exact folder name exported from your Jupyter Notebook
MODEL_DIR = BASE_DIR / "models" / "distilbert_toxic"

# Make sure output directories exist
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Dataset path 
TRAIN_DATA_PATH = DATA_DIR / "data.csv"

# Model configuration
MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 128
BATCH_SIZE = 32

# ==========================================
# MODEL CONFIGURATION & HEURISTICS
# ==========================================

# 1. Optimal thresholds tuned for >80% precision
# EXACT numbers generated from the perfectly locked Jupyter Notebook run
THRESHOLDS = {
    'toxic': 0.332,
    'severe_toxic': 0.665,
    'obscene': 0.307,
    'threat': 0.689,
    'insult': 0.594,
    'identity_hate': 0.701
}

# 2. Base AI Weights (Penalty points for severity scoring)
WEIGHTS = {
    'toxic': 1.0, 
    'severe_toxic': 3.0, 
    'obscene': 1.5, 
    'threat': 5.0,
    'insult': 1.2,
    'identity_hate': 4.0
}

# 3. Spam Penalty
SPAM_PENALTY = 1.5

# 4. Backend AI Labels
LABELS_LIST = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

# 5. UI Display Names (Translates backend labels to professional UI text)
DISPLAY_NAMES = {
    'toxic': 'Toxic',
    'severe_toxic': 'Severe Toxic',
    'obscene': 'Profanity',       
    'threat': 'Threat',
    'insult': 'Insult',
    'identity_hate': 'Hate Speech', 
    'spam': 'Spam'
}

# ==========================================
# LOGGING SETUP
# ==========================================
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("ToxicFilterApp")

logger = setup_logger()