import re
from src.config import THRESHOLDS, WEIGHTS, SPAM_PENALTY, DISPLAY_NAMES

# --- 1. HYBRID HEURISTICS ENGINE ---
def check_heuristics(original_text: str) -> dict:
    text_lower = original_text.lower()
    penalty = 0.0
    tags = []
    
    # 1. Critical Threats & Phishing (Max Penalty)
    if re.search(r'\b(know where you live|track your ip|pull your ip)\b', text_lower):
        penalty += 5.0
        tags.append("Threat / Doxxing")
    if re.search(r'\b(free\s+(vbucks|robux|skins)|link\s+in\s+bio|cheap\s+skins)\b', text_lower):
        penalty += 5.0
        tags.append("Phishing / Scam")
        
    # 2. Contextual Hate Speech (Heavy Penalty)
    if re.search(r'\b(go back to your country|you people are animals|ching chong)\b', text_lower):
        penalty += 4.0
        tags.append("Hate Speech")
    if re.search(r'\b(white|black|brown|asian)\strash\b', text_lower):
        penalty += 3.0
        tags.append("Racial Insult")
    if re.search(r'\byou(?:r|\'?re|\sare)?\s+(?:an?\s+)?(?:autistic|cancer|terrorist|braindead)\b', text_lower):
        penalty += 3.0
        tags.append("Weaponized Identity")

    # 3. ZERO-TOLERANCE SLURS (Instant Heavy Penalty)
    if re.search(r'\b(tranny|faggot|retard|nazi)\b', text_lower):
        penalty += 4.0
        tags.append("Severe Slur")
        
    # 4. Standalone Extremist Keywords
    if re.search(r'\b(terrorist)\b', text_lower):
        penalty += 2.0
        tags.append("Extremist Language")

    # 5. Gaming Toxicity & Light Insults (Warning Penalty)
    if re.search(r'\b(clown|braindead|trash|noobs?|idiots?|garbage)\b', text_lower):
        penalty += 1.5
        tags.append("Light Insult")
    if re.search(r'\b(uninstall( the game)?|git gud|bot team|stop feeding|ez( pz| game)?)\b', text_lower):
        penalty += 1.5
        tags.append("Gaming Toxicity")

    # 6. Commercial Spam & Repetitive Flooding (Warning Penalty)
    spam_phrases = [
        "twitch", 
        "subscribe to my", 
        "check out my", 
        "check my youtube",
        "check my channel",
        "free followers", 
        "buy cheap"
    ]
    if any(phrase in text_lower for phrase in spam_phrases) or re.search(r'\bsub\s*(for|4)\s*sub\b', text_lower):
        penalty += SPAM_PENALTY
        tags.append("Spam")
        
    words = text_lower.split()
    if len(words) >= 5:
        # Check for word repetition (e.g., "go go go go go")
        if re.search(r'\b(\w+)(?:\s+\1){4,}\b', text_lower):
            if "Spam" not in tags:
                penalty += SPAM_PENALTY
                tags.append("Spam")

    return {"penalty": penalty, "tags": tags}

# --- 2. MAIN MODERATION ENGINE ---
def analyze_comment(probs, text):
    tags = []
    severity_score = 0.0
    
    # A. Check AI probabilities against your custom THRESHOLDS
    for category, prob in probs.items():
        if prob >= THRESHOLDS.get(category, 0.5):
            tags.append(DISPLAY_NAMES[category])
            severity_score += WEIGHTS[category]

    # B. Apply Zero-Tolerance Heuristics & Spam Filters
    heuristic_results = check_heuristics(text)
    severity_score += heuristic_results["penalty"]
    tags.extend(heuristic_results["tags"])

    # Remove duplicate tags
    tags = list(set(tags))

    # C. Cap the maximum score at exactly 5.0
    severity_score = min(severity_score, 5.0)

    # D. Determine the Action based on the final severity score
    if severity_score == 0:
        action = "Allow"
    elif severity_score < 2.0:
        action = "Warning"
    elif severity_score < 4.0:
        action = "Mute (24h)"
    else:
        action = "Auto-Ban"

    return {
        "tags": tags,
        "severity_score": round(severity_score, 1),
        "action": action
    }