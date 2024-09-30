import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator
import streamlit as st

# Configuración inicial
text = ""
translator = Translator()

def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    
    try:
        my_file_name = text[:20]
    except:
        my_file_name = "audio"
        
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)

remove_files(7)

st.title("Reconocimiento Óptico de Caracteres")
st.subheader("Elige la fuente de la imagen, esta puede venir de la cámara o cargando un archivo")

cam_ = st.checkbox("Usar Cámara")
img_file_buffer = st.camera_input("Toma una Foto") if cam_ else None
bg_image = st.file_uploader("Cargar Imagen:", type=["png", "jpg"])

if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='Imagen cargada.', use_column_width=True)
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())
    
    st.success(f"Imagen guardada como {uploaded_file.name}")
    img_cv = cv2.imread(f'{uploaded_file.name}')
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if st.sidebar.radio("Filtro para imagen con cámara", ('Sí', 'No')) == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)
        
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

# Mostrar texto reconocido en la barra lateral
if text.strip():
    st.sidebar.write(f"Texto reconocido: {text}")
    
    # Parámetros de traducción
    in_lang = st.sidebar.selectbox(
        "Seleccione el lenguaje de entrada",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Francés", "Alemán", "Portugués"),
        index=0  # Ajusta el índice si es necesario
    )
    input_language = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
        "Francés": "fr",
        "Alemán": "de",
        "Portugués": "pt"
    }[in_lang]
    
    out_lang = st.sidebar.selectbox(
        "Selecciona tu idioma de salida",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Francés", "Alemán", "Portugués")
    )
    output_language = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
        "Francés": "fr",
        "Alemán": "de",
        "Portugués": "pt"
    }[out_lang]
    
    english_accent = st.sidebar.selectbox(
        "Seleccione el acento",
        ("Default", "India", "United Kingdom", "United States", "Canada", "Australia", "Ireland", "South Africa")
    )
    
    tld = {
        "Default": "com",
        "India": "co.in",
        "United Kingdom": "co.uk",
        "United States": "com",
        "Canada": "ca",
        "Australia": "com.au",
        "Ireland": "ie",
        "South Africa": "co.za"
    }[english_accent]
    
    if st.sidebar.button("Convertir"):
        with st.sidebar.spinner("Generando audio..."):
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            audio_file = open(f"temp/{result}.mp3", "rb")
            audio_bytes = audio_file.read()
            st.sidebar.markdown("## Tu audio:")
            st.sidebar.audio(audio_bytes, format="audio/mp3", start_time=0)
            st.sidebar.markdown("## Texto de salida:")
            st.sidebar.write(output_text)
else:
    st.sidebar.warning("No se reconoció ningún texto. Repita el proceso.")
