import os
import time
import glob
import pytesseract
from PIL import Image
import streamlit as st
from gtts import gTTS
from googletrans import Translator

# Inicializar texto
text = " "

def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    my_file_name = text[0:20] if text else "audio"
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

remove_files(7)

st.title("Reconocimiento Óptico de Caracteres")
st.subheader("Elige la fuente de la imagen, esta puede venir de la cámara o cargando un archivo")

cam_ = st.checkbox("Usar Cámara")

if cam_:
    img_file_buffer = st.camera_input("Toma una Foto")
else:
    img_file_buffer = None

bg_image = st.file_uploader("Cargar Imagen:", type=["png", "jpg"])
if bg_image is not None:
    st.image(bg_image, caption='Imagen cargada.', use_column_width=True)
    with open(bg_image.name, 'wb') as f:
        f.write(bg_image.read())

    img_pil = Image.open(bg_image)
    text = pytesseract.image_to_string(img_pil)
else:
    text = ""

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    img_pil = Image.open(bytes_data)
    text = pytesseract.image_to_string(img_pil)

# Mostrar el texto reconocido
if text.strip():
    st.sidebar.write(text)
else:
    st.sidebar.warning("No se reconoció ningún texto. Repita el proceso.")

with st.sidebar:
    st.subheader("Parámetros de traducción")
    try:
        os.mkdir("temp")
    except:
        pass
    
    translator = Translator()
    
    in_lang = st.selectbox(
        "Seleccione el lenguaje de entrada",
        ("Inglés", "Español", "Bengali", "Koreano", "Mandarín", "Japonés", "Francés", "Alemán", "Portugués")
    )
    
    input_language = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Koreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
        "Francés": "fr",
        "Alemán": "de",
        "Portugués": "pt"
    }.get(in_lang)

    out_lang = st.selectbox(
        "Selecciona tu idioma de salida",
        ("Inglés", "Español", "Bengali", "Koreano", "Mandarín", "Japonés", "Francés", "Alemán", "Portugués")
    )
    
    output_language = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Koreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
        "Francés": "fr",
        "Alemán": "de",
        "Portugués": "pt"
    }.get(out_lang)

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
        )
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
    }.get(english_accent)

    display_output_text = st.checkbox("Mostrar texto")

    if text.strip() and st.button("convertir"):
        # Mostrar el GIF de carga
        gif_placeholder = st.sidebar.empty()
        gif_placeholder.image("path/to/loading.gif", caption="Generando audio...", use_column_width=True)

        result, output_text = text_to_speech(input_language, output_language, text, tld)
        
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown(f"## Texto de salida:")
            st.write(f"{output_text}")

        # Limpiar el GIF una vez que se genera el audio
        gif_placeholder.empty()

