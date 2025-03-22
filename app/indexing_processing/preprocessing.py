import unicodedata

def preprocessing(text):
    # Normalize only invisible characters that don't affect meaning
    text = unicodedata.normalize('NFC', text)  # Canonical composition
    
    # Fix encoding issues without changing visible characters
    text = text.replace('\u0000', '')  # Remove null bytes
    
    # Standardize line endings without changing content
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Optionally: Remove truly redundant whitespace (multiple spaces → single space)
    # text = re.sub(r' {2,}', ' ', text)  # Be careful with this
    
    return text