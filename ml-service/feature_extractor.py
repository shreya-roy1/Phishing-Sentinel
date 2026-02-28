import pandas as pd
import numpy as np
import re
import os
import math
from collections import Counter
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import Path

# ==============================
# CONFIGURE YOUR LOCAL PATHS HERE
# ==============================

BASE_DIR = Path(__file__).resolve().parent   # Current folder
HTML_DIR = BASE_DIR / "dataset"
CSV_PATH = BASE_DIR / "index.csv"
OUTPUT_PATH = BASE_DIR / "extracted_features_v2.csv"

# ==============================
# FEATURE FUNCTIONS
# ==============================

def calculate_entropy(text):
    if not text:
        return 0
    entropy = 0
    counter = Counter(text)
    length = len(text)
    for count in counter.values():
        p_x = count / length
        entropy -= p_x * math.log2(p_x)
    return entropy


def extract_url_features(url):
    parsed = urlparse(url)
    features = {}

    features['url_length'] = len(url)
    features['has_ip'] = int(bool(re.search(r'\d+\.\d+\.\d+\.\d+', url)))
    features['has_at_symbol'] = int('@' in url)
    features['num_hyphens'] = url.count('-')

    subdomains = parsed.netloc.split('.')
    features['num_subdomains'] = max(len(subdomains) - 2, 0)

    # Advanced lexical
    features['url_entropy'] = calculate_entropy(url)
    features['num_digits'] = sum(c.isdigit() for c in url)
    features['num_parameters'] = len(parsed.query.split('&')) if parsed.query else 0

    sensitive_words = ['login', 'secure', 'account', 'update',
                       'bank', 'verify', 'webscr', 'signin']

    features['has_sensitive_words'] = int(
        any(word in url.lower() for word in sensitive_words)
    )

    return features


def extract_dom_features(html_path, base_url):

    features = {
        'has_password_field': 0,
        'has_hidden_iframe': 0,
        'suspicious_form_action': 0,
        'script_to_content_ratio': 0.0,
        'external_link_ratio': 0.0,
        'empty_links_ratio': 0.0,
        'num_input_fields': 0
    }

    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')

        parsed_base = urlparse(base_url).netloc

        # Input fields
        inputs = soup.find_all('input')
        features['num_input_fields'] = len(inputs)

        if soup.find('input', type='password'):
            features['has_password_field'] = 1

        # Suspicious form action
        for form in soup.find_all('form'):
            action = form.get('action', '').lower()
            if action.startswith('http') and parsed_base not in action:
                features['suspicious_form_action'] = 1
                break

        # Hidden iframe
        for iframe in soup.find_all('iframe'):
            style = iframe.get('style', '').lower()
            if 'visibility:hidden' in style or 'display:none' in style:
                features['has_hidden_iframe'] = 1
                break

        # Script to content ratio
        text_length = len(soup.get_text())
        script_length = sum(
            len(script.string)
            for script in soup.find_all('script')
            if script.string
        )

        if text_length > 0:
            features['script_to_content_ratio'] = script_length / text_length

        # Link analysis
        a_tags = soup.find_all('a', href=True)
        total_links = len(a_tags)

        external_links = 0
        empty_links = 0

        for a in a_tags:
            href = a['href'].lower()
            if href.startswith('http') and parsed_base not in href:
                external_links += 1
            elif href == '#' or href.startswith('javascript:'):
                empty_links += 1

        if total_links > 0:
            features['external_link_ratio'] = external_links / total_links
            features['empty_links_ratio'] = empty_links / total_links

    except Exception:
        pass

    return features


# ==============================
# DATASET BUILDER
# ==============================

def build_feature_dataset(csv_path, base_html_dir, output_path):

    print("Loading index.csv...")
    df = pd.read_csv(csv_path, on_bad_lines='skip')
    df.columns = df.columns.str.replace('`', '')

    print("Mapping HTML files...")
    file_map = {
        file.name: file
        for file in Path(base_html_dir).rglob("*.html")
    }

    print(f"Found {len(file_map)} HTML files.")

    all_features = []

    for index, row in df.iterrows():

        url = str(row['url'])
        html_file = str(row['website'])
        label = row['result']

        html_path = file_map.get(html_file)

        url_feats = extract_url_features(url)

        if html_path:
            dom_feats = extract_dom_features(html_path, url)
        else:
            dom_feats = {
                'has_password_field': 0,
                'has_hidden_iframe': 0,
                'suspicious_form_action': 0,
                'script_to_content_ratio': 0.0,
                'external_link_ratio': 0.0,
                'empty_links_ratio': 0.0,
                'num_input_fields': 0
            }

        combined = {**url_feats, **dom_feats, 'label': label}
        all_features.append(combined)

        if index % 5000 == 0 and index > 0:
            print(f"Processed {index} records...")

    feature_df = pd.DataFrame(all_features)
    feature_df.fillna(0, inplace=True)

    feature_df.to_csv(output_path, index=False)
    print(f"Feature dataset saved to: {output_path}")


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    build_feature_dataset(CSV_PATH, HTML_DIR, OUTPUT_PATH)