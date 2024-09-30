import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

text = ""

def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
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
st.subheader("Elige la fuente de la imágen, esta puede venir de la cámara o cargando un archivo")

cam_ = st.checkbox("Usar Cámara")

if cam_:
    img_file_buffer = st.camera_input("Toma una Foto")
else:
    img_file_buffer = None

bg_image = st.file_uploader("Cargar Imagen:", type=["png", "jpg"])
if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='Imagen cargada.', use_column_width=True)

    # Guardar la imagen en el sistema de archivos
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())

    st.success(f"Imagen guardada como {uploaded_file.name}")
    img_cv = cv2.imread(f'{uploaded_file.name}')
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

if img_file_buffer is not None:
    # To read image file buffer with OpenCV:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

# Sidebar for displaying recognized text and translation parameters
with st.sidebar:
    st.subheader("Texto Reconocido")
    if text.strip():
        st.write(text)
        st.subheader("Parámetros de Traducción")

        try:
            os.mkdir("temp")
        except:
            pass

        translator = Translator()

        # Language selection
        in_lang = st.selectbox(
            "Seleccione el lenguaje de entrada",
            ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Francés", "Alemán", "Portugués"),
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
            "Portugués": "pt"
        }[out_lang]

        english_accent = st.selectbox(
            "Seleccione el acento",
            (
                "Default",
                "India",
                "Reino Unido",
                "Estados Unidos",
                "Canadá",
                "Australia",
                "Irlanda",
                "Sudáfrica",
            ),
        )

        tld = {
            "Default": "com",
            "India": "co.in",
            "Reino Unido": "co.uk",
            "Estados Unidos": "com",
            "Canadá": "ca",
            "Australia": "com.au",
            "Irlanda": "ie",
            "Sudáfrica": "co.za"
        }[english_accent]

        display_output_text = st.checkbox("Mostrar texto")

        if st.button("Generar Audio"):
            if text.strip():
                gif_placeholder = st.empty()  # Placeholder for GIF
                with gif_placeholder.container():
                    st.image("dog.gif")  # Reemplaza con la ruta a tu GIF

                with st.spinner("Generando audio..."):
                    result, output_text = text_to_speech(input_language, output_language, text, tld)
                    audio_file = open(f"temp/{result}.mp3", "rb")
                    audio_bytes = audio_file.read()
                    st.markdown(f"## Tu audio:")
                    st.audio(audio_bytes, format="audio/mp3", start_time=0)

                    if display_output_text:
                        st.markdown(f"## Texto de salida:")
                        st.write(f" {output_text}")

                gif_placeholder.empty()  # Remove the GIF after audio generation
            else:
                st.error("No se reconoció ningún texto. Repita el proceso.")
    else:
        st.warning("No se reconoció ningún texto. Repita el proceso.")
