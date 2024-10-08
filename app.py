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

# Advertencia inicial que se mostrará si no hay texto reconocido
warning_message = st.empty()
loading_placeholder = st.sidebar.empty()  # Marcador de posición para el GIF de carga

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

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # Aplicar filtro si está habilitado
    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)  # Invertir colores como ejemplo de filtro

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

# Solo mostrar los parámetros de traducción si se ha reconocido texto
if text.strip():  # Asegurarse de que el texto no esté vacío
    detected_language = translator.detect(text).lang  # Detectar el idioma del texto
    warning_message.empty()  # Limpiar el mensaje de advertencia
    with st.sidebar:
        st.subheader("Parámetros de traducción")
        
        try:
            os.mkdir("temp")
        except FileExistsError:
            pass

        # Cambiar automáticamente el lenguaje de entrada
        input_language = detected_language

        # Mostrar el idioma detectado
        lang_map = {
            "en": "Inglés",
            "es": "Español",
            "bn": "Bengalí",
            "ko": "Coreano",
            "zh-cn": "Mandarín",
            "ja": "Japonés",
            "fr": "Francés",
            "de": "Alemán",
            "pt": "Portugués",
            "ru": "Ruso"  # Agregar ruso
        }

        st.markdown(f"### El texto reconocido fue:")
        st.write(text)
        st.markdown(f"**Idioma detectado:** {lang_map.get(input_language, 'Desconocido')}")

        # Establecer el idioma de entrada en función del idioma detectado
        in_lang_name = lang_map.get(input_language, "Desconocido")
        
        # Seleccionar el idioma de entrada automáticamente
        in_lang_options = list(lang_map.values())
        in_lang_index = in_lang_options.index(in_lang_name) if in_lang_name in in_lang_options else 0

        # Desplegable para el lenguaje de entrada
        st.selectbox("Seleccione el lenguaje de entrada", in_lang_options, index=in_lang_index)

        out_lang = st.selectbox(
            "Selecciona tu idioma de salida",
            ("Inglés", "Español", "Bengalí", "Coreano", "Mandarín", "Japonés", "Francés", "Alemán", "Portugués", "Ruso"),  # Agregar ruso
        )
        output_language = {
            "Inglés": "en",
            "Español": "es",
            "Bengalí": "bn",
            "Coreano": "ko",
            "Mandarín": "zh-cn",
            "Japonés": "ja",
            "Francés": "fr",
            "Alemán": "de",
            "Portugués": "pt",
            "Ruso": "ru"  # Agregar ruso
        }.get(out_lang, "en")

        english_accent = st.selectbox(
            "Seleccione el acento (solo aplica para inglés; no afecta el audio en otros idiomas)",
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

        if st.button("Convertir"):
            loading_placeholder.image("dog.gif")  # Mostrar el GIF de carga
            
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            audio_file = open(f"temp/{result}.mp3", "rb")
            audio_bytes = audio_file.read()
            st.markdown(f"## Tu audio:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            # Limpiar el GIF de carga después de que se genera el audio
            loading_placeholder.empty()

            # Mostrar automáticamente el texto de salida
            st.markdown(f"## Texto de salida:")
            st.write(f"{output_text}")
else:
    warning_message.warning("No se ha reconocido texto aún.")
