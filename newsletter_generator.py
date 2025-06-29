try:
    from openai import OpenAI
    NEW_OPENAI = True
except ImportError:
    try:
        import openai
        NEW_OPENAI = False
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
        import openai
        NEW_OPENAI = False

import json
from typing import Dict, List, Optional

class NewsletterGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        if NEW_OPENAI:
            self.client = OpenAI(api_key=api_key)
        else:
            openai.api_key = api_key
    
    def generate_newsletter(self, data: Dict) -> Optional[Dict]:
        """Genera la newsletter completa usando OpenAI"""
        try:
            # Costruire il prompt principale
            prompt = self._build_prompt(data)
            
            # Chiamata a OpenAI
            if NEW_OPENAI:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system", 
                            "content": self._get_system_prompt()
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=4000,
                    temperature=0.7
                )
                content = response.choices[0].message.content
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system", 
                            "content": self._get_system_prompt()
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=4000,
                    temperature=0.7
                )
                content = response.choices[0].message.content
            
            # Parsing della risposta
            return self._parse_response(content, data)
            
        except Exception as e:
            print(f"Errore dettagliato nella generazione: {str(e)}")
            print(f"Tipo errore: {type(e)}")
            # Prova con GPT-3.5 se GPT-4 non funziona
            try:
                return self._generate_with_fallback_model(data)
            except Exception as e2:
                print(f"Errore anche con modello fallback: {str(e2)}")
                return self._generate_fallback_content(data)
    
    def _generate_fallback_content(self, data: Dict) -> Dict:
        """Genera contenuto di fallback in caso di errore"""
        company = data.get('company_name', 'la nostra azienda')
        objective = data.get('email_objective', 'informare i clienti')
        
        # Contenuto personalizzato basato sui dati inseriti
        newsletter_content = f"""# Newsletter {company}

{objective}

Siamo entusiasti di condividere con te le nostre ultime novità e aggiornamenti.

**[SCOPRI DI PIÙ]**

## Cosa abbiamo per te

{data.get('content_brief', 'Contenuti esclusivi e offerte speciali pensati per te.')}"""

        # Aggiungi prodotti se presenti
        if data.get('products'):
            newsletter_content += "\n\n## I nostri prodotti\n"
            for product in data['products']:
                if product and product.get('name'):
                    newsletter_content += f"\n### {product['name']}\n"
                    newsletter_content += f"Scopri tutti i dettagli di {product['name']}.\n"
                    if product.get('link'):
                        newsletter_content += f"**[SCOPRI {product['name'].upper()}]**\n"

        # USP/Benefit
        if data.get('usp_benefit'):
            newsletter_content += f"\n\n## Perché scegliere {company}\n\n{data['usp_benefit']}\n"

        # Codici sconto
        if data.get('discount_codes'):
            newsletter_content += f"\n\n## Offerta esclusiva\n\nUsa il codice: **{data['discount_codes'][0]}**\n"

        newsletter_content += f"""

---

Grazie per la tua fiducia in {company}.

**[VISITA IL SITO]**

Il team di {company}
"""
        
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
            'newsletter_content': newsletter_content
        }
    
    def _get_system_prompt(self) -> str:
        """Prompt di sistema per definire il comportamento dell'AI"""
        return """
        Sei un esperto di email marketing e copywriting. Il tuo compito è generare newsletter ottimizzate 
        seguendo esattamente questo formato:

        1. 3 proposte di oggetto email (massimo 40 caratteri ciascuno)
        2. 3 proposte di anteprima email (massimo 100 caratteri ciascuno)
        3. Contenuto newsletter strutturato con:
           - Titolo principale
           - Paragrafo principale 
           - Call to action
           - Sezioni prodotto (se presenti) con descrizioni, prezzi, CTA
           - Chiusura e CTA finale

        Rispondi SEMPRE in formato JSON con questa struttura:
        {
            "email_subjects": ["oggetto1", "oggetto2", "oggetto3"],
            "email_previews": ["anteprima1", "anteprima2", "anteprima3"],
            "newsletter_content": "contenuto completo in markdown"
        }

        Adatta il contenuto al tone of voice richiesto e rispetta tutti i vincoli specificati.
        """
    
    def _build_prompt(self, data: Dict) -> str:
        """Costruisce il prompt personalizzato con i dati dell'utente"""
        
        # Informazioni base
        prompt = f"""
        Genera una newsletter ottimizzata per:

        **AZIENDA:** {data['company_name']}
        **SITO WEB:** {data.get('website_url', 'Non specificato')}
        **DESCRIZIONE:** {data['company_description']}

        **TIPO EMAIL:** {data['email_type']}
        **OBIETTIVO:** {data['email_objective']}
        **BRIEF CONTENUTO:** {data['content_brief']}

        **TARGET:** {data['target_audience']}
        **SEGMENTI MERCATO:** {', '.join([s for s in data['market_segments'] if s])}
        **TONE OF VOICE:** {data['tone_of_voice']}
        **LINGUA:** {data['language']}
        """
        
        # Prodotti
        if data.get('products'):
            prompt += "\n**PRODOTTI DA INCLUDERE:**\n"
            for i, product in enumerate(data['products'], 1):
                prompt += f"{i}. {product['name']}"
                if product.get('link'):
                    prompt += f" - Link: {product['link']}"
                prompt += "\n"
        
        # USP/Benefit
        if data.get('usp_benefit'):
            prompt += f"\n**USP/BENEFIT:** {data['usp_benefit']}"
        
        # Codici sconto
        if data.get('discount_codes'):
            prompt += f"\n**CODICI SCONTO:** {', '.join(data['discount_codes'])}"
        
        # Parole vietate
        if data.get('forbidden_words'):
            prompt += f"\n**PAROLE DA EVITARE:** {', '.join(data['forbidden_words'])}"
        
        # Parole richieste
        if data.get('required_words'):
            prompt += f"\n**PAROLE DA INCLUDERE:** {', '.join(data['required_words'])}"
        
        prompt += """

        Genera:
        1. 3 oggetti email accattivanti (MAX 40 caratteri)
        2. 3 anteprime email persuasive (MAX 100 caratteri)  
        3. Newsletter completa con struttura professionale

        Per la newsletter, includi:
        - Titolo coinvolgente
        - Paragrafo introduttivo che catturi l'attenzione
        - Call to action principale
        - Sezioni prodotto dettagliate (se presenti) con descrizioni, benefici e CTA
        - Chiusura persuasiva con CTA finale
        
        Usa un linguaggio adatto al tone of voice e al target specificato.
        Rispetta RIGOROSAMENTE i limiti di caratteri per oggetti e anteprime.
        """
        
        return prompt
    
    def _parse_response(self, content: str, data: Dict) -> Dict:
        """Parsing della risposta OpenAI"""
        try:
            # Tentativo di parsing JSON diretto
            if content.strip().startswith('{'):
                result = json.loads(content)
                # Verifica che abbia tutti i campi necessari
                if all(key in result for key in ['email_subjects', 'email_previews', 'newsletter_content']):
                    return result
            
            # Se non è JSON valido, prova a estrarre il contenuto manualmente
            lines = content.strip().split('\n')
            
            subjects = []
            previews = []
            newsletter_content = ""
            
            current_section = None
            content_lines = []
            
            for line in lines:
                line = line.strip()
                
                if any(word in line.lower() for word in ["oggett", "subject"]):
                    current_section = "subjects"
                elif any(word in line.lower() for word in ["anteprima", "preview"]):
                    current_section = "previews"
                elif any(word in line.lower() for word in ["contenuto", "newsletter", "content"]):
                    current_section = "content"
                elif line and current_section:
                    if current_section == "subjects" and len(subjects) < 3:
                        # Pulire la linea e prendere solo il testo
                        clean_line = line.replace("1.", "").replace("2.", "").replace("3.", "").replace("-", "").strip()
                        clean_line = clean_line.replace('"', '').replace("'", "")
                        if clean_line and len(clean_line) <= 40:
                            subjects.append(clean_line)
                    elif current_section == "previews" and len(previews) < 3:
                        clean_line = line.replace("1.", "").replace("2.", "").replace("3.", "").replace("-", "").strip()
                        clean_line = clean_line.replace('"', '').replace("'", "")
                        if clean_line and len(clean_line) <= 100:
                            previews.append(clean_line)
                    elif current_section == "content":
                        content_lines.append(line)
            
            # Se non abbiamo abbastanza oggetti/anteprime, generali di default
            company = data.get('company_name', 'Azienda')
            while len(subjects) < 3:
                subjects.append(f"Newsletter {company}"[:40])
            
            while len(previews) < 3:
                previews.append(f"Scopri le novità di {company}"[:100])
            
            newsletter_content = '\n'.join(content_lines) if content_lines else content
            
            return {
                "email_subjects": subjects[:3],
                "email_previews": previews[:3], 
                "newsletter_content": newsletter_content
            }
            
        except Exception as e:
            print(f"Errore nel parsing: {str(e)}")
            # Fallback completo
            return self._generate_fallback_content(data)

    def generate_subjects_only(self, data: Dict) -> List[str]:
        """Genera solo gli oggetti email"""
        try:
            prompt = f"""
            Genera ESATTAMENTE 3 oggetti email accattivanti per:
            Azienda: {data['company_name']}
            Tipo: {data['email_type']}
            Obiettivo: {data['email_objective']}
            Target: {data['target_audience']}
            Tone: {data['tone_of_voice']}
            
            IMPORTANTE: Ogni oggetto deve essere MASSIMO 40 caratteri.
            Rispondi solo con i 3 oggetti, uno per riga, senza numerazione.
            """
            
            if NEW_OPENAI:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.8
                )
                content = response.choices[0].message.content.strip()
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.8
                )
                content = response.choices[0].message.content.strip()
            
            subjects = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Filtra per lunghezza
            valid_subjects = [s for s in subjects if len(s) <= 40]
            
            # Assicurati di avere esattamente 3 oggetti
            while len(valid_subjects) < 3:
                valid_subjects.append(f"News {data['company_name']}"[:40])
            
            return valid_subjects[:3]
            
        except Exception as e:
            print(f"Errore generazione oggetti: {str(e)}")
            return [
                f"News {data['company_name']}"[:40],
                f"Novità {data['company_name']}"[:40], 
                f"Offerte {data['company_name']}"[:40]
            ]
