import re
from typing import List

class ScientificTextPreprocessor:
    @staticmethod
    def clean_text(text: str) -> str:
        if not text or not isinstance(text, str):
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('“', '"').replace('”', '"').replace('’', "'").replace('—', '-')
        return text.strip()

    @staticmethod
    def tokenize_words(text: str) -> List[str]:
        cleaned = ScientificTextPreprocessor.clean_text(text).lower()
        cleaned = re.sub(r'[^\w\s\-]', '', cleaned)
        return [w for w in cleaned.split() if len(w) > 2]
