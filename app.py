import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from gtts import gTTS
from googletrans import Translator

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
    if mp3_files:
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
img_file_buffer = None

with st.sidebar:
    st.subheader("Procesamiento para Cámara")
    filtro = st.radio("Filtro para imagen con cámara", ('Sí', 'No'))

if cam_:
    img_file_buffer = st.camera_input("Toma una Foto")

bg_image = st.file_uploader("Cargar Imagen:", type=["png", "jpg"])
if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='Imagen cargada.', use_column_width=True)

    # Guardar la imagen en el sistema de archivos
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())

    st.success(f"Imagen guardada como {uploaded_file.name}")
    img_cv = cv2.imread(uploaded_file.name)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    
    if text.strip():  # Verifica que se haya reconocido algún texto
        detected_lang = translator.detect(text).lang
        input_language = detected_lang  # Cambia el idioma de entrada automáticamente
        st.sidebar.write(f"**El texto reconocido fue:** {text}")
        st.sidebar.write(f"**Idioma detectado:** {input_language}")
    else:
        st.warning("No se reconoció texto en la imagen.")

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # Aplicar filtro si está habilitado
    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)  # Invertir colores como ejemplo de filtro

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

    if text.strip():  # Verifica que se haya reconocido algún texto
        detected_lang = translator.detect(text).lang
        input_language = detected_lang  # Cambia el idioma de entrada automáticamente
        st.sidebar.write(f"**El texto reconocido fue:** {text}")
        st.sidebar.write(f"**Idioma detectado:** {input_language}")
    else:
        st.warning("No se reconoció texto en la imagen.")

# Sidebar para parámetros de traducción
with st.sidebar:
    if text.strip():  # Mostrar parámetros solo si se reconoció texto
        st.subheader("Parámetros de traducción")
        
        try:
            os.mkdir("temp")
        except FileExistsError:
            pass
        
        # Selección de idioma de entrada
        in_lang = st.selectbox(
            "Seleccione el lenguaje de entrada",
            ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Francés", "Alemán", "Portugués"),
            index=["Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Francés", "Alemán", "Portugués"].index(input_language) if input_language else 0
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
            "Portugués": "pt",
        }.get(in_lang, "en")

        out_lang = st.selectbox(
            "Selecciona tu idioma de salida",
            ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Francés", "Alemán", "Portugués"),
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
            "Portugués": "pt",
        }.get(out_lang, "en")

        english_accent = st.selectbox(
            "Seleccione el acento",
            (
                "Default",
                "India",
                "United Kingdom",
                "United States",
                "Canada",
                "Australia",
                "Ireland",
                "South Africa",
            ),
        )
        
        tld = {
            "Default": "com",
            "India": "co.in",
            "United Kingdom": "co.uk",
            "United States": "com",
            "Canada": "ca",
            "Australia": "com.au",
            "Ireland": "ie",
            "South Africa": "co.za",
        }.get(english_accent, "com")

        # GIF de carga
        gif_placeholder = st.empty()
        loading_gif = gif_placeholder.image("loading.gif", use_column_width=True, caption="Generando audio...", format="auto")

        if st.button("Convertir"):
            with st.spinner("Generando audio..."):
                result, output_text = text_to_speech(input_language, output_language, text, tld)
                audio_file = open(f"temp/{result}.mp3", "rb")
                audio_bytes = audio_file.read()
                st.markdown(f"## Tu audio:")
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
                
                # Eliminar GIF de carga
                gif_placeholder.empty()

            # Mostrar el texto generado
            st.markdown(f"## Texto de salida:")
            st.write(f"{output_text}")
    else:
        st.warning("No hay texto para convertir.")
