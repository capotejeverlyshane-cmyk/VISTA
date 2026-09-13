import re

STOP_WORDS = set([
    # English
    "a", "an", "the", "is", "are", "to", "for", "of", "and", "in", "on", "with", "how", "what", "where", "when", "why", "can", "i", "you", "do", "does", "my", "me",
    # Tagalog
    "ang", "mga", "sa", "na", "ng", "ay", "ba", "pa", "po", "opo", "ko", "mo", "niya", "kami", "tayo", "nila", "kung", "para", "ano", "paano", "saan", "kailan", "bakit",
    # Bisaya
    "ang", "mga", "sa", "nga", "ug", "kay", "ba", "pa", "ko", "mo", "nimo", "nako", "niya", "kami", "kita", "nila", "kung", "para", "unsa", "unsaon", "asa", "kanus-a", "ngano", "ka", "og"
])

def clean_text(text: str) -> str:
    # Lowercase and strip whitespace
    text = text.lower().strip()
    # Remove special characters but keep letters and numbers
    text = re.sub(r"[^a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ\s]", "", text)
    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)
    
    # Remove stop words
    words = text.split()
    filtered_words = [word for word in words if word not in STOP_WORDS]
    
    # If the user only typed stop words (e.g. "hi"), keep the original so it doesn't return empty
    if not filtered_words:
        return text
        
    return " ".join(filtered_words)