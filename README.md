#README.md
# Resume Parsing – Email Extractor & Cleaner

This project provides a Python utility to **extract, clean, and auto-correct email addresses** from raw text (like resumes, scraped data, or user input).  
It automatically normalizes common issues such as missing `@`, wrong domains, extra spaces, or unusual formats.

---

##  Installation

``bash
git clone https://github.com/ISudhan/resume-parsing.git

cd resume-parsing

pip install rapidfuzz

uvicorn api:app --reload


##  Features
- Extracts email-like patterns from text.
- Cleans unwanted characters.
- Normalizes `at`, `dot`, `(at)`, `(dot)` into valid email format.
- Fixes multiple `@` symbols.
- Validates and auto-corrects domains using fuzzy matching (`rapidfuzz`).
- Supports common domains (Gmail, Yahoo, Outlook, etc.).

---

##  Requirements
- Python 3.7+
- Install dependencies:

``bash

##  Why RapidFuzz?

-  **Faster** – Written in C++ and optimized, typically 5–10x faster than `fuzzywuzzy`.
-  **No External Dependencies** – Unlike `fuzzywuzzy` which requires `python-Levenshtein` for speed, RapidFuzz works out of the box.
-  **More Features** – Supports multiple similarity metrics (Levenshtein, partial ratio, token sort ratio, Jaro-Winkler, etc.).
-  **Efficient Memory Usage** – Handles large datasets like resumes, scraped data, or bulk text more efficiently.
-  **Actively Maintained** – Modern library with ongoing improvements and community support.

---

### Example: Fuzzy Domain Correction
``python
from rapidfuzz import process

valid_domains = ["gmail.com", "yahoo.com", "outlook.com"]

domain = "gnail.com"  # typo err
best_match = process.extractOne(domain, valid_domains)

print(best_match)  # ('gmail.com', 90.0, 0)





