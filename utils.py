from typing import Dict, List
import re

def validate_inputs(data: Dict) -> List[str]:
    """Valida gli input e restituisce una lista di errori"""
    errors = []
    
    # Campi obbligatori
    required_fields = {
        'company_name': 'Nome azienda',
        'company_description': 'Descrizione azienda', 
        'email_objective': 'Obiettivo email',
        'content_brief': 'Brief contenuto'
    }
    
    for field, name in required_fields.items():
        if not data.get(field, '').strip():
            errors.append(f"{name} è obbligatorio")
    
    # Validazione URL
    if data.get('website_url') and not is_valid_url(data['website_url']):
        errors.append("URL sito web non valido")
    
    # Validazione link prodotti
    for i, product in enumerate(data.get('products', []), 1):
        if product and product.get('link') and not is_valid_url(product['link']):
            errors.append(f"Link prodotto {i} non valido")
    
    return errors

def is_valid_url(url: str) -> bool:
    """Verifica se un URL è valido"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def format_output(result: Dict) -> str:
    """Formatta l'output per il download"""
    output = "NEWSLETTER GENERATA\n"
    output += "=" * 50 + "\n\n"
    
    # Oggetti email
    output += "OGGETTI EMAIL (max 40 caratteri)\n"
    output += "-" * 30 + "\n"
    for i, subject in enumerate(result.get('email_subjects', []), 1):
        output += f"{i}. {subject} ({len(subject)} caratteri)\n"
    output += "\n"
    
    # Anteprime email
    output += "ANTEPRIME EMAIL (max 100 caratteri)\n"
    output += "-" * 30 + "\n"
    for i, preview in enumerate(result.get('email_previews', []), 1):
        output += f"{i}. {preview} ({len(preview)} caratteri)\n"
    output += "\n"
    
    # Contenuto newsletter
    output += "CONTENUTO NEWSLETTER\n"
    output += "-" * 30 + "\n"
    output += result.get('newsletter_content', '')
    output += "\n\n"
    
    output += "=" * 50 + "\n"
    output += "Generato con Newsletter AI Generator\n"
    
    return output

def clean_text(text: str) -> str:
    """Pulisce il testo da caratteri non desiderati"""
    # Rimuove caratteri speciali eccessivi
    text = re.sub(r'\s+', ' ', text)  # Spazi multipli
    text = re.sub(r'\n+', '\n', text)  # Newline multipli
    return text.strip()

def count_characters(text: str) -> int:
    """Conta i caratteri di un testo"""
    return len(text.strip())

def truncate_text(text: str, max_length: int) -> str:
    """Tronca il testo alla lunghezza massima"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def extract_products_info(products: List[Dict]) -> str:
    """Estrae informazioni sui prodotti per il prompt"""
    if not products:
        return ""
    
    info = "PRODOTTI:\n"
    for i, product in enumerate(products, 1):
        if product and product.get('name'):
            info += f"{i}. {product['name']}"
            if product.get('link'):
                info += f" - {product['link']}"
            info += "\n"
    
    return info

def format_market_segments(segments: List[str]) -> str:
    """Formatta i segmenti di mercato"""
    valid_segments = [s.strip() for s in segments if s and s.strip()]
    if not valid_segments:
        return "Non specificato"
    return ", ".join(valid_segments)

def parse_comma_separated(text: str) -> List[str]:
    """Parsa testo separato da virgole"""
    if not text:
        return []
    return [item.strip() for item in text.split(',') if item.strip()]

def validate_character_limits(subjects: List[str], previews: List[str]) -> Dict:
    """Valida i limiti di caratteri per oggetti e anteprime"""
    issues = {
        'subjects_too_long': [],
        'previews_too_long': []
    }
    
    for i, subject in enumerate(subjects):
        if len(subject) > 40:
            issues['subjects_too_long'].append(f"Oggetto {i+1}: {len(subject)} caratteri")
    
    for i, preview in enumerate(previews):
        if len(preview) > 100:
            issues['previews_too_long'].append(f"Anteprima {i+1}: {len(preview)} caratteri")
    
    return issues

def generate_fallback_content(data: Dict) -> Dict:
    """Genera contenuto di fallback in caso di errore"""
    company = data.get('company_name', 'la nostra azienda')
    
    return {
        'email_subjects': [
            f"News da {company}"[:40],
            f"Novità {company}"[:40],
            f"Offerte {company}"[:40]
        ],
        'email_previews': [
            f"Scopri le ultime novità di {company}"[:100],
            f"Non perdere le nostre offerte esclusive"[:100],
            f"Rimani sempre aggiornato con noi"[:100]
        ],
        'newsletter_content': f"""
# Newsletter {company}

Benvenuto nella nostra newsletter!

Siamo felici di tenerti aggiornato sulle nostre ultime novità e offerte esclusive.

**[CALL TO ACTION PRINCIPALE]**

## Le nostre proposte

Scopri tutti i nostri prodotti e servizi sul nostro sito web.

**[SCOPRI DI PIÙ]**

---

Grazie per la tua fiducia in {company}.

Il team di {company}

**[VISITA IL SITO]**
        """
    }

def markdown_to_mailchimp_format(content: str) -> str:
    """Converte markdown in formato più compatibile con builder email"""
    
    # Sostituisce headers markdown
    content = re.sub(r'^# (.*)', r'TITOLO: \1', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*)', r'SOTTOTITOLO: \1', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.*)', r'SEZIONE: \1', content, flags=re.MULTILINE)
    
    # Sostituisce bold
    content = re.sub(r'\*\*(.*?)\*\*', r'GRASSETTO: \1', content)
    
    # Sostituisce link
    content = re.sub(r'\[(.*?)\]\((.*?)\)', r'LINK: \1 (URL: \2)', content)
    
    # Identifica call to action
    content = re.sub(r'\[([^\]]+)\](?!\()', r'PULSANTE CTA: \1', content)
    
    return content
