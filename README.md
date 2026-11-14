# 🛡️ Toxic Comment Filtering

This project is a real-time, hybrid AI moderation system designed to filter toxic comments in gaming live chats. It combines the deep natural language understanding of a fine-tuned **DistilBERT** model with a strict **Zero-Tolerance Heuristics Engine** to catch severe threats, bypassed profanity (leetspeak), and spam. 

Built with an interactive **Streamlit** front-end, the application analyzes chat messages in real-time, assigns a severity score (0.0 to 5.0), and triggers automated moderation actions (Allow, Warning, Mute, or Auto-Ban).

---
🌐 **Live Demo:** (https://toxiccommentfiltering.streamlit.app/)

## 📁 Project Structure

Below is the complete file and folder structure for this project. 

```text
toxic_comment_project/
├── app.py                         # Main Streamlit application
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── app_findings/                  # Exported app logs and visual proofs
│   ├── 2026-07-25T09-11_export.csv
│   └── App Visual Log.pdf
├── data/                          # Training and testing datasets
│   └── data.csv                   <-- (Requires manual download, see instructions)
├── models/                        
│   └── distilbert_toxic/          # Saved fine-tuned DistilBERT model
│       ├── config.json            <-- (Requires manual download)
│       ├── model.safetensors      <-- (Requires manual download)
│       ├── tokenizer.json         <-- (Requires manual download)
│       └── tokenizer_config.json  <-- (Requires manual download)
├── notebooks/                     # Jupyter notebooks used for AI training
│   ├── 01_model_training.ipynb
│   └── Notebook Visual Log.pdf
└── src/                           # Backend logic and configurations
    ├── config.py                  # Thresholds, weights, and directory paths
    └── moderation.py              # Hybrid heuristics and scoring engine
```

## 🚀 Setup & Installation

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository & Install Dependencies
First, ensure you are in the root `toxic_comment_project/` directory. Open your terminal and install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Download the Dataset
The raw dataset is too large to host in standard repositories and must be downloaded externally.
1. Download `data.csv` [from this Google Drive link](https://drive.google.com/file/d/1W7xLfIs5kcdPZSHRzUgKxHOY1U1h6fq7/view?usp=drive_link).
2. Move the downloaded `data.csv` file directly into the `data/` folder.

### 3. Download the AI Model
The fine-tuned DistilBERT model files must be downloaded and placed in the correct directory for the app to function. 
1. Download the model files [from this Google Drive link](https://drive.google.com/drive/folders/1ZJlhaWywkowRE8ww-iYA9eKtlMyqf8OA?usp=sharing).
2. Navigate to `models/distilbert_toxic/`.
3. Place all 4 downloaded files directly into this folder:
   * `model.safetensors`
   * `tokenizer.json`
   * `config.json`
   * `tokenizer_config.json`

## 🎮 How to Run the App

Once your dependencies are installed and the `data.csv` and model files are correctly placed in their respective folders, you can launch the live dashboard!

Run the following command in your terminal from the root directory:

```bash
streamlit run app.py
```

A browser window will automatically open displaying the **Live Chat Input** and **Moderation Dashboard**.

---

## 🧠 Core Architecture & Features

### 1. Advanced Text Preprocessing (`app.py`)
Before the AI analyzes a message, it passes through a highly aggressive "Star-Catcher" and leetspeak translator. This ensures that words obfuscated with symbols (e.g., `cr@p`, `m0th3rfuck3r`, `b1tch`) are translated into readable text before punctuation is removed, preventing toxic users from bypassing the AI.

### 2. The DistilBERT Model (`models/`)
A custom-trained DistilBERT sequence classification model evaluates the cleaned text and outputs probabilities for six distinct categories:
* Toxic
* Severe Toxic
* Obscene (Profanity)
* Threat
* Insult
* Identity Hate (Hate Speech)

### 3. Hybrid Moderation Engine (`src/moderation.py`)
The engine intercepts the AI probabilities and compares them against strictly tuned math thresholds (`src/config.py`). It then applies **Zero-Tolerance Heuristics** to catch:
* **Phishing & Spam:** Looks for repetitive word flooding or phishing links (e.g., "free vbucks").
* **Gaming Toxicity:** Catches specific gaming slang (e.g., "bot team", "uninstall", "trash").
* **Severe Threats:** Auto-flags doxxing or real-world threats (e.g., "track your IP").

### 4. Automated Actions
Based on the combined AI and heuristic severity score (capped at 5.0), the system outputs a final action:
* **0.0:** `Allow` (Green)
* **0.1 - 1.9:** `Warning` (Yellow)
* **2.0 - 3.9:** `Mute (24h)` (Orange)
* **4.0 - 5.0:** `Auto-Ban` (Red)

---

## 📂 Folder Breakdown

* **`app_findings/`**: Contains visual proofs of the app working, including `App Visual Log.pdf` and exported CSV logs (`2026-07-25T09-11_export.csv`) of moderated test messages.

* **`notebooks/`**: Contains the original `01_model_training.ipynb` file where the DistilBERT model was trained and thresholds were calculated, alongside its PDF visual log, `Notebook Visual Log.pdf`

* **`src/`**: The brain of the operation. Contains `config.py` for easily tweaking AI weights/thresholds, and `moderation.py` which houses the overarching logic.
