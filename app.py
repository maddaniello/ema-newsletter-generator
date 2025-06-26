import streamlit as st
import openai
from newsletter_generator import NewsletterGenerator
from utils import validate_inputs, format_output
import json

# Configurazione pagina
st.set_page_config(
    page_title="Newsletter AI Generator",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titolo principale
st.title("📧 Newsletter AI Generator")
st.markdown("Genera newsletter ottimizzate con intelligenza artificiale")

# Sidebar per API Key
st.sidebar.header("🔑 Configurazione API")
api_key = st.sidebar.text_input(
    "Inserisci la tua OpenAI API Key",
    type="password",
    help="La tua chiave API OpenAI per generare il contenuto"
)

if api_key:
    openai.api_key = api_key
    st.sidebar.success("✅ API Key configurata")
else:
    st.sidebar.warning("⚠️ Inserisci la tua API Key per continuare")

# Sezione principale solo se API key è presente
if api_key:
    st.header("📋 Inserisci i dati per generare la newsletter")
    
    # Creare due colonne per organizzare meglio il form
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Informazioni Azienda")
        company_name = st.text_input("Nome dell'azienda *", help="Nome della tua azienda")
        website_url = st.text_input("Link al sito web", help="URL del sito web aziendale")
        company_description = st.text_area(
            "Descrizione dell'azienda *", 
            height=100,
            help="Copia e incolla dalla pagina 'Chi siamo'"
        )
        
        st.subheader("📨 Tipo di Email")
        email_type = st.selectbox(
            "Tipologia di email *",
            ["Newsletter", "DEM", "Automation"]
        )
        
        email_objective = st.text_area(
            "Obiettivo della mail *",
            height=80,
            help="Descrivi l'obiettivo principale di questa email"
        )
        
        content_brief = st.text_area(
            "Brief del contenuto *",
            height=100,
            help="Descrivi il contenuto che vuoi includere nella newsletter"
        )
    
    with col2:
        st.subheader("🎯 Target e Mercato")
        target_audience = st.selectbox("Target audience *", ["B2B", "B2C"])
        
        market_segment_1 = st.text_input("Segmento di mercato 1", help="Primo segmento di mercato")
        market_segment_2 = st.text_input("Segmento di mercato 2", help="Secondo segmento di mercato")
        market_segment_3 = st.text_input("Segmento di mercato 3", help="Terzo segmento di mercato")
        
        st.subheader("🎨 Tone of Voice")
        tone_options = ["Professionale", "Minimalista", "Persuasivo", "Informativo", "Ricercato", "Popolare", "Altro"]
        tone_of_voice = st.selectbox("Tone of voice *", tone_options)
        
        if tone_of_voice == "Altro":
            custom_tone = st.text_input("Specifica il tone of voice")
            tone_of_voice = custom_tone if custom_tone else "Professionale"
    
    # Sezione prodotti
    st.subheader("🛍️ Prodotti (opzionale)")
    col3, col4 = st.columns(2)
    
    with col3:
        product_1 = st.text_input("Prodotto 1")
        product_2 = st.text_input("Prodotto 2") 
        product_3 = st.text_input("Prodotto 3")
    
    with col4:
        product_link_1 = st.text_input("Link Prodotto 1")
        product_link_2 = st.text_input("Link Prodotto 2")
        product_link_3 = st.text_input("Link Prodotto 3")
    
    # Altre informazioni
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("💡 Informazioni Aggiuntive")
        usp_benefit = st.text_area(
            "USP / Benefit",
            height=80,
            help="Unique Selling Proposition o benefici principali"
        )
        
        language = st.selectbox(
            "Lingua *",
            ["Italiano", "Inglese", "Francese", "Spagnolo", "Tedesco"]
        )
    
    with col6:
        st.subheader("📝 Personalizzazione Testo")
        forbidden_words = st.text_area(
            "Parole vietate",
            height=60,
            help="Parole da non utilizzare, separate da virgola"
        )
        
        required_words = st.text_area(
            "Parole da usare",
            height=60,
            help="Parole che devono essere incluse, separate da virgola"
        )
        
        discount_codes = st.text_input(
            "Codici sconto disponibili",
            help="Codici sconto da includere, separati da virgola"
        )
    
    # Pulsante per generare
    st.markdown("---")
    
    if st.button("🚀 Genera Newsletter", type="primary", use_container_width=True):
        # Validazione input obbligatori
        required_fields = {
            "Nome azienda": company_name,
            "Descrizione azienda": company_description,
            "Obiettivo email": email_objective,
            "Brief contenuto": content_brief
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value.strip()]
        
        if missing_fields:
            st.error(f"❌ Campi obbligatori mancanti: {', '.join(missing_fields)}")
        else:
            # Preparare i dati per la generazione
            data = {
                "company_name": company_name,
                "website_url": website_url,
                "company_description": company_description,
                "email_type": email_type,
                "email_objective": email_objective,
                "content_brief": content_brief,
                "target_audience": target_audience,
                "market_segments": [market_segment_1, market_segment_2, market_segment_3],
                "tone_of_voice": tone_of_voice,
                "products": [
                    {"name": product_1, "link": product_link_1} if product_1 else None,
                    {"name": product_2, "link": product_link_2} if product_2 else None,
                    {"name": product_3, "link": product_link_3} if product_3 else None
                ],
                "usp_benefit": usp_benefit,
                "language": language,
                "forbidden_words": [w.strip() for w in forbidden_words.split(",") if w.strip()],
                "required_words": [w.strip() for w in required_words.split(",") if w.strip()],
                "discount_codes": [c.strip() for c in discount_codes.split(",") if c.strip()]
            }
            
            # Filtrare prodotti nulli
            data["products"] = [p for p in data["products"] if p is not None]
            
            try:
                with st.spinner("🤖 Sto generando la tua newsletter..."):
                    generator = NewsletterGenerator(api_key)
                    result = generator.generate_newsletter(data)
                
                if result:
                    st.success("✅ Newsletter generata con successo!")
                    
                    # Mostrare i risultati
                    st.header("📄 Risultato Generato")
                    
                    # Oggetti email
                    st.subheader("📧 Oggetti Email (max 40 caratteri)")
                    for i, subject in enumerate(result.get("email_subjects", []), 1):
                        st.write(f"**{i}.** {subject} ({len(subject)} caratteri)")
                    
                    # Anteprime email
                    st.subheader("👀 Anteprime Email (max 100 caratteri)")
                    for i, preview in enumerate(result.get("email_previews", []), 1):
                        st.write(f"**{i}.** {preview} ({len(preview)} caratteri)")
                    
                    # Contenuto newsletter
                    st.subheader("📝 Contenuto Newsletter")
                    st.markdown(result.get("newsletter_content", ""))
                    
                    # Pulsante download
                    newsletter_text = format_output(result)
                    st.download_button(
                        label="📥 Scarica Newsletter",
                        data=newsletter_text,
                        file_name=f"newsletter_{company_name.lower().replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                    
                else:
                    st.error("❌ Errore nella generazione della newsletter. Riprova.")
                    
            except Exception as e:
                st.error(f"❌ Errore: {str(e)}")

else:
    st.info("👈 Inserisci la tua OpenAI API Key nella barra laterale per iniziare")
    
    # Informazioni su come ottenere l'API Key
    with st.expander("ℹ️ Come ottenere una OpenAI API Key"):
        st.markdown("""
        1. Vai su [platform.openai.com](https://platform.openai.com)
        2. Crea un account o effettua il login
        3. Vai nella sezione "API Keys"
        4. Clicca su "Create new secret key"
        5. Copia la chiave e incollala nella barra laterale
        
        **Nota:** Mantieni la tua API Key privata e non condividerla con altri.
        """)

# Footer
st.markdown("---")
st.markdown("🚀 **Newsletter AI Generator** - Powered by OpenAI")
