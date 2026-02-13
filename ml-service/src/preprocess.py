import re
import math
from urllib.parse import urlparse
import numpy as np

class URLExtractor:
    def calculate_entropy(self, text):
        if not text: return 0
        prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
        return - sum([p * math.log(p) / math.log(2.0) for p in prob])

    def extract_features(self, url):
        # 0. Basic parsing
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "http://" + url
            parsed = urlparse(url)
            
        hostname = parsed.netloc
        path = parsed.path
        query = parsed.query
        
        f = []
        
        # --- URL LEVEL FEATURES (1-15) ---
        f.append(len(url)) # url_length
        f.append(url.count('.')) # number_of_dots_in_url
        f.append(1 if re.search(r'(\d)\1{2,}', url) else 0) # having_repeated_digits_in_url
        f.append(len(re.findall(r'\d', url))) # number_of_digits_in_url
        f.append(len(re.findall(r'[^a-zA-Z0-9]', url))) # number_of_special_char_in_url
        f.append(url.count('-')) # number_of_hyphens_in_url
        f.append(url.count('_')) # number_of_underline_in_url
        f.append(url.count('/')) # number_of_slash_in_url
        f.append(url.count('?')) # number_of_questionmark_in_url
        f.append(url.count('=')) # number_of_equal_in_url
        f.append(url.count('@')) # number_of_at_in_url
        f.append(url.count('$')) # number_of_dollar_in_url
        f.append(url.count('!')) # number_of_exclamation_in_url
        f.append(url.count('#')) # number_of_hashtag_in_url
        f.append(url.count('%')) # number_of_percent_in_url
        
        # --- DOMAIN LEVEL FEATURES (16-23) ---
        f.append(len(hostname)) # domain_length
        f.append(hostname.count('.')) # number_of_dots_in_domain
        f.append(hostname.count('-')) # number_of_hyphens_in_domain
        f.append(1 if re.search(r'[^a-zA-Z0-9.]', hostname) else 0) # having_special_characters_in_domain
        f.append(len(re.findall(r'[^a-zA-Z0-9.]', hostname))) # number_of_special_characters_in_domain
        f.append(1 if re.search(r'\d', hostname) else 0) # having_digits_in_domain
        f.append(len(re.findall(r'\d', hostname))) # number_of_digits_in_domain
        f.append(1 if re.search(r'(\d)\1{2,}', hostname) else 0) # having_repeated_digits_in_domain
        
        # --- SUBDOMAIN LEVEL FEATURES (24-34) ---
        subdomains = hostname.split('.')[:-2] # Logic: everything before the SLD
        f.append(len(subdomains)) # number_of_subdomains
        f.append(1 if any('.' in s for s in subdomains) else 0) # having_dot_in_subdomain
        f.append(1 if any('-' in s for s in subdomains) else 0) # having_hyphen_in_subdomain
        f.append(np.mean([len(s) for s in subdomains]) if subdomains else 0) # average_subdomain_length
        f.append(np.mean([s.count('.') for s in subdomains]) if subdomains else 0) # average_number_of_dots_in_subdomain
        f.append(np.mean([s.count('-') for s in subdomains]) if subdomains else 0) # average_number_of_hyphens_in_subdomain
        f.append(1 if any(re.search(r'[^a-zA-Z0-9]', s) for s in subdomains) else 0) # having_special_characters_in_subdomain
        f.append(sum(len(re.findall(r'[^a-zA-Z0-9]', s)) for s in subdomains)) # number_of_special_characters_in_subdomain
        f.append(1 if any(re.search(r'\d', s) for s in subdomains) else 0) # having_digits_in_subdomain
        f.append(sum(len(re.findall(r'\d', s)) for s in subdomains)) # number_of_digits_in_subdomain
        f.append(1 if any(re.search(r'(\d)\1{2,}', s) for s in subdomains) else 0) # having_repeated_digits_in_subdomain
        
        # --- PATH & EXTRA FEATURES (35-41) ---
        f.append(1 if path and path != "/" else 0) # having_path
        f.append(len(path) if path != "/" else 0) # path_length
        f.append(1 if query else 0) # having_query
        f.append(1 if parsed.fragment else 0) # having_fragment
        f.append(1 if '#' in url else 0) # having_anchor
        f.append(self.calculate_entropy(url)) # entropy_of_url
        f.append(self.calculate_entropy(hostname)) # entropy_of_domain
        
        return np.array(f).reshape(1, -1)