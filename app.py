import os
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
import os
import streamlit as st
import pytesseract
from PIL import Image
from googletrans import Translator
from gtts import gTTS
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai

# ✅ Fix: Ensure Firebase initializes only once
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")  # Use a local JSON file
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ✅ Set environment variables to fix CORS & XSRF issues
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"

# ✅ Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Use an environment variable for security

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

# ✅ Streamlit UI
st.title("OCR and Translation App")
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

languages = {"Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Urdu": "ur"}
selected_language = st.selectbox("Select translation language", list(languages.keys()))

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    try:
        # ✅ Fix: Explicitly set Tesseract path if needed
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
        
        extracted_text = pytesseract.image_to_string(image)

        # ✅ Translation
        translator = Translator()
        translated_text = translator.translate(extracted_text, dest=languages[selected_language]).text
        st.write("### Translated Text:", translated_text)

        # ✅ Text-to-Speech
        tts = gTTS(translated_text, lang=languages[selected_language])
        audio_path = "translated_audio.mp3"
        tts.save(audio_path)
        st.audio(audio_path, format="audio/mp3")

        # ✅ Chatbot Mode
        st.write("### Chatbot Mode: Ask questions about the image")
        user_query = st.text_input("Ask a question:")

        if user_query:
            db.collection("user_queries").add({"query": user_query})  # Store query in Firestore

            chat_session = model.start_chat(
                history=[{"role": "user", "parts": [
                    f"Based on the following document text, answer the user's query. Document: {extracted_text}\nQuery: {user_query}"
                ]}]
            )
            response = chat_session.send_message(user_query)
            st.write("#### Answer:", response.text.strip())

    except pytesseract.pytesseract.TesseractNotFoundError:
        st.error("Tesseract is not installed. Please check the deployment settings.")


