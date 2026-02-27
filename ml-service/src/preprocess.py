import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def extract_url_features(url):
    """Extracts lexical features from the live URL."""
    parsed = urlparse(url)
    features = {}
    
    features['url_length'] = len(url)
    features['has_ip'] = 1 if re.search(r'\d+\.\d+\.\d+\.\d+', url) else 0
    features['has_at_symbol'] = 1 if '@' in url else 0
    features['num_hyphens'] = url.count('-')
    features['num_subdomains'] = len(parsed.netloc.split('.')) - 2
    
    return features

def extract_dom_features(html_path, base_url):
    """Extracts intent-based features from the live HTML content."""
    features = {
        'has_password_field': 0,
        'has_hidden_iframe': 0,
        'suspicious_form_action': 0,
        'script_to_content_ratio': 0.0
    }
    
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            
            if soup.find('input', type='password'):
                features['has_password_field'] = 1
                
            for iframe in soup.find_all('iframe'):
                if iframe.get('style') and ('visibility:hidden' in iframe.get('style').lower() or 'display:none' in iframe.get('style').lower()):
                    features['has_hidden_iframe'] = 1
                    break
                    
            parsed_base = urlparse(base_url).netloc
            for form in soup.find_all('form'):
                action = form.get('action', '').lower()
                if action.startswith('http') and parsed_base not in action:
                    features['suspicious_form_action'] = 1
                    break
            
            text_length = len(soup.get_text())
            script_length = sum([len(script.string) for script in soup.find_all('script') if script.string])
            if text_length > 0:
                features['script_to_content_ratio'] = script_length / text_length
                
    except Exception as e:
        pass
        
    return features